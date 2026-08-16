import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from pybin.types import Architecture, Binary, Platform, Release


@dataclass(frozen=True)
class GHCRReleaseTarget:
    repository: str

    @classmethod
    def from_config(cls, config: dict[str, object]) -> "GHCRReleaseTarget":
        return cls(repository=str(config["repository"]))

    def _repository(self, release: Release) -> str:
        return self.repository.format(name=release.name)

    def _architecture(self, binary: Binary) -> str:
        return {
            Architecture.X86_64: "amd64",
            Architecture.ARM64: "arm64",
        }[binary.architecture]

    def _tag(self, release: Release, binary: Binary) -> str:
        return f"{self._repository(release)}:{release.version}-{self._architecture(binary)}"

    def _linux_binaries(self, release: Release) -> list[Binary]:
        return [binary for binary in release.binaries if binary.platform is Platform.LINUX]

    def build(self, release: Release) -> None:
        destination = f"/{release.name}"
        dockerfile = "\n".join(
            (
                "FROM scratch",
                f"COPY --chmod=755 {json.dumps(['binary', destination])}",
                f"ENTRYPOINT {json.dumps([destination])}",
            )
        )

        for binary in self._linux_binaries(release):
            with TemporaryDirectory() as context:
                Path(context, "binary").write_bytes(binary.content)
                subprocess.run(
                    [
                        "docker",
                        "buildx",
                        "build",
                        "--file",
                        "-",
                        "--load",
                        "--platform",
                        f"linux/{self._architecture(binary)}",
                        "--tag",
                        self._tag(release, binary),
                        "--label",
                        f"org.opencontainers.image.source={release.upstream_url}",
                        context,
                    ],
                    check=True,
                    input=dockerfile,
                    text=True,
                )

    def push(self, release: Release) -> None:
        self.build(release)
        tags = [self._tag(release, binary) for binary in self._linux_binaries(release)]
        for tag in tags:
            subprocess.run(["docker", "push", tag], check=True)

        if tags:
            subprocess.run(
                [
                    "docker",
                    "buildx",
                    "imagetools",
                    "create",
                    "--tag",
                    f"{self._repository(release)}:{release.version}",
                    *tags,
                ],
                check=True,
            )
