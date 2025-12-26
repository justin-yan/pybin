"""Build wheels from a YAML config file."""
import sys
from pathlib import Path

from pybin.config import load_config
from pybin.buildlib import build_wheels_from_config


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m pybin.build_from_yaml <config.yaml>", file=sys.stderr)
        sys.exit(1)

    config_path = Path(sys.argv[1])
    if not config_path.exists():
        print(f"Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    config = load_config(config_path)
    print(f"Building {config.name} v{config.pypi_version} from {config_path}")
    build_wheels_from_config(config)


if __name__ == "__main__":
    main()
