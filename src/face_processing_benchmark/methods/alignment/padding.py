"""Fixed-canvas translation with an enlarged, blurred copy as the background."""

from dataclasses import dataclass
from math import isfinite

import cv2
import numpy as np
from numpy.typing import NDArray

from face_processing_benchmark.core.types import FaceBox, ImageAlignmentResult


@dataclass(frozen=True)
class PaddingConfig:
    target_center_fraction_xy: tuple[float, float] = (0.5, 0.5)
    background_scale: float = 1.3
    blur_sigma_fraction: float = 1 / 12

    def __post_init__(self) -> None:
        if len(self.target_center_fraction_xy) != 2 or any(
            not 0 <= value <= 1 for value in self.target_center_fraction_xy
        ):
            raise ValueError("Expected two target center fractions in [0, 1]")
        if not isfinite(self.background_scale) or self.background_scale <= 1:
            raise ValueError("Background scale must be finite and greater than 1")
        if not isfinite(self.blur_sigma_fraction) or self.blur_sigma_fraction <= 0:
            raise ValueError("Blur sigma fraction must be finite and positive")


class PaddingAligner:
    """Translate a supplied face box to the target on a fixed-size RGB canvas."""

    def __init__(self, config: PaddingConfig = PaddingConfig()) -> None:
        self.config = config

    def align(
        self, image: NDArray[np.uint8], face_box: FaceBox
    ) -> ImageAlignmentResult:
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
        if box_width <= 0 or box_height <= 0:
            raise ValueError("Face box dimensions must be positive")
        center_x, center_y = x + box_width / 2, y + box_height / 2
        if not (0 <= center_x < width and 0 <= center_y < height):
            raise ValueError("Face box center must be inside the input image")

        target_x, target_y = self.config.target_center_fraction_xy
        dx, dy = target_x * width - center_x, target_y * height - center_y
        matrix = np.array([[1, 0, dx], [0, 1, dy]], dtype=np.float64)
        size = (width, height)
        shifted = cv2.warpAffine(image, matrix, size, flags=cv2.INTER_LINEAR)
        coverage = cv2.warpAffine(
            np.ones((height, width), dtype=np.float32),
            matrix,
            size,
            flags=cv2.INTER_LINEAR,
        )
        # A boundary pixel that samples beyond the source uses the background.
        valid_mask = coverage == 1
        if not valid_mask.all():
            # Background construction adapted from centralizadorFacial/centralizacao.py.
            scale = self.config.background_scale
            background = cv2.resize(image, (round(width * scale), round(height * scale)))
            top = (background.shape[0] - height) // 2
            left = (background.shape[1] - width) // 2
            background = cv2.GaussianBlur(
                background[top : top + height, left : left + width],
                (0, 0),
                sigmaX=max(size) * self.config.blur_sigma_fraction,
            )
            shifted[~valid_mask] = background[~valid_mask]

        return ImageAlignmentResult(
            image=shifted,
            matrix=matrix,
            valid_mask=valid_mask,
            transformed_face_box=(x + dx, y + dy, box_width, box_height),
        )
