from ..buildlib import build_wheels

NAME = 'dbmate'
UPSTREAM_REPO = "https://github.com/amacneil/dbmate"
VERSION = '2.17.0'
PYPI_VERSION = '2.17.0'
SUMMARY = f"A thin wrapper to distribute {UPSTREAM_REPO} via pip."
LICENSE = "MIT"

TARGET_TAG = {
    'macos-arm64': 'macosx_11_0_arm64',
    'linux-arm64': 'manylinux_2_17_aarch64.manylinux2014_aarch64.musllinux_1_1_aarch64',
    'macos-amd64': 'macosx_10_9_x86_64',
    'linux-amd64': 'manylinux_2_12_x86_64.manylinux2010_x86_64.musllinux_1_1_x86_64',
}
URL_TAG = {f"{UPSTREAM_REPO}/releases/download/v{VERSION}/{NAME}-{target}": tag for target, tag in TARGET_TAG.items()}


if __name__ == "__main__":
    build_wheels(
        NAME,
        PYPI_VERSION,
        URL_TAG,
        SUMMARY,
        LICENSE,
        )
