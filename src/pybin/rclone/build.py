from pybin.buildlib import build_wheels

NAME = 'rclone'
UPSTREAM_REPO = 'https://github.com/rclone/rclone'
VERSION = '1.69.0'
PYPI_VERSION = '1.69.0'
LICENSE = "MIT"

TARGET_TAG = {
    'osx-arm64': 'macosx_11_0_arm64',
    'osx-amd64': 'macosx_10_9_x86_64',
    'linux-arm': 'manylinux_2_17_aarch64.manylinux2014_aarch64.musllinux_1_1_aarch64',
    'linux-amd64': 'manylinux_2_12_x86_64.manylinux2010_x86_64.musllinux_1_1_x86_64',
}
URL_TAG = {f"{UPSTREAM_REPO}/releases/download/v{VERSION}/{NAME}-v{VERSION}-{target}.zip": tag for target, tag in TARGET_TAG.items()}

if __name__ == "__main__":
    build_wheels(
        NAME,
        PYPI_VERSION,
        URL_TAG,
        UPSTREAM_REPO,
        LICENSE,
        )
