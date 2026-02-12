import io
import tarfile

import pytest

from pybin.buildlib import extract_from_ar, extract_binary_from_deb, AR_MAGIC


def _make_ar_member(name: str, data: bytes) -> bytes:
    """Build a single ar archive member (header + data + padding)."""
    name_field = f"{name}/".ljust(16).encode("ascii")
    # timestamp, owner, group, mode fields (unused for our purposes)
    timestamp = b"0           "
    owner = b"0     "
    group = b"0     "
    mode = b"100644  "
    size_field = str(len(data)).ljust(10).encode("ascii")
    end_magic = b"`\n"

    header = name_field + timestamp + owner + group + mode + size_field + end_magic
    assert len(header) == 60

    result = header + data
    if len(data) % 2 != 0:
        result += b"\n"
    return result


def _make_ar_archive(*members: tuple[str, bytes]) -> bytes:
    """Build a minimal ar archive from (name, data) pairs."""
    archive = bytearray(AR_MAGIC)
    for name, data in members:
        archive.extend(_make_ar_member(name, data))
    return bytes(archive)


def _make_data_tar_gz(file_path: str, file_content: bytes) -> bytes:
    """Build a tar.gz in memory with one file."""
    buf = io.BytesIO()
    with tarfile.open(mode="w:gz", fileobj=buf) as tar:
        info = tarfile.TarInfo(name=file_path)
        info.size = len(file_content)
        tar.addfile(info, io.BytesIO(file_content))
    return buf.getvalue()


class TestExtractFromAr:
    def test_extracts_member_by_prefix(self):
        payload = b"hello world"
        archive = _make_ar_archive(
            ("debian-binary", b"2.0\n"),
            ("data.tar.gz", payload),
        )

        name, data = extract_from_ar(archive, "data.tar")

        assert name == "data.tar.gz"
        assert data == payload

    def test_raises_on_missing_member(self):
        archive = _make_ar_archive(("debian-binary", b"2.0\n"))

        with pytest.raises(ValueError, match="No member starting with"):
            extract_from_ar(archive, "data.tar")

    def test_raises_on_invalid_magic(self):
        with pytest.raises(ValueError, match="bad magic"):
            extract_from_ar(b"not an ar archive", "data.tar")


class TestExtractBinaryFromDeb:
    def test_extracts_binary_from_deb(self):
        binary_content = b"\x7fELF" + b"\x00" * 1_500_000
        data_tar = _make_data_tar_gz("usr/bin/sl", binary_content)
        deb = _make_ar_archive(
            ("debian-binary", b"2.0\n"),
            ("control.tar.gz", b"control"),
            ("data.tar.gz", data_tar),
        )

        result = extract_binary_from_deb(deb, "sl", "sapling_0.2_amd64.deb")

        assert result == binary_content

    def test_raises_when_binary_not_found(self):
        data_tar = _make_data_tar_gz("usr/bin/other", b"\x00" * 2_000_000)
        deb = _make_ar_archive(
            ("debian-binary", b"2.0\n"),
            ("data.tar.gz", data_tar),
        )

        with pytest.raises(ValueError, match="Could not find binary"):
            extract_binary_from_deb(deb, "sl", "sapling_0.2_amd64.deb")

    def test_skips_small_files(self):
        small_content = b"tiny"
        large_content = b"\x7fELF" + b"\x00" * 1_500_000
        buf = io.BytesIO()
        with tarfile.open(mode="w:gz", fileobj=buf) as tar:
            small_info = tarfile.TarInfo(name="usr/share/sl")
            small_info.size = len(small_content)
            tar.addfile(small_info, io.BytesIO(small_content))
            large_info = tarfile.TarInfo(name="usr/bin/sl")
            large_info.size = len(large_content)
            tar.addfile(large_info, io.BytesIO(large_content))
        data_tar = buf.getvalue()
        deb = _make_ar_archive(
            ("debian-binary", b"2.0\n"),
            ("data.tar.gz", data_tar),
        )

        result = extract_binary_from_deb(deb, "sl", "sapling_0.2_amd64.deb")

        assert result == large_content
