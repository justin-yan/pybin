"""Update tool versions from upstream GitHub releases."""
import sys
from pathlib import Path

from pybin.config import load_all_configs
from pybin.update import get_latest_version, update_yaml_version


def main(config_dir: Path) -> None:
    for config in load_all_configs(config_dir):
        try:
            latest_version = get_latest_version(config.upstream_repo)
        except Exception as e:
            print(f"Skipping {config.name}: {e}")
            continue

        if latest_version == config.version:
            print(f"{config.name} is already up to date")
            continue

        yaml_path = config_dir / f"{config.name}.yaml"
        update_yaml_version(yaml_path, config.version, latest_version)
        print(f"{config.name} {config.version} -> {latest_version}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/update.py <config_dir>", file=sys.stderr)
        sys.exit(1)
    main(Path(sys.argv[1]))
