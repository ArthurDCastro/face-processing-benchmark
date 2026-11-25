"""Interfaces for benchmark methods."""

from typing import Protocol

import numpy as np
from numpy.typing import NDArray

from .types import FaceDetectionResult


class FaceDetector(Protocol):
    def detect(self, image: NDArray[np.uint8]) -> FaceDetectionResult:
        """Detect faces in an RGB image and return boxes in its original pixel space."""
        ...
