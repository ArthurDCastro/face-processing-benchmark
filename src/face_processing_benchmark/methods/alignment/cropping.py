"""Face alignment by the largest source-aspect-ratio crop."""

from dataclasses import dataclass
from math import ceil, floor, gcd, inf, isfinite, nextafter
from pathlib import Path

import numpy as np
import yaml
from numpy.typing import NDArray

from face_processing_benchmark.core.types import FaceBox, ImageAlignmentResult


@dataclass(frozen=True)
class CroppingConfig:
    target_center_fraction_xy: tuple[float, float] = (0.5, 0.5)

    def __post_init__(self) -> None:
        if len(self.target_center_fraction_xy) != 2 or any(
            type(value) not in (int, float) or not 0 < value < 1
            for value in self.target_center_fraction_xy
        ):
            raise ValueError("Expected two target center fractions strictly inside (0, 1)")

    @classmethod
    def from_yaml(cls, path: Path) -> "CroppingConfig":
        """Read the shared target position for E1 centering."""
        try:
            with path.open(encoding="utf-8") as stream:
                config = yaml.safe_load(stream)
            if (
                config["schema_version"] != 2
                or config["kind"] != "experiment"
                or config["experiment_id"] != "e1_centering"
                or config["centering"]["strategy"] != "crop"
            ):
                raise ValueError("Expected a version 2 E1 experiment with crop centering")
            return cls(tuple(config["synthetic_canvas"]["target_center_fraction_xy"]))
        except (KeyError, TypeError, ValueError, yaml.YAMLError) as exc:
            raise ValueError(f"{path}: invalid cropping configuration: {exc}") from exc


@dataclass(frozen=True)
class CroppingResult(ImageAlignmentResult):
    """Crop bounds are (left, top, right, bottom), with exclusive right and bottom."""

    crop_bounds_xyxy: tuple[int, int, int, int]
    retained_area_ratio: float

    @property
    def output_width(self) -> int:
        return self.image.shape[1]

    @property
    def output_height(self) -> int:
        return self.image.shape[0]

    @property
    def retained_area_percent(self) -> float:
        return 100 * self.retained_area_ratio


class CroppingAligner:
    """Crop a uint8 RGB image around a supplied face box."""

    def __init__(self, config: CroppingConfig = CroppingConfig()) -> None:
        self.config = config

    def align(self, image: NDArray[np.uint8], face_box: FaceBox) -> CroppingResult:
        if (
            not isinstance(image, np.ndarray)
            or image.dtype != np.uint8
            or image.ndim != 3
            or image.shape[2] != 3
            or not image.size
        ):
            raise ValueError("Expected a nonempty uint8 RGB image")
        height, width = image.shape[:2]
        x, y, box_width, box_height = face_box
        if not all(isfinite(value) for value in face_box):
            raise ValueError("Face box coordinates must be finite")
        if not (
            box_width > 0
            and box_height > 0
            and 0 <= x < x + box_width <= width
            and 0 <= y < y + box_height <= height
        ):
            raise ValueError("Face box must have positive area and lie inside the image")

        center_x, center_y = x + box_width / 2, y + box_height / 2
        target_x, target_y = self.config.target_center_fraction_xy
        divisor = gcd(width, height)
        unit_width, unit_height = width // divisor, height // divisor

        # Generalize the four edge distances in centralizadorFacial/centralizacao.py
        # to an off-center target. Use integer multiples of the reduced aspect ratio.
        # Allow half a pixel for rounding the ideal origin to the pixel grid.
        max_multiple = min(
            (center_x + 0.5) / (target_x * unit_width),
            (width - center_x + 0.5) / ((1 - target_x) * unit_width),
            (center_y + 0.5) / (target_y * unit_height),
            (height - center_y + 0.5) / ((1 - target_y) * unit_height),
            divisor,
        )
        multiple = floor(nextafter(max_multiple, inf))
        if multiple < 1:
            raise ValueError("No positive crop fits the source aspect ratio at this target")

        crop_width, crop_height = multiple * unit_width, multiple * unit_height
        left = _crop_origin(center_x, target_x, crop_width, width, x, box_width)
        top = _crop_origin(center_y, target_y, crop_height, height, y, box_height)
        right, bottom = left + crop_width, top + crop_height

        return CroppingResult(
            image=image[top:bottom, left:right].copy(),
            matrix=np.array([[1, 0, -left], [0, 1, -top]], dtype=np.float64),
            valid_mask=np.ones((crop_height, crop_width), dtype=bool),
            transformed_face_box=(x - left, y - top, box_width, box_height),
            crop_bounds_xyxy=(left, top, right, bottom),
            retained_area_ratio=(crop_width * crop_height) / (width * height),
        )


def _crop_origin(
    center: float, target: float, crop_size: int, image_size: int,
    box_start: float, box_size: float,
) -> int:
    lower = max(0, ceil(box_start + box_size) - crop_size)
    upper = min(image_size - crop_size, floor(box_start))
    ideal = center - target * crop_size
    origin = min(max(round(ideal), lower), upper)
    if lower > upper or abs(origin - ideal) > 0.5 + 1e-9:
        raise ValueError("The largest crop at this target cannot contain the face box")
    return origin
