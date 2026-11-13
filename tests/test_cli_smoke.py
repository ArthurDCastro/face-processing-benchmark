"""Exercise the installed package and its thin configuration CLI."""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "entrypoint",
    [
        ["-m", "face_processing_benchmark.core.config"],
        [str(ROOT / "scripts" / "check_config.py")],
    ],
)
def test_cli_from_another_working_directory(tmp_path, entrypoint):
    result = subprocess.run(
        [sys.executable, *entrypoint, str(ROOT / "configs" / "datasets.yaml")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Valid scaffold configuration" in result.stdout
    assert list(tmp_path.iterdir()) == []


def test_cli_reports_invalid_configuration(tmp_path):
    path = tmp_path / "invalid.yaml"
    path.write_text("[]", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "face_processing_benchmark.core.config", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "Configuration error" in result.stderr
    assert "Traceback" not in result.stderr
