"""Shared output types for face detection."""

from dataclasses import dataclass
from typing import Literal

# Pixel coordinates in the input image, before detector-specific resizing.
FaceBox = tuple[float, float, float, float]


@dataclass(frozen=True)
class FaceDetectionResult:
    boxes: tuple[FaceBox, ...]
    largest_face: FaceBox | None
    inference_ms: float
    total_ms: float
    status: Literal["ok", "no_face", "error"]
    error_reason: str | None = None
