"""OpenCV YuNet adapter based on Irismoraes/centralizadorFacial."""

import hashlib
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import cv2
import numpy as np
import yaml
from numpy.typing import NDArray

from face_processing_benchmark.core.types import FaceDetectionResult


@dataclass(frozen=True)
class YuNetConfig:
    model_path: Path
    sha256: str
    score_threshold: float
    nms_threshold: float
    top_k: int
    initial_input_size_px: tuple[int, int]
    max_side_px: int

    def __post_init__(self) -> None:
        for value in (self.score_threshold, self.nms_threshold):
            if type(value) not in (float, int) or not 0 <= value <= 1:
                raise ValueError("YuNet thresholds must be numbers in [0, 1]")
        if len(self.initial_input_size_px) != 2 or any(
            type(value) is not int or value < 1
            for value in (*self.initial_input_size_px, self.top_k, self.max_side_px)
        ):
            raise ValueError(
                "YuNet input dimensions, top_k and max_side_px must be positive integers"
            )
        if (
            not isinstance(self.sha256, str)
            or len(self.sha256) != 64
            or any(char not in "0123456789abcdef" for char in self.sha256)
        ):
            raise ValueError("Expected a lowercase SHA-256 checkpoint digest")

    @classmethod
    def from_yaml(cls, path: Path, repository_root: Path) -> "YuNetConfig":
        try:
            with path.open(encoding="utf-8") as stream:
                config = yaml.safe_load(stream)
            if config["schema_version"] != 2 or config["kind"] != "methods":
                raise ValueError("Expected a version 2 methods registry")
            method = config["methods"]["yunet"]
            checkpoint = method["checkpoint"]
            relative = Path(checkpoint["path"])
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("Checkpoint path must be repository-relative")
            params = method["parameters"]
            return cls(
                model_path=repository_root / relative,
                sha256=checkpoint["sha256"],
                score_threshold=params["score_threshold"],
                nms_threshold=params["nms_threshold"],
                top_k=params["top_k"],
                initial_input_size_px=tuple(params["initial_input_size_px"]),
                max_side_px=params["max_side_px"],
            )
        except (KeyError, TypeError, ValueError, yaml.YAMLError) as exc:
            raise ValueError(f"{path}: invalid yunet configuration: {exc}") from exc


class YuNetDetector:
    def __init__(self, config: YuNetConfig) -> None:
        self.config = config
        try:
            digest = hashlib.sha256(config.model_path.read_bytes()).hexdigest()
        except OSError as exc:
            raise ValueError(f"Cannot read YuNet checkpoint: {config.model_path}") from exc
        if digest != config.sha256:
            raise ValueError(f"YuNet checkpoint SHA-256 mismatch: {config.model_path}")
        self._model = cv2.FaceDetectorYN.create(
            str(config.model_path),
            "",
            config.initial_input_size_px,
            score_threshold=config.score_threshold,
            nms_threshold=config.nms_threshold,
            top_k=config.top_k,
        )

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
            bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            height, width = bgr.shape[:2]
            inference_started = perf_counter()
            self._model.setInputSize((width, height))
            _, faces = self._model.detect(bgr)
            inference_ms = (perf_counter() - inference_started) * 1000
        except (ValueError, cv2.error) as exc:
            finished = perf_counter()
            inference_ms = (
                0.0
                if inference_started is None
                else (finished - inference_started) * 1000
            )
            return FaceDetectionResult(
                (), None, inference_ms, (finished - started) * 1000, "error", str(exc)
            )

        # The first four YuNet values are xywh. Select before undoing the
        # reference implementation's uniform downscale to preserve tie order.
        raw_boxes = () if faces is None else tuple(
            (float(x), float(y), float(w), float(h))
            for x, y, w, h in faces[:, :4]
        )
        largest_index = max(
            range(len(raw_boxes)),
            key=lambda i: raw_boxes[i][2] * raw_boxes[i][3],
            default=None,
        )
        boxes = tuple(
            (x / scale, y / scale, w / scale, h / scale) for x, y, w, h in raw_boxes
        )
        largest = boxes[largest_index] if largest_index is not None else None
        return FaceDetectionResult(
            boxes,
            largest,
            inference_ms,
            (perf_counter() - started) * 1000,
            "ok" if boxes else "no_face",
            None if boxes else "no_face_detected",
        )
