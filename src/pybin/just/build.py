from pybin.buildlib import build_wheels

NAME = 'just'
UPSTREAM_REPO = 'https://github.com/casey/just'
VERSION = '1.41.0'
PYPI_VERSION = '1.41.0'
LICENSE = "CC0 1.0 Universal"

TARGET_TAG = {
    'aarch64-apple-darwin': 'macosx_11_0_arm64',
    'aarch64-unknown-linux-musl': 'manylinux_2_17_aarch64.manylinux2014_aarch64.musllinux_1_1_aarch64',
    'x86_64-apple-darwin': 'macosx_10_9_x86_64',
    'x86_64-unknown-linux-musl': 'manylinux_2_12_x86_64.manylinux2010_x86_64.musllinux_1_1_x86_64',
}
URL_TAG = {f"{UPSTREAM_REPO}/releases/download/{VERSION}/{NAME}-{VERSION}-{target}.tar.gz": tag for target, tag in TARGET_TAG.items()}


if __name__ == "__main__":
    build_wheels(
        NAME,
        PYPI_VERSION,
        URL_TAG,
        UPSTREAM_REPO,
        LICENSE,
        )
