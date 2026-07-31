# pybin

This project was inspired by how [Maturin packages rust binaries](https://www.maturin.rs/bindings#bin).  The key observation is that in the wheel format, the [distribution-1.0.data/scripts/ directory is copied to bin](https://packaging.python.org/en/latest/specifications/binary-distribution-format/#installing-a-wheel-distribution-1-0-py32-none-any-whl), which means we can leverage this to seamlessly copy binaries into a user's PATH.

Combined with Python's platform-specific wheels, this allows us to use pip as a "cross-platform package manager" for distributing single-binary CLI applications.

This is the [list of tools bundled this way](https://github.com/justin-yan/pybin/tree/main/rules), which can be installed with `pip install $TOOLNAME-bin`. 

The same release can also be packaged as a multi-platform Docker image containing only the Linux binary. Add a Docker target to a rule:

```yaml
targets:
  - docker:
      repository: ghcr.io/example/{name}
      push: true
```

This publishes `ghcr.io/example/$TOOLNAME:$VERSION`, with the executable at `/$TOOLNAME`, for use as a build source:

```dockerfile
COPY --from=ghcr.io/example/example-tool:1.2.3 /example-tool /bin/
```

Omit `push` to load an image for the host architecture into the local Docker image store instead. The default local repository is `tool-{name}`.

## New Tool Onboarding

- Create a <tool>.yaml file.
- Fill out the github source and pypi target.
  - Stick to aarch and x86 for the architecture.
  - Prefer linux-musl if available for fully statically linked all-linux binaries.
- Create a pending publisher in PyPI for the proposed package name, targeting the `register.yaml` workflow.
