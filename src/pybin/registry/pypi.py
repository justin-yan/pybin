import subprocess
from dataclasses import dataclass
from pathlib import Path

from pybin.format.wheel import WheelPacker
from pybin.types import Release


@dataclass(frozen=True)
class PyPIReleaseTarget:
    output_directory: Path | None = None
    trusted_publishing: str = "always"

    @classmethod
    def from_config(cls, config: dict[str, object]) -> "PyPIReleaseTarget":
        output_directory = config.get("output_directory")
        return cls(
            output_directory=Path(str(output_directory)) if output_directory is not None else None,
            trusted_publishing=str(config.get("trusted_publishing", "always")),
        )

    def _packer(self, release: Release) -> WheelPacker:
        return WheelPacker(
            name=release.name,
            version=release.version,
            license=release.license,
            upstream_url=release.upstream_url,
        )

    def _paths(self, release: Release) -> list[Path]:
        output_directory = self.output_directory or Path(f"{release.name}-dist")
        packer = self._packer(release)
        return [output_directory / packer.filename(binary) for binary in release.binaries]

    def build(self, release: Release) -> None:
        packer = self._packer(release)
        for path, binary in zip(self._paths(release), release.binaries, strict=True):
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(packer(binary))

    def push(self, release: Release) -> None:
        self.build(release)
        paths = self._paths(release)
        if not paths:
            return

        subprocess.run(
            ["uv", "publish", "--trusted-publishing", self.trusted_publishing, *(str(path) for path in paths)],
            check=True,
        )


PyPIReleasePusher = PyPIReleaseTarget
