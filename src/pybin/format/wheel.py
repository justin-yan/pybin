from dataclasses import dataclass
from email.message import EmailMessage
from email.policy import EmailPolicy
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipInfo

from wheel.wheelfile import WheelFile

from pybin.platform_tags import (
    LINUX_ARM,
    LINUX_X86,
    MACOS_ARM,
    MACOS_X86,
    WIN_X86,
)
from pybin.types import Architecture, Binary, Platform


def _message(headers: dict[str, str], payload: str | None = None) -> bytes:
    message = EmailMessage(policy=EmailPolicy(max_line_length=0, utf8=True))
    for name, value in headers.items():
        message[name] = value
    if payload:
        message.set_payload(payload)
    return bytes(message)


@dataclass(frozen=True)
class WheelPacker:
    name: str
    version: str
    license: str
    upstream_url: str

    def _platform_tag(self, binary: Binary) -> str:
        _BINARY_TARGET_TO_WHEEL_TAG: dict[tuple[Platform, Architecture], str] = {
            (Platform.LINUX, Architecture.X86_64): LINUX_X86,
            (Platform.LINUX, Architecture.ARM64): LINUX_ARM,
            (Platform.MACOS, Architecture.X86_64): MACOS_X86,
            (Platform.MACOS, Architecture.ARM64): MACOS_ARM,
            (Platform.WINDOWS, Architecture.X86_64): WIN_X86,
        }

        try:
            return _BINARY_TARGET_TO_WHEEL_TAG[(binary.platform, binary.architecture)]
        except KeyError:
            raise ValueError(f"Unsupported wheel target: {binary.platform.value}/{binary.architecture.value}") from None

    def filename(self, binary: Binary) -> str:
        distribution_name = f"{self.name}_bin".replace("-", "_")
        return f"{distribution_name}-{self.version}-py3-none-{self._platform_tag(binary)}.whl"

    def __call__(self, binary: Binary) -> bytes:
        platform_tag = self._platform_tag(binary)
        distribution_name = f"{self.name}_bin".replace("-", "_")
        pypi_distribution_name = f"{self.name}-bin"
        tag = f"py3-none-{platform_tag}"
        dist_info = f"{distribution_name}-{self.version}.dist-info"
        data_dir = f"{distribution_name}-{self.version}.data"
        script_name = f"{self.name}.exe" if binary.platform is Platform.WINDOWS else self.name

        script = ZipInfo(f"{data_dir}/scripts/{script_name}", (2023, 12, 1, 0, 0, 0))
        script.compress_type = ZIP_DEFLATED
        if binary.platform is Platform.WINDOWS:
            script.create_system = 0
        else:
            script.create_system = 3
            script.external_attr = 0o100777 << 16

        metadata = _message(
            {
                "Metadata-Version": "2.1",
                "Name": pypi_distribution_name,
                "Version": self.version,
                "Summary": f"A thin wrapper to distribute {self.upstream_url} via pip.",
                "Description-Content-Type": "text/markdown",
                "License": self.license,
                "Requires-Python": ">=3.7",
                "Project-URL": "Repository, https://github.com/justin-yan/pybin",
            },
            f"""# {self.name}-bin

This project is part of the [pybin family of packages](https://github.com/justin-yan/pybin/tree/main/tools), which are generally
permissively-licensed binary tools that have been re-packaged to be distributable via python's PyPI infrastructure using
`pip install $TOOLNAME-bin`.

This is *not* affiliated with the upstream project found at {self.upstream_url}, and is merely a repackaging of their releases for installation
through PyPI. If the upstream project wants to officially release their tool on PyPI, please reach out and we will transfer the project
ownership over.

We attempt to reflect the license of the upstream tool on the releases in PyPI, but double-check at the upstream before use.

## Packaging Details

This project was inspired by how [Maturin packages rust binaries](https://www.maturin.rs/bindings#bin). The key observation is that in
the wheel format, the [distribution-1.0.data/scripts/ directory is copied to bin][w], which means we can leverage this to seamlessly copy
binaries onto a user's PATH. Combined with Python's platform-specific wheels, this allows us to somewhat use pip as a "cross-platform
package manager" for distributing single-binary CLI applications.

[w]: https://packaging.python.org/en/latest/specifications/binary-distribution-format/#installing-a-wheel-distribution-1-0-py32-none-any-whl""",
        )
        wheel_metadata = _message(
            {
                "Wheel-Version": "1.0",
                "Generator": f"{distribution_name} build.py",
                "Root-Is-Purelib": "false",
                "Tag": tag,
            }
        )

        with TemporaryDirectory() as directory:
            wheel_path = Path(directory) / self.filename(binary)
            with WheelFile(wheel_path, "w") as wheel:
                wheel.writestr(script, binary.content)
                wheel.writestr(f"{dist_info}/METADATA", metadata)
                wheel.writestr(f"{dist_info}/WHEEL", wheel_metadata)
            return wheel_path.read_bytes()
