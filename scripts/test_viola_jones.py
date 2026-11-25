#!/usr/bin/env python3
"""Run the Viola-Jones detector on the 20 selected LFW images."""

import argparse
import csv
import hashlib
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

import cv2
from _lfw_detection import run_lfw_detection

from face_processing_benchmark.methods.detection.classical.haar_cascade import (
    ViolaJonesConfig,
    ViolaJonesDetector,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def run(dataset_root: Path, config_path: Path, output_root: Path) -> Path:
    config = ViolaJonesConfig.from_yaml(config_path, REPOSITORY_ROOT)
    started = perf_counter()
    detector = ViolaJonesDetector(config)
    model_load_ms = (perf_counter() - started) * 1000
    return run_lfw_detection(
        dataset_root, output_root, detector, "viola_jones",
        {
            "model_load_ms": model_load_ms,
            "cascade_sha256": hashlib.sha256(config.cascade_path.read_bytes()).hexdigest(),
            "parameters": {**asdict(config), "cascade_path": config.cascade_path.name},
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPOSITORY_ROOT / "datasets")
    parser.add_argument("--config", type=Path,
                        default=REPOSITORY_ROOT / "configs" / "methods.yaml")
    parser.add_argument("--output-root", type=Path,
                        default=REPOSITORY_ROOT / "results" / "viola_jones")
    args = parser.parse_args()
    try:
        run(args.root.resolve(), args.config, args.output_root.resolve())
    except (OSError, ValueError, csv.Error, cv2.error) as exc:
        parser.exit(1, f"Viola-Jones test failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
