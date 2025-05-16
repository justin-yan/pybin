import io
import os
import tarfile
import urllib.request
from email.message import EmailMessage
from pathlib import Path
from typing import Optional
from zipfile import ZipInfo, ZIP_DEFLATED, ZipFile

from wheel.wheelfile import WheelFile


def make_message(headers, payload=None):
    msg = EmailMessage()
    for name, value in headers.items():
        if isinstance(value, list):
            for value_part in value:
                msg[name] = value_part
        else:
            msg[name] = value
    if payload:
        msg.set_payload(payload)
    return msg


def write_wheel_file(filename, contents):
    with WheelFile(filename, 'w') as wheel:
        for member_info, member_source in contents.items():
            wheel.writestr(member_info, bytes(member_source))
    return filename


def convert_archive_to_wheel(
        name: str,
        pypi_version: str,
        archive: bytes,
        platform_tag: str,
        upstream_url: str,
        summary: str,
        license: str,
        compression_mode: Optional[str],
):
    distribution_name = f'{name}_bin'  # If wheel names have a hyphen, the RECORD file is placed in the wrong .dist-info directory resulting in invalid wheels.
    pypi_distribution_name = f'{name}-bin'
    contents = {}

    # Extract the command binary
    datadir = f'{distribution_name}-{pypi_version}.data'
    zip_info = ZipInfo(f'{datadir}/scripts/{name}', (2023,12,1,0,0,0))
    zip_info.external_attr = 0o100777 << 16  # This is needed to force filetype and permissions
    zip_info.compress_type = ZIP_DEFLATED
    zip_info.create_system = 3

    if compression_mode in ['gz', 'bz2']:  # TODO: technically should check for .tar.gz, etc.
        with tarfile.open(mode=f"r:{compression_mode}", fileobj=io.BytesIO(archive)) as tar:
            for entry in tar:
                if entry.isreg():
                    if entry.name.split('/')[-1] == f"{name}":
                        source = tar.extractfile(entry).read()
                        zip_info.file_size = len(source)
                        contents[zip_info] = source
    elif compression_mode in ['zip']:
        with ZipFile(io.BytesIO(archive), 'r') as z:
            binfilename = None
            for file in z.namelist():
                if file.split("/")[-1] == name:
                    binfilename = file
                    break
            tbin = z.read(binfilename)  # TODO: error handling if file doesn't exist
            zip_info.file_size = len(tbin)
            contents[zip_info] = tbin
    else:
        zip_info.file_size = len(archive)
        contents[zip_info] = archive

    # Create distinfo
    tag = f'py3-none-{platform_tag}'
    metadata = {'Summary': summary,
                'Description-Content-Type': 'text/markdown',
                'License': license,
                'Requires-Python': '>=3.7',
                'Project-URL': f'Repository, https://github.com/justin-yan/pybin',
                }
    with open('README.md') as f:
        description = f.read()
    description = f"""# {name}-bin

This project is part of the [pybin family of packages](https://github.com/justin-yan/pybin/tree/main/src/pybin), which are generally permissively-licensed binary tools that have been re-packaged to be distributable via python's PyPI infrastructure using `pip install $TOOLNAME-bin`.

This is *not* affiliated with the upstream project found at {upstream_url}, and is merely a repackaging of their releases for installation through PyPI.  If an official installer is supported through PyPI, the corresponding package here will be deprecated.

We attempt to reflect the license of the upstream tool on the releases in PyPI, but double-check at the upstream before use.

## Packaging Details

This project was inspired by how [Maturin packages rust binaries](https://www.maturin.rs/bindings#bin).  The key observation is that in the wheel format, the [distribution-1.0.data/scripts/ directory is copied to bin](https://packaging.python.org/en/latest/specifications/binary-distribution-format/#installing-a-wheel-distribution-1-0-py32-none-any-whl), which means we can leverage this to seamlessly copy binaries onto a user's PATH.  Combined with Python's platform-specific wheels, this allows us to somehwat use pip as a "cross-platform package manager" for distributing single-binary CLI applications."""

    dist_info = f'{distribution_name}-{pypi_version}.dist-info'
    contents[f'{dist_info}/METADATA'] = make_message({
            'Metadata-Version': '2.1',
            'Name': pypi_distribution_name,
            'Version': pypi_version,
            **metadata,
        }, description)
    contents[f'{dist_info}/WHEEL'] = make_message({
            'Wheel-Version': '1.0',
            'Generator': f'{distribution_name} build.py',
            'Root-Is-Purelib': 'false',
            'Tag': tag,
        })

    wheel_name = f'{distribution_name}-{pypi_version}-{tag}.whl'
    outdir = f"{name}-dist"
    Path(outdir).mkdir(exist_ok=True)
    return write_wheel_file(os.path.join(outdir, wheel_name), contents)


def build_wheels(
        name: str,
        pypi_version: str,
        url_tag_map: dict,
        upstream_repo_url: str,
        license_name: str
):
    for url, tag in url_tag_map.items():
        with urllib.request.urlopen(url) as response:
            archive = response.read()
        compression_mode = url.split('.')[-1]
        compression_mode = compression_mode if compression_mode in ["gz", "bz2", "zip"] else None
        summary = f"A thin wrapper to distribute {upstream_repo_url} via pip."
        convert_archive_to_wheel(name, pypi_version, archive, tag, upstream_repo_url, summary, license_name, compression_mode)
