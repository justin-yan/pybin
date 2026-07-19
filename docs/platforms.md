Getting the platform tags matched up and validated is kind of tricky, since I don't have the machines to test all configurations.

I'm trying to make some simplifying assumptions that will hopefully be broadly true enough to support most cases.

- Archs:
  - x86
  - aarch64
- Platforms:
  - mac
  - windows (use .exe as suffix for binary)
  - linux
    - When a choice between musl and gnu is offered, use *musl* binaries and assume that musl is statically linked.
