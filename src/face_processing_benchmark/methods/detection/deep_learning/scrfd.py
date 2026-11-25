"""SCRFD-500MF inference adapted from InsightFace's official SCRFD example."""

import hashlib
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import cv2
import numpy as np
import onnxruntime as ort
import yaml
from numpy.typing import NDArray

from face_processing_benchmark.core.types import FaceDetectionResult

STRIDES = (8, 16, 32)
ANCHORS_PER_CELL = 2


@dataclass(frozen=True)
class ScrfdConfig:
    model_path: Path
    sha256: str
    version: str
    score_threshold: float
    nms_threshold: float
    internal_resolution_px: tuple[int, int]

    def __post_init__(self) -> None:
        for value in (self.score_threshold, self.nms_threshold):
            if type(value) not in (float, int) or not 0 <= value <= 1:
                raise ValueError("SCRFD thresholds must be numbers in [0, 1]")
        if len(self.internal_resolution_px) != 2 or any(
            type(side) is not int or side <= 0 or side % max(STRIDES)
            for side in self.internal_resolution_px
        ):
            raise ValueError("SCRFD width and height must be positive multiples of 32")
        if (
            not isinstance(self.sha256, str)
            or len(self.sha256) != 64
            or any(char not in "0123456789abcdef" for char in self.sha256)
        ):
            raise ValueError("Expected a lowercase SHA-256 checkpoint digest")

    @classmethod
    def from_yaml(cls, path: Path, repository_root: Path) -> "ScrfdConfig":
        try:
            with path.open(encoding="utf-8") as stream:
                config = yaml.safe_load(stream)
            if config["schema_version"] != 2 or config["kind"] != "methods":
                raise ValueError("Expected a version 2 methods registry")
            method = config["methods"]["scrfd"]
            checkpoint = method["checkpoint"]
            relative = Path(checkpoint["path"])
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("Checkpoint path must be repository-relative")
            params = method["parameters"]
            return cls(
                model_path=repository_root / relative,
                sha256=checkpoint["sha256"],
                version=checkpoint["version"],
                score_threshold=params["score_threshold"],
                nms_threshold=params["nms_threshold"],
                internal_resolution_px=tuple(params["internal_resolution_px"]),
            )
        except (KeyError, TypeError, ValueError, yaml.YAMLError) as exc:
            raise ValueError(f"{path}: invalid scrfd configuration: {exc}") from exc


def _non_maximum_suppression(
    boxes: NDArray[np.float32], scores: NDArray[np.float32], threshold: float
) -> list[int]:
    # The official SCRFD implementation uses inclusive corners for NMS.
    areas = np.prod(boxes[:, 2:] - boxes[:, :2] + 1, axis=1)
    order = scores.argsort()[::-1]
    keep = []
    while order.size:
        index = order[0]
        remaining = order[1:]
        top_left = np.maximum(boxes[index, :2], boxes[remaining, :2])
        bottom_right = np.minimum(boxes[index, 2:], boxes[remaining, 2:])
        intersection = np.prod(np.maximum(bottom_right - top_left + 1, 0), axis=1)
        union = areas[index] + areas[remaining] - intersection
        keep.append(int(index))
        order = remaining[intersection / union <= threshold]
    return keep


class ScrfdDetector:
    def __init__(self, config: ScrfdConfig) -> None:
        self.config = config
        try:
            model = config.model_path.read_bytes()
        except OSError as exc:
            raise ValueError(f"Cannot read SCRFD checkpoint: {config.model_path}") from exc
        if hashlib.sha256(model).hexdigest() != config.sha256:
            raise ValueError(f"SCRFD checkpoint SHA-256 mismatch: {config.model_path}")
        try:
            self._session = ort.InferenceSession(model, providers=["CPUExecutionProvider"])
        except Exception as exc:
            raise ValueError(f"Cannot load SCRFD checkpoint: {exc}") from exc

        inputs = self._session.get_inputs()
        width, height = config.internal_resolution_px
        expected_shape = (1, 3, height, width)
        if len(inputs) != 1 or len(inputs[0].shape) != len(expected_shape) or any(
            isinstance(actual, int) and actual != expected
            for actual, expected in zip(inputs[0].shape, expected_shape)
        ):
            raise ValueError(
                "SCRFD checkpoint input is incompatible with the configured size"
            )
        self._input_name = inputs[0].name
        if len(self._session.get_outputs()) not in (6, 9):
            raise ValueError("Expected three SCRFD score heads and three box heads")

    def _preprocess(self, image: NDArray[np.uint8]) -> tuple[NDArray[np.float32], float]:
        width, height = self.config.internal_resolution_px
        image_height, image_width = image.shape[:2]
        ratio = image_height / image_width
        if ratio > height / width:
            resized_height, resized_width = height, max(1, int(height / ratio))
        else:
            resized_height, resized_width = max(1, int(width * ratio)), width
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        canvas[:resized_height, :resized_width] = cv2.resize(
            image, (resized_width, resized_height)
        )
        # Inputs already use RGB, so no BGR-to-RGB swap is needed.
        blob = cv2.dnn.blobFromImage(canvas, 1 / 128, (width, height), (127.5,) * 3)
        return blob, resized_height / image_height

    def _decode(
        self, outputs: list[NDArray[np.float32]], scale: float
    ) -> NDArray[np.float32]:
        width, height = self.config.internal_resolution_px
        all_boxes, all_scores = [], []
        for index, stride in enumerate(STRIDES):
            scores = outputs[index].reshape(-1)
            distances = outputs[index + len(STRIDES)].reshape(-1, 4)
            grid_width = width // stride
            count = (height // stride) * grid_width * ANCHORS_PER_CELL
            if len(scores) != count or len(distances) != count:
                raise ValueError(f"Unexpected SCRFD output shape at stride {stride}")
            candidates = np.flatnonzero(scores >= self.config.score_threshold)
            # Heads interleave two anchors at each row-major grid location.
            rows, cols = np.divmod(candidates // ANCHORS_PER_CELL, grid_width)
            centers = np.column_stack((cols, rows)).astype(np.float32) * stride
            offsets = distances[candidates] * stride
            boxes = np.column_stack((centers - offsets[:, :2], centers + offsets[:, 2:]))
            all_boxes.append(boxes)
            all_scores.append(scores[candidates])

        boxes = np.concatenate(all_boxes) / scale
        scores = np.concatenate(all_scores)
        keep = _non_maximum_suppression(boxes, scores, self.config.nms_threshold)
        return boxes[keep]

    def detect(self, image: NDArray[np.uint8]) -> FaceDetectionResult:
        started = perf_counter()
        inference_ms = 0.0
        try:
            if (
                not isinstance(image, np.ndarray)
                or image.dtype != np.uint8
                or image.ndim != 3
                or image.shape[2] != 3
                or not image.size
            ):
                raise ValueError("Expected a nonempty uint8 RGB image")
            blob, scale = self._preprocess(image)
            inference_started = perf_counter()
            try:
                outputs = self._session.run(None, {self._input_name: blob})
            except Exception as exc:
                raise ValueError(f"ONNX Runtime inference failed: {exc}") from exc
            finally:
                inference_ms = (perf_counter() - inference_started) * 1000
            boxes = tuple(
                (float(x), float(y), float(right - x), float(bottom - y))
                for x, y, right, bottom in self._decode(outputs, scale)
            )
        except (ValueError, cv2.error) as exc:
            return FaceDetectionResult(
                (), None, inference_ms, (perf_counter() - started) * 1000,
                "error", str(exc),
            )
        largest = max(boxes, key=lambda box: box[2] * box[3], default=None)
        return FaceDetectionResult(
            boxes, largest, inference_ms, (perf_counter() - started) * 1000,
            "ok" if boxes else "no_face", None if boxes else "no_face_detected",
        )
