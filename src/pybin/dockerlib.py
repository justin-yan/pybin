"""
Docker image building for binary tools.

Creates minimal Docker images using multi-stage builds with scratch as the final base.
Supports multi-platform builds (linux/amd64, linux/arm64) via docker buildx.
"""

import subprocess
import tempfile
from pathlib import Path

from pybin.config import ToolConfig

# Map symbolic platform names to Docker architecture
DOCKER_ARCH_MAP = {
    "linux_arm": "arm64",
    "linux_x86": "amd64",
    "linux_gnu_arm": "arm64",
    "linux_gnu_x86": "amd64",
    "linux_musl_arm": "arm64",
    "linux_musl_x86": "amd64",
}

DOCKERFILE_TEMPLATE = """\
FROM ubuntu:jammy AS build

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \\
    wget \\
    ca-certificates \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

ARG TARGETARCH
ARG DOWNLOAD_URL_AMD64
ARG DOWNLOAD_URL_ARM64
ARG BINARY_NAME
ARG COMPRESSION_AMD64
ARG COMPRESSION_ARM64

WORKDIR /build

RUN set -ex; \\
    if [ "$TARGETARCH" = "amd64" ]; then \\
        URL="$DOWNLOAD_URL_AMD64"; \\
        COMPRESSION="$COMPRESSION_AMD64"; \\
    else \\
        URL="$DOWNLOAD_URL_ARM64"; \\
        COMPRESSION="$COMPRESSION_ARM64"; \\
    fi; \\
    wget -q "$URL" -O archive; \\
    if [ "$COMPRESSION" = "gz" ]; then \\
        tar xzf archive; \\
    elif [ "$COMPRESSION" = "bz2" ]; then \\
        tar xjf archive; \\
    elif [ "$COMPRESSION" = "zip" ]; then \\
        apt-get update && apt-get install -y --no-install-recommends unzip && rm -rf /var/lib/apt/lists/*; \\
        unzip -q archive; \\
    else \\
        mv archive "$BINARY_NAME"; \\
    fi; \\
    find . -type f -name "$BINARY_NAME" -exec mv {{}} /build/binary \\; 2>/dev/null || true; \\
    if [ ! -f /build/binary ]; then \\
        ARCHIVE_NAME=$(basename "$URL" | sed 's/\\.[^.]*$//; s/\\.[^.]*$//'); \\
        find . -type f -name "$ARCHIVE_NAME" -exec mv {{}} /build/binary \\; 2>/dev/null || true; \\
    fi; \\
    if [ ! -f /build/binary ]; then \\
        FIRST_EXEC=$(find . -type f -executable | head -1); \\
        if [ -n "$FIRST_EXEC" ]; then mv "$FIRST_EXEC" /build/binary; fi; \\
    fi; \\
    chmod +x /build/binary

FROM scratch
ARG BINARY_NAME
COPY --from=build /build/binary /bin/{binary_name}
"""


def get_compression_mode(url: str) -> str:
    """Determine compression mode from URL."""
    if url.endswith('.tar.gz') or url.endswith('.tgz'):
        return 'gz'
    elif url.endswith('.tar.bz2'):
        return 'bz2'
    elif url.endswith('.zip'):
        return 'zip'
    return 'none'


def get_docker_targets(config: ToolConfig) -> dict[str, str]:
    """
    Extract Docker-compatible targets from config.

    Returns a dict mapping Docker arch (amd64/arm64) to download URL.
    """
    docker_targets = {}

    for target, platform_name in config.targets.items():
        docker_arch = DOCKER_ARCH_MAP.get(platform_name)
        if docker_arch is None:
            continue  # Skip non-Linux targets (macOS)

        url = config.url_template.format(
            repo=config.upstream_repo,
            version=config.version,
            name=config.name,
            target=target,
        )
        # Prefer musl builds for Docker (static linking)
        # If we already have this arch, only replace if current is musl
        if docker_arch in docker_targets:
            if 'musl' in target:
                docker_targets[docker_arch] = url
        else:
            docker_targets[docker_arch] = url

    return docker_targets


def generate_dockerfile(config: ToolConfig) -> str:
    """Generate a Dockerfile for the given tool config."""
    return DOCKERFILE_TEMPLATE.format(binary_name=config.name)


def build_docker_image(
    config: ToolConfig,
    registry: str = "ghcr.io/justin-yan/pybin",
    push: bool = False,
    load: bool = True,
) -> None:
    """
    Build a multi-platform Docker image for the tool.

    Args:
        config: Tool configuration
        registry: Container registry prefix
        push: Whether to push to registry
        load: Whether to load into local Docker (only works for single-platform)
    """
    docker_targets = get_docker_targets(config)

    if not docker_targets:
        print(f"No Linux targets found for {config.name}, skipping Docker build")
        return

    platforms = list(docker_targets.keys())
    platform_str = ",".join(f"linux/{arch}" for arch in platforms)

    image_name = f"{registry}/{config.name}"
    tags = [
        f"{image_name}:{config.pypi_version}",
        f"{image_name}:latest",
    ]

    # Build args
    build_args = [
        f"BINARY_NAME={config.name}",
    ]

    if "amd64" in docker_targets:
        url = docker_targets["amd64"]
        build_args.append(f"DOWNLOAD_URL_AMD64={url}")
        build_args.append(f"COMPRESSION_AMD64={get_compression_mode(url)}")

    if "arm64" in docker_targets:
        url = docker_targets["arm64"]
        build_args.append(f"DOWNLOAD_URL_ARM64={url}")
        build_args.append(f"COMPRESSION_ARM64={get_compression_mode(url)}")

    # Generate Dockerfile and build
    with tempfile.TemporaryDirectory() as tmpdir:
        dockerfile_path = Path(tmpdir) / "Dockerfile"
        dockerfile_path.write_text(generate_dockerfile(config))

        cmd = [
            "docker", "buildx", "build",
            "--platform", platform_str,
            "-f", str(dockerfile_path),
        ]

        for tag in tags:
            cmd.extend(["-t", tag])

        for arg in build_args:
            cmd.extend(["--build-arg", arg])

        if push:
            cmd.append("--push")
        elif load and len(platforms) == 1:
            # --load only works with single platform
            cmd.append("--load")

        cmd.append(tmpdir)

        print(f"Building Docker image for {config.name}")
        print(f"  Platforms: {platform_str}")
        print(f"  Tags: {', '.join(tags)}")

        subprocess.run(cmd, check=True)


def build_docker_image_from_config(config: ToolConfig, push: bool = False) -> None:
    """Build Docker image from a ToolConfig."""
    build_docker_image(config, push=push)
