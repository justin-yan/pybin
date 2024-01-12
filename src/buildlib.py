import argparse
import io
import os
import tarfile
import urllib.request
from email.message import EmailMessage
from pathlib import Path
from zipfile import ZipInfo, ZIP_DEFLATED

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
        summary: str,
        license: str,
        compression_mode: str,
):
    distribution_name = f'{name}_bin'  # If wheel names have a hyphen, the RECORD file is placed in the wrong .dist-info directory resulting in invalid wheels.
    pypi_distribution_name = f'{name}-bin'
    contents = {}

    # Extract the command binary
    datadir = f'{distribution_name}-{pypi_version}.data'
    with tarfile.open(mode=f"r:{compression_mode}", fileobj=io.BytesIO(archive)) as tar:
        for entry in tar:
            if entry.isreg():
                if entry.name.split('/')[-1] == f"{name}":
                    source = tar.extractfile(entry).read()
                    zip_info = ZipInfo(f'{datadir}/scripts/{name}', (2023,12,1,0,0,0))
                    zip_info.external_attr = 0o100777 << 16  # This is needed to force filetype and permissions
                    zip_info.file_size = len(source)
                    zip_info.compress_type = ZIP_DEFLATED
                    zip_info.create_system = 3
                    contents[zip_info] = source

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
        summary: str,
        license: str,
    ):

    for url, tag in url_tag_map.items():
        with urllib.request.urlopen(url) as response:
            archive = response.read()
        compression_mode = url.split('.')[-1]
        convert_archive_to_wheel(name, pypi_version, archive, tag, summary, license, compression_mode)
