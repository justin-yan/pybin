from pybin.buildlib import build_wheels

NAME = 'hadolint'
UPSTREAM_REPO = 'https://github.com/hadolint/hadolint'
VERSION = '2.12.0'
PYPI_VERSION = '2.12.0'
LICENSE = "GPLv3"

TARGET_TAG = {
    'Darwin-x86_64': 'macosx_10_9_x86_64',
    'Linux-arm64': 'manylinux_2_17_aarch64.manylinux2014_aarch64.musllinux_1_1_aarch64',
    'Linux-x86_64': 'manylinux_2_12_x86_64.manylinux2010_x86_64.musllinux_1_1_x86_64',
}
URL_TAG = {f"{UPSTREAM_REPO}/releases/download/v{VERSION}/{NAME}-{target}": tag for target, tag in TARGET_TAG.items()}


if __name__ == "__main__":
    build_wheels(
        NAME,
        PYPI_VERSION,
        URL_TAG,
        UPSTREAM_REPO,
        LICENSE,
        )
