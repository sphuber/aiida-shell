# Change log

## v0.2.0

### Breaking changes
- `ShellJob`: `files` input `files` renamed to `nodes` [[f6dbfa03]](https://github.com/sphuber/aiida-shell/commit/f6dbfa0373a37df5ef776a91442bcc4ba6c6fdc5)
- `launch_shell_job`: keyword `files` renamed to `nodes`[[f6dbfa03]](https://github.com/sphuber/aiida-shell/commit/f6dbfa0373a37df5ef776a91442bcc4ba6c6fdc5)

### Features
- `ShellJob`: add support for additional `Data` types to the `nodes` input. This allows for example to pass `Float`, `Int` and `Str` instances. [[f6dbfa03]](https://github.com/sphuber/aiida-shell/commit/f6dbfa0373a37df5ef776a91442bcc4ba6c6fdc5)
- `ShellJob`: add validation for `outputs` input [[7f17e10e]](https://github.com/sphuber/aiida-shell/commit/7f17e10e3d0106139d7e1ba2811622615e029c98)

### Dependencies
- Update requirement to `aiida-core~=2.0` [[1387f65d]](https://github.com/sphuber/aiida-shell/commit/1387f65dfcc6485807f5f21dab93ddbeab0677e3)

### Devops
- Add GitHub Actions workflow for continuous deployment [[667ede87]](https://github.com/sphuber/aiida-shell/commit/667ede875899bab26d2ece5cdcfc37a2a1179f4c)
- Update the README.md with badges [[25e789fa]](https://github.com/sphuber/aiida-shell/commit/25e789faa860132af86e1d40333a57bca451aa4a)
- Make package description in pyproject.toml dynamic [[b1040187]](https://github.com/sphuber/aiida-shell/commit/b104018703487c03bc858132defbdb94d73307dc)
- Update the pre-commit dependencies [[1a217eef]](https://github.com/sphuber/aiida-shell/commit/1a217eef3e3d3722070e0e6f4edbbbc40ca18a47)
- Fix the tool.flit.sdist list in pyproject.toml [[fc1d995b]](https://github.com/sphuber/aiida-shell/commit/fc1d995bef3abaafeeae34e41b4f0a064c87b46d)
- Minor improvements to the README.md [[89913e4d]](https://github.com/sphuber/aiida-shell/commit/89913e4de2bc96e149fe86287e3e682fd4fb2854)
- Tests: filter warning for AiiDA creating the config directory[[57a76f55]](https://github.com/sphuber/aiida-shell/commit/57a76f5580291fc96635d62a8ee281e9217bff93)
