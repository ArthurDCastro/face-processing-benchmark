#!/usr/bin/env python3
"""Compare original and Padding-aligned images on the 20 selected LFW samples."""

import argparse
import csv
import hashlib
import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from statistics import mean
from tempfile import mkdtemp
from time import perf_counter

import cv2
from _lfw_detection import read_lfw_image, read_manifest

from face_processing_benchmark.core.interfaces import FaceDetector, ImageAligner
from face_processing_benchmark.methods.alignment.padding import (
    PaddingAligner,
    PaddingConfig,
)
from face_processing_benchmark.methods.detection.deep_learning.yunet import (
    YuNetConfig,
    YuNetDetector,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def process_sample(
    root: Path, source: str, visual: Path, detector: FaceDetector, aligner: ImageAligner
) -> dict:
    record = {
        "status": "error",
        "error_reason": None,
        "face_box_xywh": None,
        "transformed_face_box_xywh": None,
        "matrix": None,
        "output_width": None,
        "output_height": None,
        "padding_area_px": None,
        "padding_area_fraction": None,
        "alignment_ms": None,
        "visual": None,
    }
    try:
        image = read_lfw_image(root, source)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        detection = detector.detect(rgb)
        if detection.status != "ok" or detection.largest_face is None:
            record["status"] = "no_face" if detection.status == "no_face" else "error"
            record["error_reason"] = detection.error_reason or "No usable face box"
            return record
        box = detection.largest_face
        record["face_box_xywh"] = json.dumps(box)
        started = perf_counter()
        result = aligner.align(rgb, box)
        record["alignment_ms"] = (perf_counter() - started) * 1000
        output = cv2.cvtColor(result.image, cv2.COLOR_RGB2BGR)
        if not cv2.imwrite(str(visual), cv2.hconcat([image, output])):
            raise OSError(f"Could not write comparison: {visual}")
        record.update(
            status="ok",
            transformed_face_box_xywh=json.dumps(result.transformed_face_box),
            matrix=json.dumps(result.matrix.tolist()),
            output_width=output.shape[1],
            output_height=output.shape[0],
            padding_area_px=result.padding_area_px,
            padding_area_fraction=result.padding_area_fraction,
            visual=visual.relative_to(visual.parent.parent).as_posix(),
        )
    except (OSError, ValueError, cv2.error) as exc:
        record["error_reason"] = str(exc)
    return record


def run(
    dataset_root: Path, config_path: Path, output_root: Path, padding: PaddingConfig
) -> Path:
    manifest = dataset_root / "lfw" / "processed" / "test_samples.csv"
    rows = read_manifest(manifest)
    yunet = YuNetConfig.from_yaml(config_path, REPOSITORY_ROOT)
    detector = YuNetDetector(yunet)
    aligner = PaddingAligner(padding)

    output_root.mkdir(parents=True, exist_ok=True)
    run_dir = Path(mkdtemp(prefix="run-", dir=output_root))
    visual_dir = run_dir / "visuals"
    visual_dir.mkdir()
    records = [
        {
            "image_id": row["id"],
            "image": row["image"],
            **process_sample(
                dataset_root, row["image"], visual_dir / f"{index:02d}.png",
                detector, aligner,
            ),
        }
        for index, row in enumerate(rows, 1)
    ]
    with (run_dir / "per_image.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

    counts = Counter(record["status"] for record in records)
    areas = [r["padding_area_fraction"] for r in records if r["status"] == "ok"]
    summary = {
        "method_id": "padding",
        "detector_id": "yunet",
        "dataset_id": "lfw",
        "sample_count": len(records),
        "aligned": counts["ok"],
        "no_face": counts["no_face"],
        "errors": counts["error"],
        "mean_padding_area_fraction": mean(areas) if areas else None,
        "padding_parameters": asdict(padding),
        "detector_parameters": {
            **asdict(yunet),
            "model_path": yunet.model_path.relative_to(REPOSITORY_ROOT).as_posix(),
        },
        "opencv_version": cv2.__version__,
        "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{counts['ok']}/{len(records)} images aligned. Results: {run_dir}")
    return run_dir


def main() -> int:
    defaults = PaddingConfig()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPOSITORY_ROOT / "datasets")
    parser.add_argument(
        "--config", type=Path, default=REPOSITORY_ROOT / "configs" / "methods.yaml"
    )
    parser.add_argument(
        "--output-root", type=Path, default=REPOSITORY_ROOT / "results" / "padding"
    )
    parser.add_argument(
        "--target-center", nargs=2, type=float, metavar=("X", "Y"),
        default=defaults.target_center_fraction_xy,
    )
    parser.add_argument(
        "--background-scale", type=float, default=defaults.background_scale
    )
    parser.add_argument(
        "--blur-sigma-fraction", type=float, default=defaults.blur_sigma_fraction
    )
    args = parser.parse_args()
    try:
        padding = PaddingConfig(
            tuple(args.target_center), args.background_scale, args.blur_sigma_fraction
        )
        run(args.root.resolve(), args.config, args.output_root.resolve(), padding)
    except (OSError, ValueError, RuntimeError, csv.Error, cv2.error) as exc:
        parser.exit(1, f"Padding test failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
