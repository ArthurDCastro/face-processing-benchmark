"""Frontal face detection with dlib's bundled HOG + linear SVM detector."""

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import dlib
import numpy as np
import yaml
from numpy.typing import NDArray

from face_processing_benchmark.core.types import FaceDetectionResult


@dataclass(frozen=True)
class HogSvmConfig:
    upsample_count: int

    def __post_init__(self) -> None:
        if type(self.upsample_count) is not int or self.upsample_count < 0:
            raise ValueError("upsample_count must be a nonnegative integer")

    @classmethod
    def from_yaml(cls, path: Path) -> "HogSvmConfig":
        """Read the HOG + SVM entry of the experimental methods registry."""
        try:
            with path.open(encoding="utf-8") as stream:
                config = yaml.safe_load(stream)
            if config["schema_version"] != 2 or config["kind"] != "methods":
                raise ValueError("Expected a version 2 methods registry")
            parameters = config["methods"]["hog_svm"]["parameters"]
            return cls(upsample_count=parameters["upsample_count"])
        except (KeyError, TypeError, ValueError, yaml.YAMLError) as exc:
            raise ValueError(f"{path}: invalid hog_svm configuration: {exc}") from exc


class HogSvmDetector:
    def __init__(self, config: HogSvmConfig) -> None:
        self.config = config
        self._detector = dlib.get_frontal_face_detector()

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
            rgb = np.ascontiguousarray(image)
            inference_started = perf_counter()
            faces = self._detector(rgb, self.config.upsample_count)
            inference_ms = (perf_counter() - inference_started) * 1000
        except (ValueError, RuntimeError) as exc:
            finished = perf_counter()
            inference_ms = (
                0.0 if inference_started is None else (finished - inference_started) * 1000
            )
            return FaceDetectionResult(
                (), None, inference_ms, (finished - started) * 1000, "error", str(exc)
            )

        # dlib maps detections back after its internal upsampling. Its rectangle
        # width and height include the pixels at right() and bottom().
        boxes = tuple(
            (float(r.left()), float(r.top()), float(r.width()), float(r.height()))
            for r in faces
        )
        largest = max(boxes, key=lambda box: box[2] * box[3], default=None)
        return FaceDetectionResult(
            boxes,
            largest,
            inference_ms,
            (perf_counter() - started) * 1000,
            "ok" if boxes else "no_face",
            None if boxes else "no_face_detected",
        )
