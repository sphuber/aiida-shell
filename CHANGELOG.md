# Change log

## `v0.4.0` - 2023-03-30

### Features
- `ShellParser`: Add support to parse output directory as `FolderData` [[#31]](https://github.com/sphuber/aiida-shell/pull/31)

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

- `ShellJob`: Add `filename_stdin` input to redirect file through stdin [[#27]](https://github.com/sphuber/aiida-shell/pull/27)

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

- `ShellJob`: Add support for custom parsing [[#19]](https://github.com/sphuber/aiida-shell/pull/19)

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

- `ShellJob`: Add the `additional_retrieve` option [[#19]](https://github.com/sphuber/aiida-shell/pull/19)
- Add the `PickledData` data plugin [[#19]](https://github.com/sphuber/aiida-shell/pull/19)

### Fixes
- `ShellJob`: Use `SinglefileData.filename` before falling back on key [[#26]](https://github.com/sphuber/aiida-shell/pull/26)
- `ShellJob`: Automatically create parent directories in `filenames` [[#29]](https://github.com/sphuber/aiida-shell/pull/29)
- `ShellJob`: Raise when `<` or `>` are specified in `arguments` [[#28]](https://github.com/sphuber/aiida-shell/pull/28)

### Dependencies
- Update pre-commit requirement `isort==5.12.0` [[#30]](https://github.com/sphuber/aiida-shell/pull/30)


## `v0.3.0` - 2022-11-07

### Features
- `launch_shell_job`: Add the `submit` argument to run over the daemon [[#18]](https://github.com/sphuber/aiida-shell/pull/18)

    This adds support to submit shell job's to the daemon which allows to run many independen shell job's in parallel greatly increasing throughput:
    ```python
    launch_shell_job(
        'echo',
        arguments=['hello world'],
        submit=True
    )
    ```

- `ShellJob`: Add the `ERROR_STDERR_NOT_EMPTY` exit code [[#15]](https://github.com/sphuber/aiida-shell/pull/15)

    If the command returns a zero exit code, but the `stderr` is not empty, this exit code is set on the `ShellJob` marking it as failed.

- `ShellJob`: Customize the `_build_process_label` method [[#17]](https://github.com/sphuber/aiida-shell/pull/17)

    This ensures that the `process_label` attribute that is set for the `CalcJobNode` that represents the job execution in the provenance graph is more descriptive.
    Before it used to just be `ShellJob` making all shell job's indistinguishable from one another.
    After this change, the label is formatted as `ShellJob<command@computer`.
    For example, running `echo` on the `localhost` gets the process label `ShellJob<echo@localhost>`.

- Add the `ShellCode` data plugin [[#20]](https://github.com/sphuber/aiida-shell/pull/20)

    This custom data plugin is used for codes that are automatically setup by the `launch_shell_job` function.
    By using a separate code plugin, it will be easy to query and filter for these codes.

### Fixes
- `ShellParser`: Fix output files with non-alphanumeric characters [[#10]](https://github.com/sphuber/aiida-shell/pull/10)

    This fixes an exception that would be raised if an output file would be attached with non-alphanumeric characters, e.g., dashes.
    These characters are not valid for link labels for which the filenames are used.
    The invalid characters are now automatically replaced by underscores.

### Changes
- `launch_shell_job`: Change log level from `WARNING` to `INFO` [[#16]](https://github.com/sphuber/aiida-shell/pull/16)

    The `launch_shell_job` function emits warnings if no explicit computer is specified and if a computer or code is created automatically.
    However, since this is the most common use-case and warnings are always shown by default, these warnings would crop up a lot.
    Therefore, the log level is changed to `INFO` such they are no longer shown by default, but if the logging level is upped by the user, the log messages will be shown.

### Dependencies
- Add support for Python 3.11 [[#13]](https://github.com/sphuber/aiida-shell/pull/13)
- Update requirement `aiida-core~=2.1` [[#22]](https://github.com/sphuber/aiida-shell/pull/22)


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
- Tests: filter warning for AiiDA creating the config directory[[57a76f55]](https://github.com/sphuber/aiida-shell/commit/57a76f5580291fc96635d62a8ee281e9217bff93)
