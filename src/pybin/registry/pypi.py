from dataclasses import dataclass
from pathlib import Path

from pybin.format.wheel import WheelPacker
from pybin.types import Release


@dataclass(frozen=True)
class PyPIReleasePusher:
    upstream_url: str
    output_directory: Path | None = None

    def __call__(self, release: Release) -> None:
        output_directory = self.output_directory or Path(f"{release.name}-dist")
        output_directory.mkdir(exist_ok=True)
        packer = WheelPacker(name=release.name, version=release.version, license=release.license, upstream_url=self.upstream_url)

        for binary in release.binaries:
            (output_directory / packer.filename(binary)).write_bytes(packer(binary))
