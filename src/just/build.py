from ..buildlib import build_wheels

NAME = 'just'
VERSION = '1.18.1'
PYPI_VERSION = '1.18.1'
SUMMARY = "A thin wrapper to distribute https://github.com/casey/just via pip."
LICENSE = "CC0 1.0 Universal"

TARGET_TAG = {
    'aarch64-apple-darwin': 'macosx_11_0_arm64',
    'aarch64-unknown-linux-musl': 'manylinux_2_17_aarch64.manylinux2014_aarch64.musllinux_1_1_aarch64',
    'x86_64-apple-darwin': 'macosx_10_9_x86_64',
    'x86_64-unknown-linux-musl': 'manylinux_2_12_x86_64.manylinux2010_x86_64.musllinux_1_1_x86_64',
}
URL_TAG = {f"https://github.com/casey/just/releases/download/{VERSION}/{NAME}-{VERSION}-{target}.tar.gz": tag for target, tag in TARGET_TAG.items()}


if __name__ == "__main__":
    build_wheels(
        NAME,
        PYPI_VERSION,
        URL_TAG,
        SUMMARY,
        LICENSE,
        )
