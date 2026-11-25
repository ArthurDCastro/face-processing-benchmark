#!/usr/bin/env python3
"""Select reproducible technical test samples from LFW and PPM-100 manifests."""

from __future__ import annotations

import argparse
import csv
import random
import sys
from collections import Counter
from pathlib import Path
from tempfile import NamedTemporaryFile

from PIL import Image

from validate_datasets import image_info, safe_file

DATASETS = ("lfw", "ppm100")
COLUMNS = ("id", "image", "matte")
SAMPLE_COUNT = 20
SEED = 42

Sample = tuple[str, str, str]


def read_samples(path: Path) -> list[Sample]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.reader(stream, strict=True)
        if next(reader, None) != list(COLUMNS):
            raise ValueError(f"{path}: expected columns {', '.join(COLUMNS)}")
        samples = []
        for row in reader:
            if len(row) != len(COLUMNS):
                raise ValueError(f"{path}:{reader.line_num}: expected three fields")
            image_id, image, matte = row
            samples.append((image_id, image, matte))
    return samples


def unique_candidates(samples: list[Sample]) -> set[Sample]:
    ids = Counter(image_id.strip() for image_id, _, _ in samples)
    images = Counter(image for _, image, _ in samples)
    mattes = Counter(matte for _, _, matte in samples if matte)
    return {
        (image_id, image, matte)
        for image_id, image, matte in samples
        if image_id.strip()
        and ids[image_id.strip()] == images[image] == 1
        and (not matte or mattes[matte] == 1)
    }


def raw_file(root: Path, dataset: str, value: str) -> Path:
    relative = Path(value)
    raw_dir = root / dataset / "raw"
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Expected a dataset-relative path: {value}")
    path = safe_file(root, value)
    if not path.is_relative_to(raw_dir):
        raise ValueError(f"File outside {raw_dir}: {value}")
    return path


def validate_sample(root: Path, dataset: str, sample: Sample) -> set[Path]:
    _, image, matte = sample
    image_path = raw_file(root, dataset, image)
    info, problems = image_info(image_path)
    if problems:
        raise ValueError(f"{image}: {', '.join(problems)}")
    if dataset == "lfw":
        if matte:
            raise ValueError(f"Unexpected matte for LFW image: {image}")
        return {image_path}

    matte_path = raw_file(root, dataset, matte)
    if matte_path == image_path:
        raise ValueError(f"Image and matte refer to the same file: {image}")
    matte_info, problems = image_info(matte_path, mask=True)
    # Constant mattes are accepted by the dataset validator.
    errors = set(problems) - {"constant_mask"}
    if errors:
        raise ValueError(f"{matte}: {', '.join(sorted(errors))}")
    if (info["width"], info["height"]) != (matte_info["width"], matte_info["height"]):
        raise ValueError(f"Image and matte dimensions differ: {image}, {matte}")
    return {image_path, matte_path}


def select_samples(root: Path, dataset: str, candidates: set[Sample]) -> list[Sample]:
    # Canonical order keeps the selection independent of manifest row ordering.
    shuffled = sorted(candidates)
    random.Random(SEED).shuffle(shuffled)
    selected = []
    used_paths: set[Path] = set()
    for sample in shuffled:
        try:
            paths = validate_sample(root, dataset, sample)
            if paths & used_paths:
                raise ValueError("File already used by another selected sample")
        except (OSError, ValueError, Image.DecompressionBombError) as exc:
            print(f"{dataset}: skipping {sample[0]}: {exc}", file=sys.stderr)
            continue
        selected.append(sample)
        used_paths.update(paths)
        if len(selected) == SAMPLE_COUNT:
            return selected
    raise ValueError(
        f"{dataset}: found only {len(selected)} of {SAMPLE_COUNT} valid samples"
    )


def write_samples(path: Path, samples: list[Sample]) -> None:
    # Replace only after the complete CSV has been written.
    with NamedTemporaryFile(
        mode="w", dir=path.parent, newline="", encoding="utf-8", delete=False
    ) as stream:
        temporary = Path(stream.name)
        try:
            writer = csv.writer(stream)
            writer.writerow(COLUMNS)
            writer.writerows(samples)
            stream.close()
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)


def prepare_samples(root: Path, dataset: str, recreate: bool) -> None:
    processed = root / dataset / "processed"
    if processed.resolve() != processed:
        raise ValueError(f"Expected a regular processed directory: {processed}")
    output = processed / "test_samples.csv"
    candidates = unique_candidates(read_samples(processed / "manifest.csv"))
    if output.exists() and not recreate:
        saved = read_samples(output)
        if len(saved) != SAMPLE_COUNT or len(set(saved)) != SAMPLE_COUNT:
            raise ValueError(f"{output}: expected {SAMPLE_COUNT} unique samples")
        used_paths: set[Path] = set()
        for sample in saved:
            if sample not in candidates:
                raise ValueError(f"{output}: sample differs from manifest: {sample[0]}")
            paths = validate_sample(root, dataset, sample)
            if paths & used_paths:
                raise ValueError(f"{output}: duplicate file for sample {sample[0]}")
            used_paths.update(paths)
        print(f"{dataset}: reused and verified {len(saved)} samples in {output}")
        return

    selected = select_samples(root, dataset, candidates)
    write_samples(output, selected)
    print(f"{dataset}: wrote {len(selected)} samples to {output} (seed {SEED})")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "datasets",
        help="Dataset directory (default: <repository>/datasets)",
    )
    parser.add_argument("--dataset", choices=("all", *DATASETS), default="all")
    parser.add_argument(
        "--recreate", action="store_true", help="Replace existing sample manifests"
    )
    args = parser.parse_args()
    root = args.root.resolve()
    datasets = DATASETS if args.dataset == "all" else (args.dataset,)
    failed = False
    for dataset in datasets:
        try:
            prepare_samples(root, dataset, args.recreate)
        except (OSError, ValueError, csv.Error, Image.DecompressionBombError) as exc:
            print(f"{dataset}: {exc}", file=sys.stderr)
            failed = True
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
