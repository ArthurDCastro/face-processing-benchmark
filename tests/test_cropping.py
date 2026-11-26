"""Geometry checks for Cropping with synthetic RGB images."""

from pathlib import Path

import numpy as np
import pytest

from face_processing_benchmark.methods.alignment.cropping import (
    CroppingAligner,
    CroppingConfig,
)


def test_centered_box_keeps_full_image():
    image = np.arange(12 * 16 * 3, dtype=np.uint8).reshape(12, 16, 3)
    box = (6, 4, 4, 4)

    result = CroppingAligner().align(image, box)

    assert result.crop_bounds_xyxy == (0, 0, 16, 12)
    assert (result.output_width, result.output_height) == (16, 12)
    assert result.retained_area_percent == 100
    assert result.transformed_face_box == box
    assert result.valid_mask.all()
    np.testing.assert_array_equal(result.image, image)
    np.testing.assert_array_equal(result.matrix, [[1, 0, 0], [0, 1, 0]])


@pytest.mark.parametrize(
    ("box", "bounds"),
    [((0, 1, 4, 4), (0, 0, 5, 5)), ((12, 7, 4, 4), (11, 6, 16, 11))],
)
def test_edge_crop_is_maximal_and_inside_source(box, bounds):
    image = np.arange(16 * 16 * 3, dtype=np.uint8).reshape(16, 16, 3)
    result = CroppingAligner().align(image, box)
    x, y, w, h = box
    # The nearest pixel origin can place the face center half a pixel off target.
    left, top, right, bottom = result.crop_bounds_xyxy
    assert result.crop_bounds_xyxy == bounds
    assert 0 <= left <= x < x + w <= right <= 16
    assert 0 <= top <= y < y + h <= bottom <= 16
    assert result.image.shape == (5, 5, 3)
    assert abs(x + w / 2 - left - 2.5) <= 0.5
    assert abs(y + h / 2 - top - 2.5) <= 0.5
    np.testing.assert_array_equal(result.image, image[top:bottom, left:right])
    assert result.retained_area_ratio == pytest.approx(25 / 256)


def test_noncentral_target_keeps_exact_rectangular_aspect_ratio():
    image = np.zeros((18, 24, 3), dtype=np.uint8)
    result = CroppingAligner(CroppingConfig((0.25, 0.75))).align(image, (4, 7, 2, 4))

    assert result.crop_bounds_xyxy == (1, 0, 17, 12)
    assert result.output_width * image.shape[0] == result.output_height * image.shape[1]
    x, y, w, h = result.transformed_face_box
    assert (x + w / 2, y + h / 2) == (4, 9)
    np.testing.assert_array_equal(result.matrix, [[1, 0, -1], [0, 1, 0]])


@pytest.mark.parametrize("box", [(-1, 1, 4, 4), (13, 1, 4, 4), (0, 0, 0, 4)])
def test_out_of_bounds_or_empty_box_is_rejected(box):
    with pytest.raises(ValueError, match="Face box"):
        CroppingAligner().align(np.zeros((12, 16, 3), dtype=np.uint8), box)


def test_no_positive_crop_for_coprime_dimensions():
    with pytest.raises(ValueError, match="No positive crop"):
        CroppingAligner().align(np.zeros((11, 17, 3), dtype=np.uint8), (0, 0, 2, 2))


def test_crop_that_cuts_face_is_rejected():
    with pytest.raises(ValueError, match="cannot contain the face box"):
        CroppingAligner().align(np.zeros((12, 16, 3), dtype=np.uint8), (0, 0, 4, 8))


def test_yaml_target_is_loaded(tmp_path: Path):
    config = tmp_path / "e1.yaml"
    config.write_text(
        "schema_version: 2\nkind: experiment\nexperiment_id: e1_centering\n"
        "centering: {strategy: crop}\n"
        "synthetic_canvas: {target_center_fraction_xy: [0.25, 0.75]}\n",
        encoding="utf-8",
    )
    assert CroppingConfig.from_yaml(config).target_center_fraction_xy == (0.25, 0.75)
