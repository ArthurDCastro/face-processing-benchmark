"""Tests for the SCRFD adapter and official checkpoint."""

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

pytest.importorskip("cv2")
np = pytest.importorskip("numpy")
ort = pytest.importorskip("onnxruntime")

from face_processing_benchmark.methods.detection.deep_learning.scrfd import (  # noqa: E402
    ScrfdConfig,
    ScrfdDetector,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def config():
    return ScrfdConfig.from_yaml(ROOT / "configs/methods.yaml", ROOT)


def test_decode_filter_nms_and_original_coordinates(config, monkeypatch):
    class Session:
        def get_inputs(self):
            return [SimpleNamespace(name="input", shape=[1, 3, "height", "width"])]

        def get_outputs(self):
            return range(6)

        def run(self, output_names, inputs):
            assert output_names is None
            blob = inputs["input"]
            assert blob.shape == (1, 3, 64, 64)
            assert blob.dtype == np.float32
            np.testing.assert_allclose(
                blob[0, :, 0, 0], (np.array([220, 50, 10]) - 127.5) / 128
            )
            assert (blob[0, :, 32:] == -127.5 / 128).all()
            scores = [np.zeros((1, count, 1), dtype=np.float32) for count in (128, 32, 8)]
            boxes = [np.zeros((1, count, 4), dtype=np.float32) for count in (128, 32, 8)]
            # First two anchors share a center and identical boxes. The
            # higher scoring smaller face is retained ahead of the larger one.
            scores[0][0, [18, 19, 44, 46], 0] = [0.9, 0.8, 0.7, 0.49]
            boxes[0][0, [18, 19], :] = 0.5
            boxes[0][0, 44, :] = 1
            return scores + boxes

    def create(model, *, providers):
        assert isinstance(model, bytes)
        assert providers == ["CPUExecutionProvider"]
        return Session()

    monkeypatch.setattr(ort, "InferenceSession", create)
    config = replace(config, internal_resolution_px=(64, 64))
    image = np.full((16, 32, 3), (220, 50, 10), dtype=np.uint8)
    result = ScrfdDetector(config).detect(image)
    assert result.status == "ok"
    assert result.boxes == ((2, 2, 4, 4), (20, 4, 8, 8))
    assert result.largest_face == result.boxes[1]
    assert result.total_ms >= result.inference_ms >= 0
    assert tuple(image[0, 0]) == (220, 50, 10)


def test_official_checkpoint_no_face_and_invalid_input(config):
    detector = ScrfdDetector(config)
    result = detector.detect(np.zeros((100, 140, 3), dtype=np.uint8))
    assert result.status == "no_face"
    assert result.boxes == () and result.largest_face is None
    assert result.error_reason == "no_face_detected"
    assert result.total_ms >= result.inference_ms >= 0
    invalid = detector.detect(np.zeros((100, 140), dtype=np.uint8))
    assert invalid.status == "error"
    assert "RGB" in invalid.error_reason


def test_runtime_failure_is_recorded(config, monkeypatch):
    class BrokenSession:
        def run(self, *_args):
            raise RuntimeError("inference failed")

    detector = ScrfdDetector(config)
    monkeypatch.setattr(detector, "_session", BrokenSession())
    result = detector.detect(np.zeros((64, 64, 3), dtype=np.uint8))
    assert result.status == "error"
    assert "inference failed" in result.error_reason
    assert result.boxes == () and result.largest_face is None
    assert result.total_ms >= result.inference_ms >= 0


def test_checkpoint_digest_mismatch(config, tmp_path):
    path = tmp_path / "incorrect.onnx"
    path.write_bytes(b"incorrect checkpoint")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        ScrfdDetector(replace(config, model_path=path))
