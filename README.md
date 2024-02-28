# pybin

This project was inspired by how [Maturin packages rust binaries](https://www.maturin.rs/bindings#bin).  The key observation is that in the wheel format, the [distribution-1.0.data/scripts/ directory is copied to bin](https://packaging.python.org/en/latest/specifications/binary-distribution-format/#installing-a-wheel-distribution-1-0-py32-none-any-whl), which means we can leverage this to seamlessly copy binaries into a user's PATH.

Combined with Python's platform-specific wheels, this allows us to use pip as a "cross-platform package manager" for distributing single-binary CLI applications.

## Wheel Building Process

The core of the logic lies in the `buildlib.py` module.

- A mapping from download URL (often github releases) to pypi platform tag is required.
- For each platform:
    - Download the release & extract the binary.
    - Set file permissions and place into scripts directory within wheel archive.
    - Create the METADATA and WHEEL files within wheel archive.
    - Place wheel into `dist/` folder.
- Once all wheels are constructed, the distribution is uploaded to PyPI.

CICD is configured to automatically recognize new *PyPI* releases by looking for a diff on the PYPI_VERSION.  When this happens, a build-and-release cycle is performed for that release version.

## Catalog

- `pip install dive-bin`: [pybin version](https://github.com/justin-yan/pybin/tree/main/src/dive), [upstream source](https://github.com/wagoodman/dive)
- `pip install hadolint-bin`: [pybin version](https://github.com/justin-yan/pybin/tree/main/src/hadolint), [upstream source](https://github.com/hadolint/hadolint)
- `pip install just-bin`: [pybin version](https://github.com/justin-yan/pybin/tree/main/src/just), [upstream source](https://github.com/casey/just)
- `pip install lazydocker-bin`: [pybin version](https://github.com/justin-yan/pybin/tree/main/src/lazydocker), [upstream source](https://github.com/jesseduffield/lazydocker)
- `pip install rclone-bin`: [pybin version](https://github.com/justin-yan/pybin/tree/main/src/rclone), [upstream source](https://github.com/rclone/rclone)
- `pip install scc-bin`: [pybin version](https://github.com/justin-yan/pybin/tree/main/src/scc), [upstream source](https://github.com/boyter/scc)
- `pip install usql-bin`: [pybin version](https://github.com/justin-yan/pybin/tree/main/src/usql), [upstream source](https://github.com/xo/usql)
