import subprocess
import tempfile
from pathlib import Path

from pybin.config import ToolConfig, DOCKER_PLATFORM_MAP


def get_extraction_command(compression_mode: str) -> str:
    """Return the shell command to extract an archive based on compression type."""
    if compression_mode == "gz":
        return "tar xzf archive"
    elif compression_mode == "bz2":
        return "tar xjf archive"
    elif compression_mode == "zip":
        return "unzip -q archive"
    else:
        # No compression, binary downloaded directly
        return "mv archive binary_file"


def generate_dockerfile(
    name: str,
    download_url: str,
    compression_mode: str | None,
) -> str:
    """Generate a Dockerfile for building a minimal image with a single binary."""
    extraction_cmd = get_extraction_command(compression_mode) if compression_mode else "mv archive binary_file"

    # For archives, we need to find the binary after extraction
    if compression_mode in ["gz", "bz2", "zip"]:
        # Find the binary - most tools have a binary matching the tool name
        find_binary = f'find . -type f -name "{name}" -executable | head -1 | xargs -I {{}} mv {{}} /binary'
        # Fallback: if no executable found with exact name, look for any executable
        find_binary_fallback = f"""
        if [ ! -f /binary ]; then
            find . -type f -executable | head -1 | xargs -I {{}} mv {{}} /binary
        fi"""
    else:
        find_binary = "mv binary_file /binary"
        find_binary_fallback = ""

    dockerfile = f"""FROM ubuntu:jammy AS build

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \\
    wget \\
    ca-certificates \\
    unzip && \\
    apt-get clean && \\
    rm -rf /var/lib/apt/lists/*

WORKDIR /build
RUN wget -qO archive '{download_url}' && \\
    {extraction_cmd} && \\
    {find_binary}{find_binary_fallback} && \\
    chmod +x /binary

FROM scratch
COPY --from=build /binary /{name}
ENTRYPOINT ["/{name}"]
"""
    return dockerfile


def build_docker_image(
    name: str,
    version: str,
    download_url: str,
    docker_platform: str,
    registry: str = "ghcr.io/justin-yan/pybin",
) -> str:
    """Build a Docker image for a single platform.

    Returns the image tag that was built.
    """
    compression_mode = download_url.split(".")[-1]
    compression_mode = compression_mode if compression_mode in ["gz", "bz2", "zip"] else None

    dockerfile_content = generate_dockerfile(name, download_url, compression_mode)

    # Convert docker platform to tag suffix (linux/amd64 -> amd64)
    arch_suffix = docker_platform.split("/")[-1]
    image_tag = f"{registry}/{name}:{version}-{arch_suffix}"

    with tempfile.TemporaryDirectory() as tmpdir:
        dockerfile_path = Path(tmpdir) / "Dockerfile"
        dockerfile_path.write_text(dockerfile_content)

        cmd = [
            "docker", "buildx", "build",
            "--platform", docker_platform,
            "--tag", image_tag,
            "--load",
            "--file", str(dockerfile_path),
            tmpdir,
        ]

        print(f"Building {image_tag} for {docker_platform}...")
        subprocess.run(cmd, check=True)

    return image_tag


def build_docker_images_from_config(
    config: ToolConfig,
    registry: str = "ghcr.io/justin-yan/pybin",
) -> list[str]:
    """Build Docker images for all Linux platforms defined in the config.

    Returns a list of image tags that were built.
    """
    built_tags = []
    docker_targets = config.get_docker_targets()

    for docker_platform, (download_url, _target_name) in docker_targets.items():
        tag = build_docker_image(
            name=config.name,
            version=config.pypi_version,
            download_url=download_url,
            docker_platform=docker_platform,
            registry=registry,
        )
        built_tags.append(tag)

    return built_tags


def push_docker_images(
    config: ToolConfig,
    registry: str = "ghcr.io/justin-yan/pybin",
) -> None:
    """Push Docker images and create a multi-arch manifest.

    This builds, pushes individual platform images, and creates a manifest list.
    """
    docker_targets = config.get_docker_targets()
    platform_tags = []

    # Build and push individual platform images
    for docker_platform, (download_url, _target_name) in docker_targets.items():
        compression_mode = download_url.split(".")[-1]
        compression_mode = compression_mode if compression_mode in ["gz", "bz2", "zip"] else None

        dockerfile_content = generate_dockerfile(config.name, download_url, compression_mode)
        arch_suffix = docker_platform.split("/")[-1]
        image_tag = f"{registry}/{config.name}:{config.pypi_version}-{arch_suffix}"

        with tempfile.TemporaryDirectory() as tmpdir:
            dockerfile_path = Path(tmpdir) / "Dockerfile"
            dockerfile_path.write_text(dockerfile_content)

            cmd = [
                "docker", "buildx", "build",
                "--platform", docker_platform,
                "--tag", image_tag,
                "--push",
                "--file", str(dockerfile_path),
                tmpdir,
            ]

            print(f"Building and pushing {image_tag} for {docker_platform}...")
            subprocess.run(cmd, check=True)

        platform_tags.append(image_tag)

    # Create and push multi-arch manifest
    manifest_tag = f"{registry}/{config.name}:{config.pypi_version}"
    print(f"Creating manifest {manifest_tag}...")

    # Remove existing manifest if it exists (docker manifest create fails if it exists)
    subprocess.run(
        ["docker", "manifest", "rm", manifest_tag],
        capture_output=True,  # Suppress error if manifest doesn't exist
    )

    cmd = ["docker", "manifest", "create", manifest_tag] + platform_tags
    subprocess.run(cmd, check=True)

    cmd = ["docker", "manifest", "push", manifest_tag]
    subprocess.run(cmd, check=True)

    print(f"Successfully pushed {manifest_tag}")
