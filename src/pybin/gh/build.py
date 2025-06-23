from pybin.buildlib import build_wheels

NAME = 'gh'
UPSTREAM_REPO = "https://github.com/cli/cli"
VERSION = '2.74.2'
PYPI_VERSION = '2.74.2'
LICENSE = "MIT"

TARGET_TAG = {
    'macOS_arm64.zip': 'macosx_11_0_arm64',
    'linux_arm64.tar.gz': 'manylinux_2_17_aarch64.manylinux2014_aarch64.musllinux_1_1_aarch64',
    'macOS_amd64.zip': 'macosx_10_9_x86_64',
    'linux_amd64.tar.gz': 'manylinux_2_12_x86_64.manylinux2010_x86_64.musllinux_1_1_x86_64',
}
URL_TAG = {f"{UPSTREAM_REPO}/releases/download/v{VERSION}/{NAME}_{VERSION}_{target}": tag for target, tag in TARGET_TAG.items()}


if __name__ == "__main__":
    build_wheels(
        NAME,
        PYPI_VERSION,
        URL_TAG,
        UPSTREAM_REPO,
        LICENSE,
        )
