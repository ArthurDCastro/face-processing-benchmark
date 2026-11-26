"""Shared output types for benchmark methods."""

from dataclasses import dataclass
from typing import Literal
import numpy as np
from numpy.typing import NDArray

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


@dataclass(frozen=True)
class ImageAlignmentResult:
    """RGB output and geometry in pixels.

    The 2x3 matrix maps source coordinates to output coordinates. True mask
    values identify output pixels sampled entirely from the translated source.
    The transformed box uses the same geometry and may extend past the canvas.
    """

    image: NDArray[np.uint8]
    matrix: NDArray[np.float64]
    valid_mask: NDArray[np.bool_]
    transformed_face_box: FaceBox

    @property
    def padding_area_px(self) -> int:
        return self.valid_mask.size - int(np.count_nonzero(self.valid_mask))

    @property
    def padding_area_fraction(self) -> float:
        return self.padding_area_px / self.valid_mask.size
