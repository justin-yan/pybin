import io
import tarfile

from pybin.format.tar import TarUnpacker


def test_extracts_binary_from_compressed_tar() -> None:
    distribution = io.BytesIO()
    with tarfile.open(fileobj=distribution, mode="w:gz") as archive:
        content = b"executable"
        member = tarfile.TarInfo("package/example-tool")
        member.size = len(content)
        archive.addfile(member, io.BytesIO(content))

    assert TarUnpacker(extract_spec="example-tool")(distribution.getvalue()) == b"executable"
