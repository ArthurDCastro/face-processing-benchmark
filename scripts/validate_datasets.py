#!/usr/bin/env python3
"""Validate dataset manifests and image/alpha-matte integrity without modifying raw files.

Usage:
    python scripts/prepare_datasets.py --index
    python scripts/validate_datasets.py --dataset all
    python scripts/validate_datasets.py --dataset ppm100

Writes reports under datasets/<name>/processed/validation/.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError
import numpy as np

EXPECTED_COUNTS = {"ppm100": 100, "p3m500np": 500}
DATASETS = ("lfw", "ppm100", "p3m500np")
VALID_MASK_MODES = {"1", "L", "I;16", "I;16B", "I;16L", "I", "F", "RGB", "RGBA", "LA"}


def image_info(path: Path, mask: bool = False) -> tuple[dict, list[str]]:
    problems = []
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        image.load()
        info = {"width": image.width, "height": image.height, "mode": image.mode, "format": image.format}
        if image.width < 1 or image.height < 1:
            problems.append("invalid_dimensions")
        if mask:
            if image.mode not in VALID_MASK_MODES:
                problems.append("unexpected_mask_mode")
            values = None
            # Accept RGB masks only when R, G and B encode exactly the same grayscale matte.
            # Do not use a color channel arbitrarily: this would silently corrupt annotations.
            if image.mode in ("RGB", "RGBA"):
                rgb = np.asarray(image.convert("RGB"))
                is_grayscale_rgb = bool(np.array_equal(rgb[..., 0], rgb[..., 1]) and np.array_equal(rgb[..., 1], rgb[..., 2]))
                if image.mode == "RGBA":
                    alpha = np.asarray(image.getchannel("A"))
                    # If alpha actually stores a matte, prioritize it. A fully opaque alpha
                    # channel commonly accompanies a grayscale-in-RGB mask.
                    if alpha.min() != alpha.max():
                        values = alpha
                        info["mask_source"] = "alpha"
                    elif is_grayscale_rgb:
                        values = rgb[..., 0]
                        info["mask_source"] = "rgb_grayscale"
                    else:
                        problems.append("ambiguous_rgba_mask")
                elif is_grayscale_rgb:
                    values = rgb[..., 0]
                    info["mask_source"] = "rgb_grayscale"
                else:
                    problems.append("rgb_channels_differ")
            elif image.mode == "LA":
                alpha = np.asarray(image.getchannel("A"))
                lum = np.asarray(image.getchannel("L"))
                if alpha.min() != alpha.max():
                    values = alpha
                    info["mask_source"] = "alpha"
                else:
                    values = lum
                    info["mask_source"] = "luminance"
            elif image.mode in VALID_MASK_MODES:
                values = np.asarray(image)
                info["mask_source"] = "single_channel"
            if values is not None:
                if values.ndim != 2:
                    problems.append("mask_not_single_channel")
                elif not np.isfinite(values).all():
                    problems.append("non_finite_mask_values")
                else:
                    info["mask_min"] = float(values.min())
                    info["mask_max"] = float(values.max())
                    info["mask_unique_values"] = int(np.unique(values).size)
                    if values.max() == values.min():
                        problems.append("constant_mask")
    return info, problems


def safe_file(root: Path, value: str) -> Path:
    if not value or not value.strip():
        raise ValueError("missing_path")
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("path_outside_dataset_root")
    if not path.is_file():
        raise FileNotFoundError(str(path))
    return path


def check_dataset(root: Path, name: str, expected_lfw: int) -> dict:
    source = root / name / "processed" / "manifest.csv"
    report_dir = root / name / "processed" / "validation"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = {"dataset": name, "manifest": str(source), "expected_minimum": expected_lfw if name == "lfw" else EXPECTED_COUNTS[name], "rows": 0, "valid_rows": 0, "error_rows": 0, "warning_rows": 0, "issues": {}, "status": "FAILED"}
    records = []
    if not source.is_file():
        report["issues"] = {"missing_manifest": 1}
        (report_dir / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        return report

    with source.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if not {"id", "image", "matte"}.issubset(set(reader.fieldnames or [])):
            report["issues"] = {"invalid_manifest_columns": 1}
            (report_dir / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
            return report
        rows = list(reader)
    report["rows"] = len(rows)
    ids = Counter(row.get("id", "") for row in rows)
    images = Counter(row.get("image", "") for row in rows)
    mattes = Counter(row.get("matte", "") for row in rows if row.get("matte"))
    issue_counts = Counter()
    for row in rows:
        issues = []
        warnings = []
        image_info_result = {}
        matte_info_result = {}
        id_ = row.get("id", "").strip()
        if not id_:
            issues.append("empty_id")
        elif ids[id_] > 1:
            issues.append("duplicate_id")
        if images[row.get("image", "")] > 1:
            issues.append("duplicate_image_path")
        if name != "lfw" and row.get("matte") and mattes[row["matte"]] > 1:
            issues.append("duplicate_matte_path")
        try:
            image_path = safe_file(root, row.get("image", ""))
            image_info_result, image_problems = image_info(image_path)
            issues.extend(image_problems)
        except (OSError, ValueError, UnidentifiedImageError, MemoryError) as exc:
            issues.append("image_invalid_or_missing")
            warnings.append(f"image_detail: {str(exc)[:200]}")
        if name != "lfw":
            try:
                mask_path = safe_file(root, row.get("matte", ""))
                matte_info_result, mask_problems = image_info(mask_path, mask=True)
                for issue in mask_problems:
                    if issue in ("constant_mask", "unexpected_mask_mode"):
                        warnings.append(issue)
                    else:
                        issues.append(issue)
                if image_info_result and (image_info_result["width"], image_info_result["height"]) != (matte_info_result["width"], matte_info_result["height"]):
                    issues.append("dimension_mismatch")
            except (OSError, ValueError, UnidentifiedImageError, MemoryError) as exc:
                issues.append("matte_invalid_or_missing")
                warnings.append(f"matte_detail: {str(exc)[:200]}")
        else:
            if row.get("matte"):
                warnings.append("lfw_unexpected_matte")
        for issue in issues:
            issue_counts[issue] += 1
        report["valid_rows"] += not issues
        report["error_rows"] += bool(issues)
        report["warning_rows"] += bool(warnings)
        records.append({"id": id_, "image": row.get("image", ""), "matte": row.get("matte", ""), "status": "ERROR" if issues else ("WARNING" if warnings else "OK"), "errors": ";".join(issues), "warnings": ";".join(warnings), "image_width": image_info_result.get("width", ""), "image_height": image_info_result.get("height", ""), "image_mode": image_info_result.get("mode", ""), "matte_width": matte_info_result.get("width", ""), "matte_height": matte_info_result.get("height", ""), "matte_mode": matte_info_result.get("mode", ""), "matte_source": matte_info_result.get("mask_source", ""), "matte_min": matte_info_result.get("mask_min", ""), "matte_max": matte_info_result.get("mask_max", "")})
    if len(rows) < report["expected_minimum"]:
        issue_counts["insufficient_images"] += 1
    if name != "lfw" and len(rows) > report["expected_minimum"]:
        issue_counts["unexpected_extra_pairs"] += 1
    pairing_issues = root / name / "processed" / "pairing_issues.txt"
    if pairing_issues.is_file():
        lines = [line.strip() for line in pairing_issues.read_text(encoding="utf-8").splitlines()]
        actual_issues = [line for line in lines if line and line not in ("Missing matches:", "Ambiguous matches:")]
        if actual_issues:
            issue_counts["index_pairing_issues"] += 1
    report["issues"] = dict(issue_counts)
    report["status"] = "PASS" if report["error_rows"] == 0 and not issue_counts else "FAILED"
    with (report_dir / "files.csv").open("w", newline="", encoding="utf-8") as stream:
        fields = list(records[0].keys()) if records else ["id", "image", "matte", "status", "errors", "warnings", "image_width", "image_height", "image_mode", "matte_width", "matte_height", "matte_mode", "matte_source", "matte_min", "matte_max"]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    (report_dir / "summary.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent / "datasets", help="Dataset directory (default: <repository>/datasets)")
    parser.add_argument("--dataset", choices=("all", *DATASETS), default="all")
    parser.add_argument("--min-lfw", type=int, default=1000, help="Minimum LFW images available for selection")
    args = parser.parse_args()
    if args.min_lfw < 1:
        parser.error("--min-lfw must be positive")
    root = args.root.resolve()
    if not root.is_dir():
        parser.error(f"Dataset directory does not exist: {root}. Use --root with the real dataset path.")
    names = DATASETS if args.dataset == "all" else (args.dataset,)
    failed = False
    for name in names:
        result = check_dataset(root, name, args.min_lfw)
        print(f"{name}: {result['status']} | {result['valid_rows']}/{result['rows']} valid | {result['warning_rows']} warning rows | issues={result['issues']}")
        failed |= result["status"] != "PASS"
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
