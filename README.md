# pybin

This project was inspired by how [Maturin packages rust binaries](https://www.maturin.rs/bindings#bin).  The key observation is that in the wheel format, the [distribution-1.0.data/scripts/ directory is copied to bin](https://packaging.python.org/en/latest/specifications/binary-distribution-format/#installing-a-wheel-distribution-1-0-py32-none-any-whl), which means we can leverage this to seamlessly copy binaries into a user's PATH.

Combined with Python's platform-specific wheels, this allows us to use pip as a "cross-platform package manager" for distributing single-binary CLI applications.

This is the [list of tools bundled this way](https://github.com/justin-yan/pybin/tree/main/src/pybin), which can be installed with `pip install $TOOLNAME-bin`. 

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
