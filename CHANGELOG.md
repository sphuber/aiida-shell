# Change log

## `v0.5.1` - 2023-05-04

### Fixes
- `ShellJob`: Remove `tot_num_mpiprocs` from `resources` default [[5e61c89]](https://github.com/sphuber/aiida-shell/commit/5e61c891958f705eaf56d8b590227011f16706ef)
- `launch_shell_job`: Only `which` command if code doesn't already exist [[c1c31ab]](https://github.com/sphuber/aiida-shell/commit/c1c31ab404abcad4778accc8c01c3afbb818dfc8)


## `v0.5.0` - 2023-05-03

### Features
- `launch_shell_job`: Accept string for the `arguments` argument [[a8af91a]](https://github.com/sphuber/aiida-shell/commit/a8af91a5a0005233c3de4669b74bc185892a8126)

    It is now possible to pass the command line arguments for the command as a string, instead of a list of individual arguments:
    ```python
    from aiida_shell import launch_shell_job
    results, node = launch_shell_job(
        'date',
        arguments='--iso-8601 --universal',
    )
    ```

- `launch_shell_job`: Accept `AbstractCode` for `command` argument [[dacfbd3]](https://github.com/sphuber/aiida-shell/commit/dacfbd3e25e9c0fd05e7d4c033f4ea092e3825fb)

    It is now possible to pass a specific preconfigured code to run, instead of the command's name:
    ```python
    from aiida.orm import load_node
    from aiida_shell import launch_shell_job
    results, node = launch_shell_job(
        load_node('date@localhost'),
        arguments='--iso-8601 --universal',
    )
    ```

### Fixes
- `launch_shell_job`: Fix bug in `submit=True` when used within work chain [[dbeac91]](https://github.com/sphuber/aiida-shell/commit/dbeac9161e24b2abd57f4481ef15b6bea78a8e28)

### Devops
- Fix `mypy` configuration in `.pre-commit.config.yaml` [[e16ace0]](https://github.com/sphuber/aiida-shell/commit/e16ace018bd14b2112afa70d100bd8190065e2ab)
- Change PR numbers to commit hash in `CHANGELOG.md` [[71d8f2b]](https://github.com/sphuber/aiida-shell/commit/71d8f2be5a03a2d6eb59b1aaff7e478e0d7e939a)
- Update version number in `CITATION.cff` [[b3f672c]](https://github.com/sphuber/aiida-shell/commit/b3f672cdae1d6fa611356cae4e0f53fbbd0a63ce)
- Fix the `daemon_client` fixture (#33) [[30a7c06]](https://github.com/sphuber/aiida-shell/commit/30a7c064b0c542b06ceb06de904534362f94a594)

### Documentation
- Add skeleton of documentation [[8595c17]](https://github.com/sphuber/aiida-shell/commit/8595c176ae4380d59502c13fdc41624087b30fb5)
- Add links to docs in `README.md` and `pyproject.toml` [[d987c55]](https://github.com/sphuber/aiida-shell/commit/d987c5515a496fff972d6bddf4aca33ee55adca6)
- Add logo [[03855fa]](https://github.com/sphuber/aiida-shell/commit/03855faa5a3944fd48f39439be2056d51080ff72)
- Move examples from `README.md` to how-to guides [[e15fb53]](https://github.com/sphuber/aiida-shell/commit/e15fb53b23163a412de829a7d7fefa5947cb8a03)


## `v0.4.0` - 2023-03-30

### Features
- `ShellParser`: Add support to parse output directory as `FolderData` [[269fd391]](https://github.com/sphuber/aiida-shell/commit/269fd391736d3567c20146c763b4882f44456f6b)

    It is now possible to add a directory to the `outputs` and it will be attached as a `FolderData` output node:
    ```python
    from io import StringIO
    from aiida.orm import SinglefileData
    from aiida_shell import launch_shell_job
    results, node = launch_shell_job(
        'tar',
        arguments=['-zxvf', '{archive}'],
        nodes={
            'archive': SinglefileData('/some/path/archive.tar.gz'),
        },
        outputs=['sub_folder']
    )
    ```

- `ShellJob`: Add `filename_stdin` input to redirect file through stdin [[87bc8360]](https://github.com/sphuber/aiida-shell/commit/87bc8360c28b08a27baffe4ccad445b7332241b1)

    Certain shell commands require input to be passed through the stdin file descriptor.
    To reproduce this behaviour, the file that should be redirected through stdin can be defined using the `metadata.option.filename_stdin` input:
    ```python
    from io import StringIO
    from aiida.orm import SinglefileData
    from aiida_shell import launch_shell_job
    results, node = launch_shell_job(
        'cat',
        nodes={
            'input': SinglefileData(StringIO('string a'))
        },
        metadata={'options': {'filename_stdin': 'input'}}
    )
    print(results['stdout'].get_content())
    ```

- `ShellJob`: Add support for custom parsing [[32db3847]](https://github.com/sphuber/aiida-shell/commit/32db3847975f14e5955e46f0abb28645c0939b4d)

    This makes it possible to define a custom parser on-the-fly to parse output data and attach it any existing `Data` class.
    For example, the content of the file can be stored as a `Str` instead of a `SinglefileData`:
    ```python
    from aiida_shell import launch_shell_job

    def parser(self, dirpath):
        from aiida.orm import Str
        return {'string': Str((dirpath / 'stdout').read_text().strip())}

    results, node = launch_shell_job(
        'echo',
        arguments=['some output'],
        parser=parser
    )
    print(results['string'].value)
    ```

- `ShellJob`: Add the `additional_retrieve` option [[05def137]](https://github.com/sphuber/aiida-shell/commit/05def1371f53853a98417b9ee9d00a0903f36337)
- Add the `PickledData` data plugin [[3a40eefc]](https://github.com/sphuber/aiida-shell/commit/3a40eefc9c3bded1d69fbbb68c0960f0052222ea)

### Fixes
- `ShellJob`: Use `SinglefileData.filename` before falling back on key [[fe34d973]](https://github.com/sphuber/aiida-shell/commit/fe34d9731b7057b2d03f92483ade68f57b534a3f)
- `ShellJob`: Automatically create parent directories in `filenames` [[9b380200]](https://github.com/sphuber/aiida-shell/commit/9b380200efe0621d3bf50940d993e4ff88d7e9e8)
- `ShellJob`: Raise when `<` or `>` are specified in `arguments` [[5f42f0aa]](https://github.com/sphuber/aiida-shell/commit/5f42f0aa18911196352d2e7c780c29ee9b596e74)

### Dependencies
- Update pre-commit requirement `isort==5.12.0` [[69ac1ffe]](https://github.com/sphuber/aiida-shell/commit/69ac1ffe780305d5d111c848e82fb191b68c4891)


## `v0.3.0` - 2022-11-07

### Features
- `launch_shell_job`: Add the `submit` argument to run over the daemon [[6f2435bc]](https://github.com/sphuber/aiida-shell/commit/6f2435bc3a057531535925848c7407ece9d752f1)

    This adds support to submit shell job's to the daemon which allows to run many independen shell job's in parallel greatly increasing throughput:
    ```python
    launch_shell_job(
        'echo',
        arguments=['hello world'],
        submit=True
    )
    ```

- `ShellJob`: Add the `ERROR_STDERR_NOT_EMPTY` exit code [[8f4dd2cb]](https://github.com/sphuber/aiida-shell/commit/8f4dd2cbb0cf51a5c945a3c01b4036bd38b0c9b8)

    If the command returns a zero exit code, but the `stderr` is not empty, this exit code is set on the `ShellJob` marking it as failed.

- `ShellJob`: Customize the `_build_process_label` method [[506fe91f]](https://github.com/sphuber/aiida-shell/commit/506fe91f5aa27710fbf91d259c116c26ac310b36)

    This ensures that the `process_label` attribute that is set for the `CalcJobNode` that represents the job execution in the provenance graph is more descriptive.
    Before it used to just be `ShellJob` making all shell job's indistinguishable from one another.
    After this change, the label is formatted as `ShellJob<command@computer`.
    For example, running `echo` on the `localhost` gets the process label `ShellJob<echo@localhost>`.

- Add the `ShellCode` data plugin [[a185219a]](https://github.com/sphuber/aiida-shell/commit/a185219adf47476284c26aade0ba453ea67c7ded)

    This custom data plugin is used for codes that are automatically setup by the `launch_shell_job` function.
    By using a separate code plugin, it will be easy to query and filter for these codes.

### Fixes
- `ShellParser`: Fix output files with non-alphanumeric characters [[6f699897]](https://github.com/sphuber/aiida-shell/commit/6f699897a3e4187681bbd1f1c24ba7a4dc384f07)

    This fixes an exception that would be raised if an output file would be attached with non-alphanumeric characters, e.g., dashes.
    These characters are not valid for link labels for which the filenames are used.
    The invalid characters are now automatically replaced by underscores.

### Changes
- `launch_shell_job`: Change log level from `WARNING` to `INFO` [[a41f0ba1]](https://github.com/sphuber/aiida-shell/commit/a41f0ba1ec3f19c252f4af1c84c48923462f8467)

    The `launch_shell_job` function emits warnings if no explicit computer is specified and if a computer or code is created automatically.
    However, since this is the most common use-case and warnings are always shown by default, these warnings would crop up a lot.
    Therefore, the log level is changed to `INFO` such they are no longer shown by default, but if the logging level is upped by the user, the log messages will be shown.

### Dependencies
- Add support for Python 3.11 [[bde79f3c]](https://github.com/sphuber/aiida-shell/commit/bde79f3c60ec0ac1197e02291be06b4312993e4a)
- Update requirement `aiida-core~=2.1` [[f9391d61]](https://github.com/sphuber/aiida-shell/commit/f9391d61a9d11c30831b9b7d78de8a7d0cff9f31)


## `v0.2.0` - 2022-06-05

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
- Tests: filter warning for AiiDA creating the config directory [[57a76f55]](https://github.com/sphuber/aiida-shell/commit/57a76f5580291fc96635d62a8ee281e9217bff93)
