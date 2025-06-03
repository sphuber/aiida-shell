# Change log

## `v0.8.1` - 2025-06-03

### Fixes
- `ShellJob`: Fix `RemoteData` handling [[cfe207d]](https://github.com/sphuber/aiida-shell/commit/cfe207dbe86f0675cce509071782c8debc624c37)

### Documentation
- Fix broken commit links in `CHANGELOG.md` [[14866d1]](https://github.com/sphuber/aiida-shell/commit/14866d1450aa252ec414373e86e98611e2eae9db)

### Devops
- Add explicit `sphinx.configuration` key to RTD conf [[189df63]](https://github.com/sphuber/aiida-shell/commit/189df631759eb07e574bfb5a5be2843ea532ec9d)


## `v0.8.0` - 2024-09-18

### Breaking changes
- `launch_shell_job`: Move `computer` to top-level of `metadata` [[2ab8219]](https://github.com/sphuber/aiida-shell/commit/2ab82195b755cfc6d814439a72670632d2e025ff)
- `ShellJob`: Change the signature of custom parser functions [[8a561b6]](https://github.com/sphuber/aiida-shell/commit/8a561b6a7c74eb35ff3a7bc7f062a72e41c4f707)

### Refactor
- Refactor: abstract `prepare_shell_job_inputs` from `launch_shell_job` [[cc72abd]](https://github.com/sphuber/aiida-shell/commit/cc72abd4e835c2f60d6a33750cfb50d29e71a232)

### Fixes
- `prepare_code`: Quote command when passing to `which` in order to resolve [[104d03b]](https://github.com/sphuber/aiida-shell/commit/104d03b3b9b43b3b3eec77e6e10bd6ec7ffa5ec0)
- `ShellCalculation`: Resolve escaped curly braces in arguments [[521a7ec]](https://github.com/sphuber/aiida-shell/commit/521a7ec491ea15d4f1a1af5cbf7621e37bb9ad7c)


## `v0.7.3` - 2024-07-16

### Fixes

- `ShellJob`: Fix bug when `metadata.options.output_filename` is specified [[437f2b3]](https://github.com/sphuber/aiida-shell/commit/437f2b3c656fec275ff8a5a4f710b469f6c3264c)


## `v0.7.2` - 2024-07-01

### Fixes
- `ShellJob`: Fix `RemoteData` inputs shadowing job's own input files [[9d32bf8]](https://github.com/sphuber/aiida-shell/commit/9d32bf8b94ca30bf3657abd6cbca541151e53f56)

### Dependencies
- Update requirement `aiida-core~=2.6` [[b41d007]](https://github.com/sphuber/aiida-shell/commit/b41d007231080450be58cabb020cfcbbde00d56b)

### Devops
- Package: Change `Development Status` from `Alpha` to `Beta` [[fcfce35]](https://github.com/sphuber/aiida-shell/commit/fcfce35d80bba3ae3070125dea52f1ac1e0b8cfa)
- Make use of the improved `pytest` fixtures in `aiida-core` [[27a6393]](https://github.com/sphuber/aiida-shell/commit/27a63932eeca3ca80356dc0a9a0f9ef9b7b78295)


## `v0.7.1` - 2024-05-13

### Fixes
- `ShellParser`: Prefix output filenames starting with a number [[352c309]](https://github.com/sphuber/aiida-shell/commit/352c309c0b4b5fd2c6af78dcf01013bfb6def6a6)

### Docs
- Docs: Add hint on retrieving outputs from daemon submitted jobs [[31ebfbc]](https://github.com/sphuber/aiida-shell/commit/31ebfbcde77f30a34a5495f349c19424d8dc1984)


## `v0.7.0` - 2024-03-22

### Features
- `PickledData`: Allow passing kwargs to pickler [[f94f030]](https://github.com/sphuber/aiida-shell/commit/f94f030abb36fd8f0dee60190c71b9df5e0a8a6c)
- `ShellJob`: Automatically serialize string for `arguments` [[4518221]](https://github.com/sphuber/aiida-shell/commit/451822157d9bc585254fded0352863258a7a7290)
- `launch_shell_job`: Add option to keep skip resolving of `command` [[d4ad9e7]](https://github.com/sphuber/aiida-shell/commit/d4ad9e72b26b3fd6591501e29fab2c9d70046d88)

### Fixes
- Fix `InvalidOperation` raised by `aiida-core` when pickling [[0458966]](https://github.com/sphuber/aiida-shell/commit/045896653ab3f7459a6400039596400f22bb2004)
- `prepare_computer`: Check whether `default_mpiprocs_per_machine` is set [[97f0b55]](https://github.com/sphuber/aiida-shell/commit/97f0b55404f81b8020591773075721f9efd34776)
- `ShellJob`: Detect and prevent filename clashes [[415b27e]](https://github.com/sphuber/aiida-shell/commit/415b27e1ab69e98afba27a2179c095f8feca6c4b)

### Changes
- Set default localhost scratch to `$TMP/aiida_shell_scratch` [[beeab21]](https://github.com/sphuber/aiida-shell/commit/beeab21f87ecb89d798fa9a142e099b8689bd478)

### Dependencies
- Add support for Python 3.12 [[0ddb9c3]](https://github.com/sphuber/aiida-shell/commit/0ddb9c3178a0b76719f20d8a2ba869eb31e0147c)
- Drop support for Python 3.8 [[ab97ef7]](https://github.com/sphuber/aiida-shell/commit/ab97ef796d365c4ecd30edd2c0556f3c701c7a8d)
- Update minimum requirement `aiida-core~=2.5` (#69) [[d61dd00]](https://github.com/sphuber/aiida-shell/commit/d61dd00db66a3d2d82cb18a1907da2c510272ac0)

### Docs
- Add a favicon [[c439b5f]](https://github.com/sphuber/aiida-shell/commit/c439b5f592884ccb3d407d48fe8bc0f2f4a74f4c)
- Add how-to on use of `prepend_text` metadata option (#67) [[d20edd1]](https://github.com/sphuber/aiida-shell/commit/d20edd1b56f7738daa2de1a03c06d4d7f19cef18)
- Add section on how to run with MPI [[adf491d]](https://github.com/sphuber/aiida-shell/commit/adf491d9973d0ecb5b9d42c6bb0fc7c63e2b73ca)
- Add section with examples [[2d9ae56]](https://github.com/sphuber/aiida-shell/commit/2d9ae56c7514e3ea290e3bafbdeb7cfb1e1c8764)
- Fix typos `option` instead of `options` [[825aad1]](https://github.com/sphuber/aiida-shell/commit/825aad1fcf2c9f94034c2f4f1e4737c6b17c635a)
- Link to AiiDA's docs for creating custom codes [[0cfbe4c]](https://github.com/sphuber/aiida-shell/commit/0cfbe4c72a0560f41af345ea4ebfab10079c5f69)

### Devops
- Add pre-commit hooks to format TOML and YAML files [[1cfb428]](https://github.com/sphuber/aiida-shell/commit/1cfb42890dac545785d4235a9fd187ee6fbd69bd)


## `v0.6.0` - 2023-11-02

### Features
- `ShellJob`: Add support for `RemoteData` nodes [[4a60253]](https://github.com/sphuber/aiida-shell/commit/4a60253210b455869e285685dfc53984204fe11c)

    The `nodes` input of the `launch_shell_job` and `ShellJob` now allow `RemoteData` nodes.
    Their content will be copied to the working directory of the job, just as with `SinglefileData` nodes.
    See [the how-to example in the documentation](https://aiida-shell.readthedocs.io/en/latest/howto.html#running-a-shell-command-with-remote-data) for details.

- `ShellJob`: Allow entry point strings for the `parser` input [[2f4fb3d]](https://github.com/sphuber/aiida-shell/commit/2f4fb3df8e419228cf2b70ddf1aa5bd25b0ae708)
- Add the `EntryPointData` data plugin [[161cfef]](https://github.com/sphuber/aiida-shell/commit/161cfef271b4b97150c747447a9b51e28afd592d)

### Fixes
- `ShellJob`: Do not copy contents of `nodes` to repository [[5d46235]](https://github.com/sphuber/aiida-shell/commit/5d4623504cb36387334356d5bfb131f30153efc8)

### Changes
- `launch_shell_job`: Move `arguments` to be the second argument [[8957f59]](https://github.com/sphuber/aiida-shell/commit/8957f594405e05bfe87e0d285e771b30d8953b6f)
- Add top-level imports explicitly to `__all__` [[7fc9ba5]](https://github.com/sphuber/aiida-shell/commit/7fc9ba5aaa89f1f9c2595b3c35c35d16f70c3d6d)
- Move module `engine.launchers.shell_job` to `launch` [[a0dac1e]](https://github.com/sphuber/aiida-shell/commit/a0dac1e2f34db6cd13eafb4ebf4ac0ba2143ecba)

### Docs
- Update the styling to custom theme [[0588076]](https://github.com/sphuber/aiida-shell/commit/0588076b13c8e4d818ded72c88cc899e77a771ac)
- Add example showcase of `pdb-tools` [[ae6b919]](https://github.com/sphuber/aiida-shell/commit/ae6b919492300091aa3fedbf061b50cbbbd2a5bf)
- Add the changelog to the documentation [[6bc435b]](https://github.com/sphuber/aiida-shell/commit/6bc435bece7c38ad0d8b555a0cebe3936382b637)
- Improve the logo [[42fd0de]](https://github.com/sphuber/aiida-shell/commit/42fd0def21ac9a9234fc136b582fef98ae1a0f7d)
- Fix outdated markdown style header [[a2a9294]](https://github.com/sphuber/aiida-shell/commit/a2a929478c2137726045e251fa47b3b09eb10ebb)

### Devops
- Migrate to `ruff` and cleanup pre-commit config [[a591f2a]](https://github.com/sphuber/aiida-shell/commit/a591f2ab0f4d81d07eb617404df058ddd6a1f351)
- Update `setup-python` dependency in CI/CD to v4 [[3788672]](https://github.com/sphuber/aiida-shell/commit/37886727bf583e35ae7e9ea9db06ce2984cff5d7)
- Update dependency requirement `mypy==1.6.1` [[5ddb83e]](https://github.com/sphuber/aiida-shell/commit/5ddb83eef22d01ca98dc099635a0f63333129d03)


## `v0.5.3` - 2023-06-13

### Features
- `ShellJob`: Add support for `FolderData` in `nodes` input [[9587c33]](https://github.com/sphuber/aiida-shell/commit/9587c337cd70b2dadb26a723dfa1ad4691570272)


## `v0.5.2` - 2023-05-12

### Features
- `ShellJob`: Add the optional `redirect_stderr` input [[92f726b]](https://github.com/sphuber/aiida-shell/commit/92f726b5fcd631dc4aaa85505869e2dabca9b77c)

    A common practice when running shell commands is to redirect the content, written to the stderr file descriptor, to stdout.
    This is normally accomplished as follows:

        date > stdout 2>&1

    This behaviour can now be reproduced by setting the ``metadata.options.redirect_stderr`` input to ``True``:

        from aiida_shell import launch_shell_job
        results, node = launch_shell_job(
            'date',
            metadata={'options': {'redirect_stderr': True}}
        )

### Fixes
- `ShellJob`: Add `invalidates_cache=True` to exit codes < `400` [[4d405e1]](https://github.com/sphuber/aiida-shell/commit/4d405e168aa46a8e1d878e2e4040cc128cc651fa)

### Devops
- Add the `py.typed` file following PEP 561 [[680a0e9]](https://github.com/sphuber/aiida-shell/commit/680a0e9e4a8888c6967ce7c3b531da551f210401)
- Update Python version on RTD to 3.11 [[2cfd4a2]](https://github.com/sphuber/aiida-shell/commit/2cfd4a243cf4db45800e5e84f78acec08fa9844d)


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
    from aiida.orm import SinglefileData
    from aiida_shell import launch_shell_job
    results, node = launch_shell_job(
        'cat',
        nodes={
            'input': SinglefileData.from_string('string a')
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
