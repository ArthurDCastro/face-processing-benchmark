"""Check scaffold configuration boundaries without datasets or models."""

from pathlib import Path

import pytest

from face_processing_benchmark.core.config import ConfigError, load_config

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("kind", ["datasets", "methods"])
def test_repository_examples(kind):
    config = load_config(ROOT / "configs" / f"{kind}.yaml")
    assert config == {"schema_version": 1, "kind": kind, kind: {}}


@pytest.mark.parametrize(
    "content",
    [
        "",
        "[]",
        "schema_version: true\nkind: datasets\ndatasets: {}",
        "schema_version: 2\nkind: datasets\ndatasets: {}",
        "schema_version: 1\nkind: []\ndatasets: {}",
        "schema_version: 1\nkind: methods",
        "schema_version: 1\nkind: methods\nmethods: []",
        "schema_version: 1\nkind: methods\nmethods: {unselected: {}}",
        "schema_version: 1\nkind: datasets\ndatasets: {}\nunknown: true",
        "invalid: [",
    ],
)
def test_invalid_configuration_is_rejected(tmp_path, content):
    path = tmp_path / "invalid.yaml"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(path)


def test_missing_file_has_context(tmp_path):
    path = tmp_path / "missing.yaml"
    with pytest.raises(ConfigError, match="missing.yaml"):
        load_config(path)
