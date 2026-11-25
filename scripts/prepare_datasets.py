#!/usr/bin/env python3
"""Prepare directories, optionally download LFW, and index datasets without changing raw files."""
from __future__ import annotations
import argparse
import csv
import hashlib
import zipfile
import sys
import shutil
import tarfile
import urllib.request
from pathlib import Path

LFW_URL = 'https://ndownloader.figshare.com/files/5976015'
LFW_SHA256 = 'b47c8422c8cded889dc5a13418c4bc2abbda121092b3533a83306f90d900100a'
IMAGE_EXT = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff'}
DATASETS = ('lfw', 'ppm100', 'p3m500np')
PPM100_DRIVE_URL = 'https://drive.google.com/file/d/1JUx-EPoV9QAhQgmW0AyOen-xKQUzZia-/view?usp=sharing'
# The official link distributes the complete P3M-10k archive, NOT P3M-500-NP alone.
P3M_DRIVE_URL = 'https://drive.google.com/file/d/1odzHp2zbQApLm90HH_Cvr5b5OwJVhEQG/view?usp=sharing'



def make_dirs(root: Path) -> None:
    for name in DATASETS:
        for suffix in ('raw', 'processed'):
            (root / name / suffix).mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def download_lfw(root: Path) -> None:
    folder = root / 'lfw' / 'raw'
    archive = folder / 'lfw-funneled.tgz'
    if not archive.exists():
        print(f'Downloading LFW funneled from {LFW_URL}')
        temp = archive.with_name(archive.name + '.partial')
        try:
            with urllib.request.urlopen(LFW_URL, timeout=60) as response, temp.open('wb') as out:
                shutil.copyfileobj(response, out)
            temp.replace(archive)
        finally:
            temp.unlink(missing_ok=True)
    digest = sha256(archive)
    if digest != LFW_SHA256:
        raise RuntimeError(f'LFW checksum mismatch: {digest}. Remove the incorrect archive manually.')
    extracted = folder / 'lfw_funneled'
    if extracted.exists():
        print('LFW already extracted.')
        return
    print('Extracting verified LFW archive.')
    with tarfile.open(archive, 'r:gz') as tar:
        for member in tar.getmembers():
            # Only plain files and directories allowed. Reject traversal and special files.
            name = Path(member.name)
            if name.is_absolute() or '..' in name.parts or not (member.isfile() or member.isdir()):
                raise RuntimeError(f'Unsafe tar member: {member.name}')
            target = (folder / name).resolve()
            if not target.is_relative_to(folder.resolve()):
                raise RuntimeError(f'Unsafe extraction path: {member.name}')
        tar.extractall(folder, filter='data')
    print('LFW is ready in datasets/lfw/raw/lfw_funneled/.')


def download_drive_archive(url: str, destination: Path) -> Path:
    """Download a public Google Drive item, with a resumable local archive."""
    try:
        import gdown
    except ImportError as exc:
        raise RuntimeError(
            "Install Google Drive support: python -m pip install -e '.[dataset-downloads]'"
        ) from exc
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0:
        print(f'Using existing download: {destination}')
        return destination
    temp = destination.with_suffix(destination.suffix + '.partial')
    print(f'Downloading official dataset archive into {destination}...')
    outcome = gdown.download(url, output=str(temp), quiet=False, fuzzy=True, resume=True)
    if not outcome or not temp.exists() or temp.stat().st_size == 0:
        raise RuntimeError('Google Drive download failed or was blocked; try again later or use the official browser link.')
    # Check that we did not save a Google Drive error/HTML response.
    if not zipfile.is_zipfile(temp) and not tarfile.is_tarfile(temp):
        raise RuntimeError(f'Download is not a recognized ZIP/TAR archive: {temp}. Keep for inspection.')
    temp.replace(destination)
    return destination


def safe_archive_members(archive: Path):
    """Yield (relative name, stream opener) without trusting archive paths."""
    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as z:
            for info in z.infolist():
                if info.is_dir():
                    continue
                if (info.external_attr >> 16) & 0o170000 == 0o120000:
                    raise RuntimeError(f'Symlink in ZIP not supported: {info.filename}')
                yield info.filename, lambda info=info: z.open(info)
    elif tarfile.is_tarfile(archive):
        with tarfile.open(archive, 'r:*') as t:
            for member in t:
                if member.isdir():
                    continue
                if not member.isfile():
                    raise RuntimeError(f'Unsafe TAR member type: {member.name}')
                yield member.name, lambda member=member: t.extractfile(member)
    else:
        raise RuntimeError(f'Unsupported archive: {archive}')


def extract_dataset(archive: Path, dest: Path, only_np: bool = False) -> int:
    """Extract safely; for P3M select only the non-blurred P3M-500-NP subset."""
    count = 0
    dest.mkdir(parents=True, exist_ok=True)
    for name, get_stream in safe_archive_members(archive):
        rel = Path(name.replace('\\', '/'))
        if rel.is_absolute() or '..' in rel.parts or not rel.parts:
            raise RuntimeError(f'Unsafe archive path: {name}')
        if only_np:
            # Subset name may be written P3M-500-NP or P3M_500_NP.
            parts_normalized = [part.lower().replace('_', '-').replace(' ', '-') for part in rel.parts]
            if 'p3m-500-np' not in parts_normalized:
                continue
            pos = parts_normalized.index('p3m-500-np')
            rel = Path(*rel.parts[pos + 1:])
            if not rel.parts:
                continue
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.stat().st_size > 0:
            continue
        with get_stream() as src, target.open('wb') as out:
            shutil.copyfileobj(src, out)
        count += 1
    return count


def download_ppm100(root: Path) -> None:
    raw = root / 'ppm100' / 'raw'
    archive = download_drive_archive(PPM100_DRIVE_URL, raw / 'ppm100_original.zip')
    count = extract_dataset(archive, raw)
    print(f'PPM-100 extraction: {count} new files. Run --index and validate the pairs.')


def download_p3m500np(root: Path, acknowledge_large: bool) -> None:
    if not acknowledge_large:
        raise RuntimeError('The official link downloads the FULL P3M-10k archive, not only 500 NP images. '
                           'Re-run with --allow-full-p3m-archive to acknowledge the larger download.')
    raw = root / 'p3m500np' / 'raw'
    archive = download_drive_archive(P3M_DRIVE_URL, raw / 'p3m10k_original.zip')
    count = extract_dataset(archive, raw, only_np=True)
    if not list_images(raw):
        raise RuntimeError('P3M-500-NP not found at the expected path in the full archive. '
                           'Inspect the archive structure before attempting extraction again.')
    print(f'P3M-500-NP extraction: {count} new files (other subsets not extracted). Run --index.')


def list_images(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob('*') if p.is_file() and p.suffix.lower() in IMAGE_EXT)


def match_pair_files(raw: Path, image_folder_names: set[str], matte_folder_names: set[str]):
    images = [p for p in list_images(raw) if any(part.lower() in image_folder_names for part in p.relative_to(raw).parts[:-1])]
    mattes = [p for p in list_images(raw) if any(part.lower() in matte_folder_names for part in p.relative_to(raw).parts[:-1])]
    groups = {}
    for p in mattes:
        groups.setdefault(p.stem.lower(), []).append(p)
    matches, missing, ambiguous = [], [], []
    for p in images:
        options = groups.get(p.stem.lower(), [])
        if len(options) == 1:
            matches.append((p, options[0]))
        elif not options:
            missing.append(p)
        else:
            ambiguous.append(p)
    return matches, missing, ambiguous, len(images), len(mattes)


def index_dataset(root: Path, name: str) -> None:
    raw = root / name / 'raw'
    processed = root / name / 'processed'
    if name == 'lfw':
        images = list_images(raw / 'lfw_funneled') if (raw / 'lfw_funneled').exists() else []
        rows = [{'id': str(i).zfill(5), 'image': str(p.relative_to(root)), 'matte': ''} for i, p in enumerate(images)]
        print(f'LFW: {len(rows)} images (no face boxes or mattes in this standard release).')
    else:
        if name == 'ppm100':
            image_dirs = {'image', 'images', 'fg', 'original_image', 'original_images'}
            matte_dirs = {'matte', 'mattes', 'alpha', 'mask', 'masks'}
        else:
            image_dirs = {'original_image', 'original_images', 'image', 'images'}
            matte_dirs = {'mask', 'masks', 'matte', 'mattes', 'alpha'}
        matches, missing, ambiguous, n_images, n_mattes = match_pair_files(raw, image_dirs, matte_dirs)
        rows = [{'id': p.stem, 'image': str(p.relative_to(root)), 'matte': str(m.relative_to(root))} for p, m in matches]
        print(f'{name}: {n_images} images, {n_mattes} mattes, {len(matches)} unique pairs; missing={len(missing)}, ambiguous={len(ambiguous)}')
        if missing or ambiguous:
            issue = processed / 'pairing_issues.txt'
            issue.write_text('Missing matches:\n' + '\n'.join(str(p.relative_to(root)) for p in missing) + '\nAmbiguous matches:\n' + '\n'.join(str(p.relative_to(root)) for p in ambiguous) + '\n', encoding='utf-8')
            print(f'  See {issue}')
        if len(rows) == 0:
            print('  No pairs found. Check extracted folder names (image/ and matte/ or original_image/ and mask/).')
    target = processed / 'manifest.csv'
    with target.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=('id', 'image', 'matte'))
        writer.writeheader()
        writer.writerows(rows)
    print(f'  Manifest: {target}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('datasets'))
    parser.add_argument('--download-lfw', action='store_true')
    parser.add_argument('--download-ppm100', action='store_true')
    parser.add_argument('--download-p3m500np', action='store_true')
    parser.add_argument('--allow-full-p3m-archive', action='store_true', help='Acknowledge download of the entire official P3M-10k archive')
    parser.add_argument('--download-all', action='store_true', help='Download LFW and PPM-100; P3M-500-NP also requires --allow-full-p3m-archive')
    parser.add_argument('--index', action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    make_dirs(root)
    if args.download_lfw or args.download_all:
        download_lfw(root)
    if args.download_ppm100 or args.download_all:
        download_ppm100(root)
    if args.download_p3m500np or args.download_all:
        download_p3m500np(root, args.allow_full_p3m_archive)
    if args.index:
        for name in DATASETS:
            index_dataset(root, name)
    if not (args.download_lfw or args.download_ppm100 or args.download_p3m500np or args.download_all or args.index):
        print(f'Created dataset folders at {root}. Use --download-lfw, --download-ppm100, --download-p3m500np, and/or --index.')

if __name__ == '__main__':
    main()
