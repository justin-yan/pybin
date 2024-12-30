from pybin.buildlib import build_wheels

NAME = 'usql'
UPSTREAM_REPO = 'https://github.com/xo/usql'
VERSION = '0.19.15'
PYPI_VERSION = '0.19.15'
LICENSE = "MIT"

TARGET_TAG = {
    'darwin-arm64': 'macosx_11_0_arm64',
    'darwin-amd64': 'macosx_10_9_x86_64',
    'linux-arm64': 'manylinux_2_17_aarch64.manylinux2014_aarch64.musllinux_1_1_aarch64',
    'linux-amd64': 'manylinux_2_12_x86_64.manylinux2010_x86_64.musllinux_1_1_x86_64',
}
URL_TAG = {f"{UPSTREAM_REPO}/releases/download/v{VERSION}/{NAME}-{VERSION}-{target}.tar.bz2": tag for target, tag in TARGET_TAG.items()}


if __name__ == "__main__":
    build_wheels(
        NAME,
        PYPI_VERSION,
        URL_TAG,
        UPSTREAM_REPO,
        LICENSE,
        )
