import argparse
import sys
from pathlib import Path

from pybin.config import load_config
from pybin.dockerlib import build_docker_image_from_config


def main():
    parser = argparse.ArgumentParser(
        description="Build Docker image from tool configuration"
    )
    parser.add_argument(
        "config",
        type=Path,
        help="Path to tool YAML configuration file",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push image to registry after building",
    )

    args = parser.parse_args()

    if not args.config.exists():
        print(f"Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)

    config = load_config(args.config)
    print(f"Building Docker image for {config.name} v{config.pypi_version}")
    build_docker_image_from_config(config, push=args.push)


if __name__ == "__main__":
    main()
