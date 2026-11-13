"""Load and validate empty scaffold registrations without running benchmarks."""

import argparse
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    """A configuration cannot be read or does not match the scaffold schema."""


def load_config(path: str | Path) -> dict[str, Any]:
    """Read a YAML scaffold file; relative paths use the working directory.

    Only empty dataset or method registrations are currently supported. Entry
    validation will be added when the corresponding schemas are defined.
    """
    config_path = Path(path)
    try:
        with config_path.open(encoding="utf-8") as stream:
            config = yaml.safe_load(stream)
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ConfigError(f"Cannot read configuration '{config_path}': {exc}") from exc

    if not isinstance(config, Mapping):
        raise ConfigError("Configuration must be a YAML mapping.")
    if type(config.get("schema_version")) is not int or config["schema_version"] != 1:
        raise ConfigError("schema_version must be the integer 1.")
    kind = config.get("kind")
    if not isinstance(kind, str) or kind not in {"datasets", "methods"}:
        raise ConfigError("kind must be 'datasets' or 'methods'.")
    if set(config) != {"schema_version", "kind", kind}:
        raise ConfigError(f"Expected only schema_version, kind, and {kind} fields.")
    if not isinstance(config[kind], dict):
        raise ConfigError(f"{kind} must be a mapping.")
    if config[kind]:
        raise ConfigError(f"Populated {kind} registrations are not supported yet.")
    return dict(config)


def main(argv: Sequence[str] | None = None) -> int:
    """Validate one scaffold configuration from the terminal."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="Path to a scaffold YAML file")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
    except ConfigError as exc:
        parser.exit(2, f"Configuration error: {exc}\n")
    print(f"Valid scaffold configuration: {args.config} ({config['kind']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
