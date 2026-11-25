"""Tests for YuNet configuration, coordinate conversion and detection results."""

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

cv2 = pytest.importorskip("cv2")
np = pytest.importorskip("numpy")

from face_processing_benchmark.methods.detection.deep_learning.yunet import (  # noqa: E402
    YuNetConfig,
    YuNetDetector,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def config():
    return YuNetConfig.from_yaml(ROOT / "configs/methods.yaml", ROOT)


def test_input_scaling_box_conversion_and_largest(config, monkeypatch):
    class Network:
        def setInputSize(self, size):
            assert size == (1024, 512)

        def detect(self, image):
            assert image.shape == (512, 1024, 3)
            assert tuple(image[0, 0]) == (10, 20, 200)
            faces = np.zeros((2, 15), dtype=np.float32)
            faces[:, :4] = [(10, 20, 40, 50), (30, 40, 60, 70)]
            return 1, faces

    def create(path, model_config, initial_size, **kwargs):
        assert Path(path) == config.model_path
        assert model_config == ""
        assert initial_size == (320, 320)
        assert kwargs == {"score_threshold": 0.7, "nms_threshold": 0.3, "top_k": 5000}
        return Network()

    monkeypatch.setattr(cv2, "FaceDetectorYN", SimpleNamespace(create=create))
    detector = YuNetDetector(config)
    image = np.full((1024, 2048, 3), (200, 20, 10), dtype=np.uint8)
    result = detector.detect(image)
    assert result.status == "ok"
    assert result.boxes == ((20, 40, 80, 100), (60, 80, 120, 140))
    assert result.largest_face == result.boxes[1]
    assert result.total_ms >= result.inference_ms >= 0
    assert tuple(image[0, 0]) == (200, 20, 10)


def test_official_model_no_face_and_input_failure(config):
    detector = YuNetDetector(config)
    blank = detector.detect(np.zeros((121, 137, 3), dtype=np.uint8))
    assert blank.status == "no_face"
    assert blank.boxes == () and blank.largest_face is None
    assert blank.error_reason == "no_face_detected"
    assert blank.total_ms >= blank.inference_ms >= 0

    invalid = detector.detect(np.zeros((80, 120), dtype=np.uint8))
    assert invalid.status == "error"
    assert invalid.boxes == () and invalid.largest_face is None
    assert "RGB" in invalid.error_reason


def test_opencv_failure_is_recorded(config, monkeypatch):
    detector = YuNetDetector(config)

    class BrokenNetwork:
        def setInputSize(self, size):
            raise cv2.error("inference failed")

    monkeypatch.setattr(detector, "_model", BrokenNetwork())
    result = detector.detect(np.zeros((80, 120, 3), dtype=np.uint8))
    assert (result.status, result.error_reason) == ("error", "inference failed")
    assert result.boxes == () and result.largest_face is None
    assert result.total_ms >= result.inference_ms >= 0


def test_checkpoint_digest_mismatch(config, tmp_path):
    path = tmp_path / "incorrect.onnx"
    path.write_bytes(b"incorrect checkpoint")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        YuNetDetector(replace(config, model_path=path))
