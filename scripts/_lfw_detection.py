"""Shared reporting for isolated detection tests on the selected LFW images."""

import csv
import hashlib
import json
from pathlib import Path
from statistics import median
from tempfile import mkdtemp

import cv2

from face_processing_benchmark.core.interfaces import FaceDetector
from face_processing_benchmark.core.types import FaceDetectionResult


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream, strict=True)
        if reader.fieldnames != ["id", "image", "matte"]:
            raise ValueError(f"Unexpected manifest columns: {path}")
        rows = list(reader)
    if (
        len(rows) != 20
        or any(not row["id"] or not row["image"] or row["matte"] != "" for row in rows)
        or len({row["id"] for row in rows}) != 20
        or len({row["image"] for row in rows}) != 20
    ):
        raise ValueError(f"Expected 20 unique LFW image entries in {path}")
    return rows


def process_image(
    detector: FaceDetector, root: Path, source: str, visual: Path | None
) -> FaceDetectionResult:
    try:
        relative = Path(source)
        path = (root / relative).resolve()
        if relative.is_absolute() or not path.is_relative_to(root / "lfw" / "raw"):
            raise ValueError("Image path must be relative to the LFW raw directory")
        if not path.is_file():
            raise ValueError("Image file is missing")
        image = cv2.imread(str(path), cv2.IMREAD_COLOR | cv2.IMREAD_IGNORE_ORIENTATION)
        if image is None:
            raise ValueError("Image cannot be decoded")
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    except (OSError, ValueError, cv2.error) as exc:
        return FaceDetectionResult((), None, 0.0, 0.0, "error", str(exc))

    result = detector.detect(rgb)
    if visual is None:
        return result
    for box in result.boxes:
        x, y, width, height = box
        color = (0, 255, 0) if box == result.largest_face else (0, 165, 255)
        cv2.rectangle(
            image, (round(x), round(y)),
            (round(x + width) - 1, round(y + height) - 1), color, 2,
        )
    if result.status != "ok":
        cv2.putText(image, result.status, (6, 20), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 255), 1, cv2.LINE_AA)
    if not cv2.imwrite(str(visual), image):
        raise OSError(f"Could not write annotated image: {visual}")
    return result


def run_lfw_detection(
    dataset_root: Path,
    output_root: Path,
    detector: FaceDetector,
    method_id: str,
    metadata: dict,
    *,
    write_visuals: bool = True,
) -> Path:
    manifest = dataset_root / "lfw" / "processed" / "test_samples.csv"
    rows = read_manifest(manifest)
    output_root.mkdir(parents=True, exist_ok=True)
    run_dir = Path(mkdtemp(prefix="run-", dir=output_root))
    visual_dir = run_dir / "visuals"
    if write_visuals:
        visual_dir.mkdir()
    records = []
    for index, row in enumerate(rows, 1):
        visual = visual_dir / f"{index:02d}.png" if write_visuals else None
        result = process_image(detector, dataset_root, row["image"], visual)
        records.append({
            "image_id": row["id"],
            "image": row["image"],
            "status": result.status,
            "error_reason": result.error_reason,
            "face_count": len(result.boxes),
            "boxes_xywh": json.dumps(result.boxes),
            "largest_face_xywh": json.dumps(result.largest_face),
            "inference_ms": result.inference_ms,
            "total_ms": result.total_ms,
            "visual": (
                visual.relative_to(run_dir).as_posix()
                if visual is not None and visual.is_file()
                else ""
            ),
        })

    with (run_dir / "per_image.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

    measured = [row for row in records if row["status"] != "error"]
    detected = sum(row["status"] == "ok" for row in records)
    summary = {
        "method_id": method_id,
        "dataset_id": "lfw",
        "sample_count": len(records),
        "detected": detected,
        "no_face": sum(row["status"] == "no_face" for row in records),
        "errors": len(records) - len(measured),
        "multiple_faces": sum(row["face_count"] > 1 for row in records),
        "detection_rate": detected / len(records),
        "timed_samples": len(measured),
        "median_inference_ms": median(row["inference_ms"] for row in measured)
        if measured else None,
        "median_total_ms": median(row["total_ms"] for row in measured)
        if measured else None,
        "opencv_version": cv2.__version__,
        "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        **metadata,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"{detected}/{len(records)} images with a detection. Results: {run_dir}")
    return run_dir
