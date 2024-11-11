from ..buildlib import build_wheels

NAME = 'scc'
UPSTREAM_REPO = 'https://github.com/boyter/scc'
VERSION = '3.2.0'
PYPI_VERSION = '3.2.0'
LICENSE = "The Unlicense (Unlicense)"

TARGET_TAG = {
    'Darwin_arm64': 'macosx_11_0_arm64',
    'Darwin_x86_64': 'macosx_10_9_x86_64',
    'Linux_arm64': 'manylinux_2_17_aarch64.manylinux2014_aarch64.musllinux_1_1_aarch64',
    'Linux_x86_64': 'manylinux_2_12_x86_64.manylinux2010_x86_64.musllinux_1_1_x86_64',
}
URL_TAG = {f"{UPSTREAM_REPO}/releases/download/v{VERSION}/{NAME}_{target}.tar.gz": tag for target, tag in TARGET_TAG.items()}


if __name__ == "__main__":
    build_wheels(
        NAME,
        PYPI_VERSION,
        URL_TAG,
        UPSTREAM_REPO,
        LICENSE,
        )
