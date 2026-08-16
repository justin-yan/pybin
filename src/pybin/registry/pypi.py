import subprocess
from dataclasses import dataclass
from pathlib import Path

from pybin.format.wheel import WheelPacker
from pybin.types import Release


@dataclass(frozen=True)
class PyPIReleaseTarget:
    @classmethod
    def from_config(cls, config: dict[str, object]) -> "PyPIReleaseTarget":
        return cls()

    def _packer(self, release: Release) -> WheelPacker:
        return WheelPacker(
            name=release.name,
            version=release.version,
            license=release.license,
            upstream_url=release.upstream_url,
        )

    def _paths(self, release: Release) -> list[Path]:
        packer = self._packer(release)
        return [Path(f"{release.name}-dist") / packer.filename(binary) for binary in release.binaries]

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
            ["uv", "publish", "--trusted-publishing", "always", *(str(path) for path in paths)],
            check=True,
        )
