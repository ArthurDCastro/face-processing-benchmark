"""Interfaces for benchmark methods."""

from typing import Protocol

import numpy as np
from numpy.typing import NDArray

from .types import FaceBox, FaceDetectionResult, ImageAlignmentResult


class FaceDetector(Protocol):
    def detect(self, image: NDArray[np.uint8]) -> FaceDetectionResult:
        """Detect faces in an RGB image and return boxes in its original pixel space."""
        ...


class ImageAligner(Protocol):
    def align(
        self, image: NDArray[np.uint8], face_box: FaceBox
    ) -> ImageAlignmentResult:
        """Align an RGB image using a face box in its original pixel space."""
        ...
