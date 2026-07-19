import io
import tarfile
from dataclasses import dataclass
from pathlib import PurePosixPath

from pybin.format._archive import select_archive_member


@dataclass(frozen=True)
class TarUnpacker:
    extract_spec: str

    def __call__(self, distribution: bytes) -> bytes:
        with tarfile.open(fileobj=io.BytesIO(distribution), mode="r:*") as archive:
            member = select_archive_member(
                [PurePosixPath(member.name) for member in archive if member.isreg()],
                self.extract_spec,
            )
            source = archive.extractfile(member.as_posix())
            assert source is not None
            return source.read()
