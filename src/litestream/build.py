from ..buildlib import build_wheels

NAME = 'litestream'
VERSION = '0.3.13'
PYPI_VERSION = '0.3.13a1'
SUMMARY = "A thin wrapper to distribute https://github.com/benbjohnson/litestream via pip."
LICENSE = "Apache-2.0"

TARGET_TAG = {
    'darwin-arm64.zip': 'macosx_11_0_arm64',
    'linux-arm64.tar.gz': 'manylinux_2_17_aarch64.manylinux2014_aarch64.musllinux_1_1_aarch64',
    'darwin-amd64.zip': 'macosx_10_9_x86_64',
    'linux-amd64.tar.gz': 'manylinux_2_12_x86_64.manylinux2010_x86_64.musllinux_1_1_x86_64',
}
URL_TAG = {f"https://github.com/benbjohnson/litestream/releases/download/v{VERSION}/{NAME}-V{VERSION}-{target}": tag for target, tag in TARGET_TAG.items()}


if __name__ == "__main__":
    print(URL_TAG)
    build_wheels(
        NAME,
        PYPI_VERSION,
        URL_TAG,
        SUMMARY,
        LICENSE,
        )
