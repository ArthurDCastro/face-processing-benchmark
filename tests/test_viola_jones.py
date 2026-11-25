"""Checks for the Viola–Jones adapter and its isolated LFW runner."""

import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

cv2 = pytest.importorskip("cv2")
np = pytest.importorskip("numpy")

from face_processing_benchmark.methods.detection.classical.haar_cascade import (  # noqa: E402
    ViolaJonesConfig,
    ViolaJonesDetector,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def config():
    return ViolaJonesConfig.from_yaml(ROOT / "configs/methods.yaml", ROOT)


def test_preprocessing_parameters_scale_and_largest_face(config):
    detector = ViolaJonesDetector(config)
    image = np.full((1024, 2048, 3), (255, 0, 0), dtype=np.uint8)
    original = image.copy()

    class Cascade:
        def detectMultiScale(self, gray, **params):
            assert gray.shape == (512, 1024)
            assert (gray == 76).all()
            assert params == {
                "scaleFactor": 1.1, "minNeighbors": 5, "minSize": (30, 30)
            }
            return np.array([(30, 40, 50, 40), (10, 20, 30, 70)])

    detector._cascade = Cascade()
    result = detector.detect(image)
    assert result.status == "ok"
    assert result.boxes == ((60, 80, 100, 80), (20, 40, 60, 140))
    assert result.largest_face == result.boxes[1]
    assert result.total_ms >= result.inference_ms >= 0
    assert np.array_equal(image, original)


def test_no_face_and_invalid_input_are_distinct(config):
    detector = ViolaJonesDetector(config)
    empty = detector.detect(np.zeros((100, 100, 3), dtype=np.uint8))
    invalid = detector.detect(np.zeros((100, 100), dtype=np.uint8))
    assert (empty.status, empty.boxes, empty.largest_face) == ("no_face", (), None)
    assert empty.error_reason == "no_face_detected"
    assert empty.total_ms >= empty.inference_ms >= 0
    assert invalid.status == "error"
    assert invalid.boxes == () and invalid.largest_face is None
    assert "RGB" in invalid.error_reason


def test_standalone_runner_records_all_samples(tmp_path):
    dataset = tmp_path / "datasets"
    raw = dataset / "lfw" / "raw"
    processed = dataset / "lfw" / "processed"
    raw.mkdir(parents=True)
    processed.mkdir()
    image = np.zeros((64, 64, 3), dtype=np.uint8)
    with (processed / "test_samples.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["id", "image", "matte"])
        for index in range(20):
            name = f"{index}.png"
            if index != 19:
                assert cv2.imwrite(str(raw / name), image)
            writer.writerow([index, f"lfw/raw/{name}", ""])

    output = tmp_path / "results"
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/test_viola_jones.py"),
         "--root", str(dataset), "--output-root", str(output)],
        check=True,
    )
    (run,) = output.iterdir()
    summary = json.loads((run / "summary.json").read_text())
    assert summary["sample_count"] == 20
    assert summary["no_face"] == 19
    assert summary["errors"] == 1
    assert summary["detected"] == 0
    assert len(summary["cascade_sha256"]) == 64
    assert len(list((run / "visuals").glob("*.png"))) == 19
    with (run / "per_image.csv").open(newline="") as stream:
        records = list(csv.DictReader(stream))
    assert len(records) == 20
    assert records[0]["boxes_xywh"] == "[]"
    assert records[-1]["status"] == "error"
    assert records[-1]["visual"] == ""
