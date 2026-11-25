"""Viola–Jones Haar detector adapted from Irismoraes/centralizadorFacial."""

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import cv2
import numpy as np
import yaml
from numpy.typing import NDArray

from face_processing_benchmark.core.types import FaceDetectionResult


@dataclass(frozen=True)
class ViolaJonesConfig:
    cascade_path: Path
    scale_factor: float
    min_neighbors: int
    min_size_px: tuple[int, int]
    max_side_px: int

    @classmethod
    def from_yaml(cls, path: Path, repository_root: Path) -> "ViolaJonesConfig":
        """Read the Viola-Jones entry of the experimental methods registry."""
        try:
            with path.open(encoding="utf-8") as stream:
                config = yaml.safe_load(stream)
            if config["schema_version"] != 2 or config["kind"] != "methods":
                raise ValueError("Expected a version 2 methods registry")
            method = config["methods"]["viola_jones"]
            checkpoint = method["checkpoint"]
            parameters = method["parameters"]
            custom_path = checkpoint["path"]
            if custom_path is None:
                cascade_path = Path(cv2.data.haarcascades) / checkpoint["bundled_file"]
            else:
                relative = Path(custom_path)
                if relative.is_absolute() or ".." in relative.parts:
                    raise ValueError("Checkpoint path must be repository-relative")
                cascade_path = repository_root / relative
            return cls(
                cascade_path=cascade_path,
                scale_factor=parameters["scale_factor"],
                min_neighbors=parameters["min_neighbors"],
                min_size_px=tuple(parameters["min_size_px"]),
                max_side_px=parameters["max_side_px"],
            )
        except (KeyError, TypeError, ValueError, yaml.YAMLError) as exc:
            raise ValueError(f"{path}: invalid viola_jones configuration: {exc}") from exc

    def __post_init__(self) -> None:
        if type(self.scale_factor) not in (int, float) or not (
            1 < self.scale_factor < float("inf")
        ):
            raise ValueError("scale_factor must be a finite number greater than one")
        if type(self.min_neighbors) is not int or self.min_neighbors < 0:
            raise ValueError("min_neighbors must be a nonnegative integer")
        if len(self.min_size_px) != 2 or any(
            type(side) is not int or side < 1 for side in self.min_size_px
        ):
            raise ValueError("min_size_px must contain two positive integers")
        if type(self.max_side_px) is not int or self.max_side_px < 1:
            raise ValueError("max_side_px must be a positive integer")


class ViolaJonesDetector:
    def __init__(self, config: ViolaJonesConfig) -> None:
        self.config = config
        if not config.cascade_path.is_file():
            raise ValueError(f"Cascade file not found: {config.cascade_path}")
        try:
            self._cascade = cv2.CascadeClassifier(str(config.cascade_path))
        except (cv2.error, SystemError) as exc:
            raise ValueError(f"Cannot load cascade: {config.cascade_path}") from exc
        if self._cascade.empty():
            raise ValueError(f"Cannot load cascade: {config.cascade_path}")

    def detect(self, image: NDArray[np.uint8]) -> FaceDetectionResult:
        started = perf_counter()
        inference_started = None
        try:
            if (
                not isinstance(image, np.ndarray)
                or image.dtype != np.uint8
                or image.ndim != 3
                or image.shape[2] != 3
                or not image.size
            ):
                raise ValueError("Expected a nonempty uint8 RGB image")
            scale = min(1.0, self.config.max_side_px / max(image.shape[:2]))
            if scale < 1.0:
                image = cv2.resize(
                    image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA
                )

            # The reference times grayscale conversion, equalization and cascade
            # inference together, excluding the resize and box selection.
            inference_started = perf_counter()
            gray = cv2.equalizeHist(cv2.cvtColor(image, cv2.COLOR_RGB2GRAY))
            faces = self._cascade.detectMultiScale(
                gray,
                scaleFactor=self.config.scale_factor,
                minNeighbors=self.config.min_neighbors,
                minSize=self.config.min_size_px,
            )
            inference_ms = (perf_counter() - inference_started) * 1000
        except (ValueError, cv2.error) as exc:
            finished = perf_counter()
            return FaceDetectionResult(
                (), None,
                0.0 if inference_started is None else (finished - inference_started) * 1000,
                (finished - started) * 1000, "error", str(exc),
            )

        # Match the upstream scalar coordinate conversion and first-on-tie rule.
        boxes = tuple(
            (float(x) / scale, float(y) / scale, float(w) / scale, float(h) / scale)
            for x, y, w, h in faces
        )
        largest_index = max(
            range(len(boxes)),
            key=lambda index: int(faces[index][2]) * int(faces[index][3]),
            default=None,
        )
        largest = boxes[largest_index] if largest_index is not None else None
        return FaceDetectionResult(
            boxes, largest, inference_ms, (perf_counter() - started) * 1000,
            "ok" if largest else "no_face", None if largest else "no_face_detected",
        )
