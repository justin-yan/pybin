import io
import os
import tarfile
from pathlib import Path
from zipfile import ZipFile

import pytest

from pybin.buildlib import convert_archive_to_wheel, identify_binary_file


def _make_tar_gz(binary_name: str, binary_content: bytes) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(mode="w:gz", fileobj=buf) as tar:
        info = tarfile.TarInfo(name=f"subdir/{binary_name}")
        info.size = len(binary_content)
        tar.addfile(info, io.BytesIO(binary_content))
    return buf.getvalue()


def _make_zip(binary_name: str, binary_content: bytes) -> bytes:
    buf = io.BytesIO()
    with ZipFile(buf, "w") as zf:
        zf.writestr(f"subdir/{binary_name}", binary_content)
    return buf.getvalue()


FAKE_BINARY = b"\x00" * 2_000_000  # 2 MB, above the 1 MB heuristic threshold


class TestIdentifyBinaryFile:
    def test_exact_name_match(self) -> None:
        assert identify_binary_file("temporal", "temporal", "https://example.com/temporal_1.0.tar.gz")

    def test_url_basename_match(self) -> None:
        url = "https://github.com/org/repo/releases/download/v1.0/codex-x86_64-unknown-linux-gnu.tar.gz"
        assert identify_binary_file("codex-x86_64-unknown-linux-gnu", "codex", url)

    def test_no_match(self) -> None:
        assert not identify_binary_file("README.md", "temporal", "https://example.com/temporal_1.0.tar.gz")


class TestConvertArchiveToWheel:
    def test_hyphenated_name_produces_valid_wheel_filename(self, tmp_path: Path) -> None:
        archive = _make_tar_gz("temporal-test-server", FAKE_BINARY)
        orig_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = convert_archive_to_wheel(
                name="temporal-test-server",
                pypi_version="1.33.0",
                archive=archive,
                platform_tag="macosx_11_0_arm64",
                upstream_url="https://github.com/temporalio/sdk-java",
                summary="test",
                license="Apache-2.0",
                compression_mode="gz",
                download_url="https://example.com/temporal-test-server_1.33.0_macOS_arm64.tar.gz",
            )
            filename = os.path.basename(result)
            # Wheel filenames must have exactly 5 dash-separated components: name-ver-py-abi-plat
            assert filename.count("-") == 4, f"Wheel filename has wrong number of components: {filename}"
            assert filename.startswith("temporal_test_server_bin-")
        finally:
            os.chdir(orig_cwd)

    def test_simple_name_produces_valid_wheel_filename(self, tmp_path: Path) -> None:
        archive = _make_tar_gz("temporal", FAKE_BINARY)
        orig_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = convert_archive_to_wheel(
                name="temporal",
                pypi_version="1.6.2",
                archive=archive,
                platform_tag="macosx_11_0_arm64",
                upstream_url="https://github.com/temporalio/cli",
                summary="test",
                license="MIT",
                compression_mode="gz",
                download_url="https://example.com/temporal_1.6.2_darwin_arm64.tar.gz",
            )
            filename = os.path.basename(result)
            assert filename.count("-") == 4
            assert filename.startswith("temporal_bin-")
        finally:
            os.chdir(orig_cwd)

    def test_zip_archive_extracts_binary(self, tmp_path: Path) -> None:
        archive = _make_zip("mytool", FAKE_BINARY)
        orig_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = convert_archive_to_wheel(
                name="mytool",
                pypi_version="0.1.0",
                archive=archive,
                platform_tag="macosx_11_0_arm64",
                upstream_url="https://github.com/org/mytool",
                summary="test",
                license="MIT",
                compression_mode="zip",
                download_url="https://example.com/mytool_0.1.0.zip",
            )
            assert os.path.exists(result)
        finally:
            os.chdir(orig_cwd)

    def test_raises_when_binary_not_found(self, tmp_path: Path) -> None:
        archive = _make_tar_gz("wrong-name", FAKE_BINARY)
        orig_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            with pytest.raises(AssertionError, match="Failed to identify a binary"):
                convert_archive_to_wheel(
                    name="mytool",
                    pypi_version="0.1.0",
                    archive=archive,
                    platform_tag="macosx_11_0_arm64",
                    upstream_url="https://github.com/org/mytool",
                    summary="test",
                    license="MIT",
                    compression_mode="gz",
                    download_url="https://example.com/mytool_0.1.0.tar.gz",
                )
        finally:
            os.chdir(orig_cwd)
