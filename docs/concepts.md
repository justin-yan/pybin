## Examples

- Github:
  - repository
  - with N releases
  - with M assets
- PyPI:
  - package
  - with N releases
  - with M distributions (wheels)
- Docker:
  - repository
  - With N tags
  - with M images (+ an OCI index)


## Domain Concept

- Release: N binaries, name, version, license
- Binary: bytes, architecture, platform

  
## Replication Concept

- ReleaseSource:
  - Registry + Read Rule
- ReleaseTarget:
  - Registry + Write Rule

The read and write rules will need to have some concept of applying distribution formats to registry implementations

- DistributionFormat:
    - wheel
    - Tar
    - "passthrough"
    - OCI Image
    - Go vs. Rust name parsing(?)
