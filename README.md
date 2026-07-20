# pybin

This project was inspired by how [Maturin packages rust binaries](https://www.maturin.rs/bindings#bin).  The key observation is that in the wheel format, the [distribution-1.0.data/scripts/ directory is copied to bin](https://packaging.python.org/en/latest/specifications/binary-distribution-format/#installing-a-wheel-distribution-1-0-py32-none-any-whl), which means we can leverage this to seamlessly copy binaries into a user's PATH.

Combined with Python's platform-specific wheels, this allows us to use pip as a "cross-platform package manager" for distributing single-binary CLI applications.

This is the [list of tools bundled this way](https://github.com/justin-yan/pybin/tree/main/rules), which can be installed with `pip install $TOOLNAME-bin`. 

## New Tool Onboarding

- Create a <tool>.yaml file.
- Fill out the github source and pypi target.
  - Stick to aarch and x86 for the architecture.
  - Prefer linux-musl if available for fully statically linked all-linux binaries.
- Create a pending publisher in PyPI for the proposed package name, targeting the `register.yaml` workflow.
