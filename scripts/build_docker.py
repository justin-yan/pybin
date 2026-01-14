import argparse
import sys
from pathlib import Path

from pybin.config import load_config
from pybin.dockerlib import build_docker_images_from_config, push_docker_images


def main():
    parser = argparse.ArgumentParser(
        description="Build Docker images for a tool from YAML config"
    )
    parser.add_argument("config", type=Path, help="Path to the tool's YAML config file")
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push images to registry and create multi-arch manifest",
    )
    parser.add_argument(
        "--registry",
        default="ghcr.io/justin-yan/pybin",
        help="Container registry to use (default: ghcr.io/justin-yan/pybin)",
    )

    args = parser.parse_args()

    if not args.config.exists():
        print(f"Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)

    config = load_config(args.config)
    print(f"Building Docker images for {config.name} v{config.pypi_version}")

    if args.push:
        push_docker_images(config, registry=args.registry)
    else:
        tags = build_docker_images_from_config(config, registry=args.registry)
        print(f"Built images: {', '.join(tags)}")


if __name__ == "__main__":
    main()
