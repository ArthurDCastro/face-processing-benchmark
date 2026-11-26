"""Geometry and background checks without a detector or dataset."""

import cv2
import numpy as np
import pytest

from face_processing_benchmark.methods.alignment.padding import (
    PaddingAligner,
    PaddingConfig,
)


def test_centered_face_preserves_image_and_dimensions():
    image = np.arange(12 * 16 * 3, dtype=np.uint8).reshape(12, 16, 3)
    box = (6, 4, 4, 4)

    result = PaddingAligner().align(image, box)

    assert result.image.shape == image.shape
    assert result.image.dtype == image.dtype
    np.testing.assert_array_equal(result.image, image)
    np.testing.assert_array_equal(result.matrix, [[1, 0, 0], [0, 1, 0]])
    assert result.transformed_face_box == box
    assert result.valid_mask.all()
    assert result.padding_area_px == 0
    assert result.padding_area_fraction == 0


@pytest.mark.parametrize(
    ("box", "translation", "source_region", "output_region"),
    [
        ((0, 0, 4, 4), (6, 4), np.s_[:8, :10], np.s_[4:, 6:]),
        ((12, 8, 4, 4), (-6, -4), np.s_[4:, 6:], np.s_[:8, :10]),
    ],
)
def test_edge_face_is_centered_and_empty_pixels_use_blurred_background(
    box, translation, source_region, output_region
):
    image = np.arange(12 * 16 * 3, dtype=np.uint8).reshape(12, 16, 3)
    config = PaddingConfig(background_scale=1.5, blur_sigma_fraction=0.1)

    result = PaddingAligner(config).align(image, box)

    assert result.image.shape == image.shape
    assert result.transformed_face_box == (6, 4, 4, 4)
    np.testing.assert_array_equal(result.matrix[:, 2], translation)
    np.testing.assert_array_equal(result.image[output_region], image[source_region])
    valid = np.zeros((12, 16), dtype=bool)
    valid[output_region] = True
    np.testing.assert_array_equal(result.valid_mask, valid)
    assert result.padding_area_px == 112
    assert result.padding_area_fraction == pytest.approx(112 / 192)
    enlarged = cv2.resize(image, (24, 18))
    background = cv2.GaussianBlur(enlarged[3:15, 4:20], (0, 0), 1.6)
    np.testing.assert_array_equal(result.image[~valid], background[~valid])


def test_fractional_target_and_partial_face_box_at_edge():
    image = np.full((12, 16, 3), 123, dtype=np.uint8)
    result = PaddingAligner(PaddingConfig(target_center_fraction_xy=(0.3, 0.75))).align(
        image, (-1, 8, 3, 4)
    )

    x, y, width, height = result.transformed_face_box
    assert (x + width / 2, y + height / 2) == pytest.approx((4.8, 9))
    np.testing.assert_allclose(result.matrix, [[1, 0, 4.3], [0, 1, -1]])
    expected_mask = np.zeros((12, 16), dtype=bool)
    expected_mask[:11, 5:] = True
    np.testing.assert_array_equal(result.valid_mask, expected_mask)
    np.testing.assert_array_equal(result.image, image)


@pytest.mark.parametrize("box", [(0, 0, 0, 4), (-5, 0, 4, 4), (0, 0, np.nan, 4)])
def test_invalid_box_raises_value_error(box):
    image = np.zeros((12, 16, 3), dtype=np.uint8)

    with pytest.raises(ValueError, match="Face box"):
        PaddingAligner().align(image, box)
