import subprocess
import sys
from email.parser import BytesParser
from io import BytesIO
from pathlib import Path
from platform import machine
from zipfile import ZipFile

import pytest

from pybin.format.wheel import WheelPacker
from pybin.types import Architecture, Binary, Platform


@pytest.mark.parametrize(
    ("platform", "architecture", "platform_tag", "script_name", "create_system"),
    [
        (Platform.LINUX, Architecture.X86_64, "manylinux2014_x86_64.musllinux_1_1_x86_64", "example-tool", 3),
        (Platform.LINUX, Architecture.ARM64, "manylinux2014_aarch64.musllinux_1_1_aarch64", "example-tool", 3),
        (Platform.MACOS, Architecture.X86_64, "macosx_10_9_x86_64", "example-tool", 3),
        (Platform.MACOS, Architecture.ARM64, "macosx_11_0_arm64", "example-tool", 3),
        (Platform.WINDOWS, Architecture.X86_64, "win_amd64", "example-tool.exe", 0),
    ],
)
def test_packs_platform_binary(
    platform: Platform,
    architecture: Architecture,
    platform_tag: str,
    script_name: str,
    create_system: int,
) -> None:
    packer = WheelPacker(
        name="example-tool",
        version="1.2.3",
        license="MIT",
        upstream_url="https://github.com/example/tool",
    )
    binary = Binary(content=b"executable", architecture=architecture, platform=platform)

    assert packer.filename(binary) == f"example_tool_bin-1.2.3-py3-none-{platform_tag}.whl"
    with ZipFile(BytesIO(packer(binary))) as wheel:
        script = wheel.getinfo(f"example_tool_bin-1.2.3.data/scripts/{script_name}")
        assert wheel.read(script) == b"executable"
        assert script.create_system == create_system
        if platform is not Platform.WINDOWS:
            assert script.external_attr >> 16 == 0o100777

        wheel_metadata = BytesParser().parsebytes(wheel.read("example_tool_bin-1.2.3.dist-info/WHEEL"))
        assert wheel_metadata["Tag"] == f"py3-none-{platform_tag}"


def test_packs_distribution_metadata() -> None:
    packer = WheelPacker(
        name="example-tool",
        version="1.2.3",
        license="MIT",
        upstream_url="https://github.com/example/tool",
    )
    binary = Binary(content=b"executable", architecture=Architecture.X86_64, platform=Platform.LINUX)

    with ZipFile(BytesIO(packer(binary))) as wheel:
        assert wheel.testzip() is None
        metadata = BytesParser().parsebytes(wheel.read("example_tool_bin-1.2.3.dist-info/METADATA"))
        assert metadata["Name"] == "example-tool-bin"
        assert metadata["Version"] == "1.2.3"
        assert metadata["License"] == "MIT"
        assert metadata["Summary"] == "A thin wrapper to distribute https://github.com/example/tool via pip."
        assert "example_tool_bin-1.2.3.dist-info/RECORD" in wheel.namelist()


@pytest.mark.skipif(sys.platform != "linux" or machine() != "x86_64", reason="requires Linux x86-64")
def test_installs_linux_x86_64_wheel_with_uv(tmp_path: Path) -> None:
    packer = WheelPacker(
        name="example-tool",
        version="1.2.3",
        license="MIT",
        upstream_url="https://github.com/example/tool",
    )
    binary = Binary(
        content=b"#!/bin/sh\nprintf 'installed successfully\\n'\n",
        architecture=Architecture.X86_64,
        platform=Platform.LINUX,
    )
    wheel_path = tmp_path / packer.filename(binary)
    wheel_path.write_bytes(packer(binary))
    environment = tmp_path / "environment"

    subprocess.run(["uv", "venv", "--python", sys.executable, environment], check=True, capture_output=True, text=True)
    subprocess.run(
        ["uv", "pip", "install", "--python", environment / "bin/python", wheel_path],
        check=True,
        capture_output=True,
        text=True,
    )

    command = environment / "bin/example-tool"
    assert command.read_bytes() == binary.content
    assert subprocess.run([command], check=True, capture_output=True, text=True).stdout == "installed successfully\n"
