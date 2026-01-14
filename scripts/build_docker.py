import argparse
import sys
from pathlib import Path

from pybin.config import load_config
from pybin.dockerlib import build_docker_image


def main():
    parser = argparse.ArgumentParser(description="Build Docker image for a pybin tool")
    parser.add_argument("config", type=Path, help="Path to tool config YAML file")
    parser.add_argument(
        "--push", action="store_true", help="Push image to registry after building"
    )
    args = parser.parse_args()

    if not args.config.exists():
        print(f"Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)

    config = load_config(args.config)
    print(f"Building Docker image for {config.name} v{config.version}")

    image_tag = build_docker_image(config, push=args.push)
    print(f"Built image: {image_tag}")


if __name__ == "__main__":
    main()
