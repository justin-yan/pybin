"""Docker image building utilities for pybin tools."""

import subprocess
import tempfile
from pathlib import Path

from pybin.config import ToolConfig
from pybin.docker_tags import DOCKER_AMD64, DOCKER_ARM64


def get_extraction_command(url: str, name: str) -> str:
    """Return shell command to extract the binary from a downloaded archive."""
    if url.endswith(".tar.gz"):
        return f'tar xzf archive && find . -name "{name}" -type f -exec mv {{}} {name} \\;'
    elif url.endswith(".tar.bz2"):
        return f'tar xjf archive && find . -name "{name}" -type f -exec mv {{}} {name} \\;'
    elif url.endswith(".zip"):
        return f'unzip -q archive && find . -name "{name}" -type f -exec mv {{}} {name} \\;'
    else:
        return f"mv archive {name}"


def generate_dockerfile(config: ToolConfig) -> str:
    """Generate a multi-arch Dockerfile for the tool."""
    docker_targets = config.get_docker_targets()

    if DOCKER_AMD64 not in docker_targets or DOCKER_ARM64 not in docker_targets:
        raise ValueError(
            f"Config for {config.name} must have both amd64 and arm64 Linux targets"
        )

    url_amd64 = docker_targets[DOCKER_AMD64]
    url_arm64 = docker_targets[DOCKER_ARM64]
    name = config.name

    extract_amd64 = get_extraction_command(url_amd64, name)
    extract_arm64 = get_extraction_command(url_arm64, name)

    # Determine if we need unzip
    needs_unzip = url_amd64.endswith(".zip") or url_arm64.endswith(".zip")
    apt_packages = "wget ca-certificates"
    if needs_unzip:
        apt_packages += " unzip"

    dockerfile = f"""# syntax=docker/dockerfile:1
FROM ubuntu:22.04 AS build-amd64
RUN apt-get update && apt-get install -y --no-install-recommends {apt_packages}
WORKDIR /build
RUN wget -q "{url_amd64}" -O archive && {extract_amd64} && chmod +x {name} && mv {name} /{name}

FROM ubuntu:22.04 AS build-arm64
RUN apt-get update && apt-get install -y --no-install-recommends {apt_packages}
WORKDIR /build
RUN wget -q "{url_arm64}" -O archive && {extract_arm64} && chmod +x {name} && mv {name} /{name}

FROM scratch AS final-amd64
COPY --from=build-amd64 /{name} /{name}

FROM scratch AS final-arm64
COPY --from=build-arm64 /{name} /{name}

FROM final-$TARGETARCH
ENTRYPOINT ["/{name}"]
"""
    return dockerfile


def build_docker_image(
    config: ToolConfig,
    registry: str = "ghcr.io",
    org: str = "justin-yan",
    push: bool = False,
) -> str:
    """Build a multi-arch Docker image for the tool.

    Returns the image tag that was built.
    """
    image_tag = f"{registry}/{org}/{config.name}:{config.version}"
    dockerfile_content = generate_dockerfile(config)

    with tempfile.TemporaryDirectory() as tmpdir:
        dockerfile_path = Path(tmpdir) / "Dockerfile"
        dockerfile_path.write_text(dockerfile_content)

        cmd = [
            "docker",
            "buildx",
            "build",
            "--platform",
            "linux/amd64,linux/arm64",
            "-t",
            image_tag,
            "-f",
            str(dockerfile_path),
        ]

        if push:
            cmd.append("--push")

        cmd.append(tmpdir)

        print(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)

    return image_tag
