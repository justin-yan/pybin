import io
from zipfile import ZipFile

from pybin.format.zip import ZipUnpacker


def test_extracts_binary_from_zip() -> None:
    distribution = io.BytesIO()
    with ZipFile(distribution, "w") as archive:
        archive.writestr("package/example-tool", b"executable")

    assert ZipUnpacker(extract_spec="example-tool")(distribution.getvalue()) == b"executable"
