import io
from dataclasses import dataclass
from pathlib import PurePosixPath
from zipfile import ZipFile

from pybin.format._archive import select_archive_member


@dataclass(frozen=True)
class ZipUnpacker:
    extract_spec: str

    def __call__(self, distribution: bytes) -> bytes:
        with ZipFile(io.BytesIO(distribution)) as archive:
            member = select_archive_member(
                [PurePosixPath(member.filename) for member in archive.infolist() if not member.is_dir()],
                self.extract_spec,
            )
            return archive.read(member.as_posix())
