"""Tests for the dlib adapter and its isolated LFW report format."""

import csv
import importlib.util
import json
from pathlib import Path

import pytest

dlib = pytest.importorskip("dlib")
np = pytest.importorskip("numpy")

from face_processing_benchmark.methods.detection.classical.hog_svm import (  # noqa: E402
    HogSvmConfig,
    HogSvmDetector,
)

ROOT = Path(__file__).resolve().parents[1]


def test_all_boxes_and_largest_on_original_grid(monkeypatch):
    config = HogSvmConfig.from_yaml(ROOT / "configs/methods.yaml")
    image = np.zeros((80, 120, 3), dtype=np.uint8)[:, ::-1]
    image[0, 0] = (255, 12, 34)

    def detect(rgb, upsample_count):
        assert rgb.shape == image.shape and rgb.flags.c_contiguous
        assert tuple(rgb[0, 0]) == (255, 12, 34)
        assert upsample_count == config.upsample_count == 1
        return [dlib.rectangle(-2, 4, 10, 20), dlib.rectangle(20, 30, 59, 59)]

    monkeypatch.setattr(dlib, "get_frontal_face_detector", lambda: detect)
    result = HogSvmDetector(config).detect(image)
    assert result.boxes == ((-2, 4, 13, 17), (20, 30, 40, 30))
    assert result.largest_face == result.boxes[1]
    assert result.status == "ok"
    assert result.error_reason is None
    assert result.total_ms >= result.inference_ms >= 0
    assert tuple(image[0, 0]) == (255, 12, 34)


def test_no_face_invalid_input_and_inference_failure(monkeypatch):
    detector = HogSvmDetector(HogSvmConfig(0))
    image = np.zeros((80, 120, 3), dtype=np.uint8)
    assert detector.detect(image).status == "no_face"
    assert detector.detect(image[..., 0]).status == "error"

    def fail(*_args):
        raise RuntimeError("inference failed")

    monkeypatch.setattr(detector, "_detector", fail)
    result = detector.detect(image)
    assert (result.status, result.error_reason) == ("error", "inference failed")
    assert result.boxes == () and result.largest_face is None
    assert result.total_ms >= result.inference_ms >= 0


@pytest.mark.parametrize("upsample_count", [-1, True, 1.5, None])
def test_invalid_upsample_count(upsample_count):
    with pytest.raises(ValueError, match="nonnegative integer"):
        HogSvmConfig(upsample_count)


@pytest.mark.parametrize("visuals", [True, False])
def test_runner_reports_boxes_and_missing_input(tmp_path, monkeypatch, visuals):
    cv2 = pytest.importorskip("cv2")
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location(
        "run_hog_svm", ROOT / "scripts/test_hog_svm.py"
    )
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    monkeypatch.setattr(
        dlib, "get_frontal_face_detector",
        lambda: lambda *_args: [dlib.rectangle(6, 8, 29, 39)],
    )

    dataset = tmp_path / "datasets"
    raw = dataset / "lfw/raw"
    processed = dataset / "lfw/processed"
    raw.mkdir(parents=True)
    processed.mkdir()
    with (processed / "test_samples.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["id", "image", "matte"])
        for i in range(20):
            if i != 19:
                image = np.zeros((60, 60, 3), dtype=np.uint8)
                assert cv2.imwrite(str(raw / f"{i}.png"), image)
            writer.writerow([i, f"lfw/raw/{i}.png", ""])

    run = runner.run(
        dataset, ROOT / "configs/methods.yaml", tmp_path / "results", visuals=visuals
    )
    summary = json.loads((run / "summary.json").read_text())
    assert summary["method_id"] == "hog_svm"
    assert (summary["sample_count"], summary["detected"], summary["errors"]) == (20, 19, 1)
    assert summary["dlib_version"] == dlib.__version__
    with (run / "per_image.csv").open(newline="") as stream:
        records = list(csv.DictReader(stream))
    assert len(records) == 20
    assert json.loads(records[0]["boxes_xywh"]) == [[6, 8, 24, 32]]
    assert json.loads(records[0]["largest_face_xywh"]) == [6, 8, 24, 32]
    assert records[-1]["status"] == "error"
    assert records[-1]["visual"] == ""
    if visuals:
        assert len(list((run / "visuals").glob("*.png"))) == 19
        annotated = cv2.imread(str(run / records[0]["visual"]))
        assert tuple(annotated[8, 6]) == (0, 255, 0)
    else:
        assert not (run / "visuals").exists()
        assert records[0]["visual"] == ""
