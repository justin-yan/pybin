import sys
from pathlib import Path

from pybin.config import load_all_configs
from pybin.update import (
    extract_version,
    get_latest_tag,
    get_latest_version,
    update_yaml_version,
)


def main(config_dir: Path) -> None:
    for config in load_all_configs(config_dir):
        try:
            if config.version_strategy == "raw_tag":
                tag = get_latest_tag(config.upstream_repo)
                new_version = tag
                new_pypi_version = extract_version(tag)
            else:
                new_version = get_latest_version(config.upstream_repo)
                new_pypi_version = new_version
        except Exception as e:
            print(f"Skipping {config.name}: {e}")
            continue

        if new_version == config.version:
            print(f"{config.name} is already up to date")
            continue

        yaml_path = config_dir / f"{config.name}.yaml"
        update_yaml_version(
            yaml_path,
            config.version,
            new_version,
            config.pypi_version,
            new_pypi_version,
        )
        print(f"{config.name} {config.version} -> {new_version}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/update.py <config_dir>", file=sys.stderr)
        sys.exit(1)
    main(Path(sys.argv[1]))
