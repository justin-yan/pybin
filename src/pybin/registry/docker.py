import subprocess
from dataclasses import dataclass
from pathlib import Path
from platform import machine
from tempfile import TemporaryDirectory

from pybin.types import Architecture, Platform, Release

_DOCKER_ARCHITECTURES = {
    Architecture.X86_64: "amd64",
    Architecture.ARM64: "arm64",
}

_MACHINE_ARCHITECTURES = {
    "aarch64": "arm64",
    "arm64": "arm64",
    "amd64": "amd64",
    "x86_64": "amd64",
}


def generate_dockerfile(name: str) -> str:
    return f"""# syntax=docker/dockerfile:1
FROM scratch
ARG TARGETARCH
COPY --chmod=755 ${{TARGETARCH}} /{name}
"""


@dataclass(frozen=True)
class DockerReleaseBuilder:
    repository: str = "tool-{name}"
    push: bool = False

    @classmethod
    def from_config(cls, config: dict[str, object]) -> "DockerReleaseBuilder":
        return cls(
            repository=str(config.get("repository", "tool-{name}")),
            push=bool(config.get("push", False)),
        )

    def __call__(self, release: Release) -> None:
        binaries = {_DOCKER_ARCHITECTURES[binary.architecture]: binary.content for binary in release.binaries if binary.platform is Platform.LINUX}
        if not binaries:
            raise ValueError(f"Release {release.name!r} has no Linux binaries for a Docker image")

        image_tag = f"{self.repository.format(name=release.name)}:{release.version}"
        architectures = sorted(binaries) if self.push else [_MACHINE_ARCHITECTURES[machine().lower()]]
        if not self.push and architectures[0] not in binaries:
            raise ValueError(f"Release {release.name!r} has no Linux binary for the local {architectures[0]} architecture")

        with TemporaryDirectory() as context_directory:
            context = Path(context_directory)
            (context / "Dockerfile").write_text(generate_dockerfile(release.name))
            for architecture, content in binaries.items():
                (context / architecture).write_bytes(content)

            command = [
                "docker",
                "buildx",
                "build",
                "--push" if self.push else "--load",
                "--platform",
                ",".join(f"linux/{architecture}" for architecture in architectures),
                "--provenance=false",
                "--tag",
                image_tag,
            ]
            subprocess.run([*command, str(context)], check=True)
