#!/usr/bin/env python3
"""Run SCRFD on the 20 selected LFW images."""

import argparse
import csv
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

import cv2
import onnxruntime as ort
from _lfw_detection import run_lfw_detection

from face_processing_benchmark.methods.detection.deep_learning.scrfd import (
    ScrfdConfig,
    ScrfdDetector,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def run(
    dataset_root: Path, config_path: Path, output_root: Path, *, visuals: bool = True
) -> Path:
    config = ScrfdConfig.from_yaml(config_path, REPOSITORY_ROOT)
    started = perf_counter()
    detector = ScrfdDetector(config)
    return run_lfw_detection(
        dataset_root,
        output_root,
        detector,
        "scrfd",
        {
            "model_load_ms": (perf_counter() - started) * 1000,
            "onnxruntime_version": ort.__version__,
            "execution_provider": "CPUExecutionProvider",
            "checkpoint_sha256": config.sha256,
            "parameters": {
                **asdict(config),
                "model_path": config.model_path.relative_to(REPOSITORY_ROOT).as_posix(),
            },
        },
        write_visuals=visuals,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPOSITORY_ROOT / "datasets")
    parser.add_argument(
        "--config", type=Path, default=REPOSITORY_ROOT / "configs" / "methods.yaml"
    )
    parser.add_argument(
        "--output-root", type=Path, default=REPOSITORY_ROOT / "results" / "scrfd"
    )
    parser.add_argument("--no-visuals", action="store_true", help="Write reports only")
    args = parser.parse_args()
    try:
        run(
            args.root.resolve(), args.config, args.output_root.resolve(),
            visuals=not args.no_visuals,
        )
    except (OSError, ValueError, RuntimeError, csv.Error, cv2.error) as exc:
        parser.exit(1, f"SCRFD test failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
