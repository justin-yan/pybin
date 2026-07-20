from pathlib import PurePosixPath

import pytest

from pybin.format._archive import select_archive_member


def test_selects_member_by_filename() -> None:
    members = [PurePosixPath("package/README.md"), PurePosixPath("package/example-tool")]

    assert select_archive_member(members, "example-tool") == PurePosixPath("package/example-tool")


def test_selects_only_member_when_filename_differs() -> None:
    members = [PurePosixPath("example-tool-x86_64-unknown-linux-gnu")]

    assert select_archive_member(members, "example-tool") == members[0]


def test_prefers_match_in_bin_directory() -> None:
    members = [PurePosixPath("package/example-tool"), PurePosixPath("package/bin/example-tool")]

    assert select_archive_member(members, "example-tool") == PurePosixPath("package/bin/example-tool")


def test_rejects_archive_without_matching_member() -> None:
    members = [PurePosixPath("README.md"), PurePosixPath("LICENSE")]

    with pytest.raises(ValueError, match="No archive member matches 'example-tool'"):
        select_archive_member(members, "example-tool")
