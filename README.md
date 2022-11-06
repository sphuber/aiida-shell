# `aiida-shell`
[![PyPI version](https://badge.fury.io/py/aiida-shell.svg)](https://badge.fury.io/py/aiida-shell)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/aiida-shell.svg)](https://pypi.python.org/pypi/aiida-shell)
[![CI](https://github.com/sphuber/aiida-shell/workflows/ci/badge.svg)](https://github.com/sphuber/aiida-shell/actions/workflows/ci.yml)

AiiDA plugin that makes running shell commands easy.
Run any shell executable without writing a dedicated plugin or parser.


## Installation

The recommended method of installation is through [`pip`](https://pip.pypa.io/en/stable/):

    pip install aiida-shell

## Requirements

To use `aiida-shell` a configured AiiDA profile is required.
Please refer to the [documentation of `aiida-core`](https://aiida.readthedocs.io/projects/aiida-core/en/latest/intro/get_started.html) for detailed instructions.


## Examples

### Running a shell command
The most simple example is to run a shell command without any arguments:

```python
from aiida_shell import launch_shell_job
results, node = launch_shell_job('date')
print(results['stdout'].get_content())
```
Which should print something like `Thu 17 Mar 2022 10:49:52 PM CET`.

### Running a shell command with arguments
To pass arguments to the shell command, pass them as a list to the `arguments` keyword:

```python
from aiida_shell import launch_shell_job
results, node = launch_shell_job(
    'date',
    arguments=['--iso-8601']
)
print(results['stdout'].get_content())
```
which should print something like `2022-03-17`.

### Running a shell command with files as arguments
For commands that take arguments that refer to files, pass those files using the `nodes` keyword.
The keyword takes a dictionary of `SinglefileData` nodes.
To specify where on the command line the files should be passed, use placeholder strings in the `arguments` keyword.
```python
from io import StringIO
from aiida.orm import SinglefileData
from aiida_shell import launch_shell_job
results, node = launch_shell_job(
    'cat',
    arguments=['{file_a}', '{file_b}'],
    nodes={
        'file_a': SinglefileData(StringIO('string a')),
        'file_b': SinglefileData(StringIO('string b')),
    }
)
print(results['stdout'].get_content())
```
which prints `string astring b`.

### Running a shell command with files as arguments with specific filenames
The keys in the `nodes` dictionary can only use alphanumeric characters and underscores.
The keys will be used as the link label of the file in the provenance graph, and as the filename in the temporary directory in which the shell command will be executed.
Certain commands may require specific filenames, for example including a file extension, e.g., `filename.txt`, but this cannot be used in the `nodes` arguments.
To specify explicit filenames that should be used in the running directory, that are different from the keys in the `nodes` argument, use the `filenames` argument:
```python
from io import StringIO
from aiida.orm import SinglefileData
from aiida_shell import launch_shell_job
results, node = launch_shell_job(
    'cat',
    arguments=['{file_a}'],
    nodes={
        'file_a': SinglefileData(StringIO('string a')),
    },
    filenames={
        'file_a': 'filename.txt'
    }
)
print(results['stdout'].get_content())
```
which prints `string a`.

The output filename can be anything except for `stdout`, `stderr` and `status`, which are reserved filenames.

### Passing other `Data` types as input
The `nodes` keyword does not only accept `SinglefileData` nodes, but it accepts also other `Data` types.
For these node types, the content returned by the `value` property is directly cast to `str`, which is used to replace the corresponding placeholder in the `arguments`.
So as long as the `Data` type implements this `value` property it should be supported.
Of course, whether it makes sense for the value of the node to be used directly as a command line argument for the shell job, is up to the user.
Typical useful examples, are the base types that ship with AiiDA, such as the `Float`, `Int` and `Str` types:
```python
from aiida.orm import Float, Int, Str
from aiida_shell import launch_shell_job
results, node = launch_shell_job(
    'echo',
    arguments=['{float}', '{int}', '{string}'],
    nodes={
        'float': Float(1.0),
        'int': Int(2),
        'string': Str('string'),
    },
)
print(results['stdout'].get_content())
```
which prints `1.0 2 string`.
This example is of course contrived, but when combining it with other components of AiiDA, which typically return outputs of these form, they can be used directly as inputs for `launch_shell_job` without having to convert the values.
This ensures that provenance is kept.

### Defining output files
When the shell command is executed, AiiDA captures by default the content written to the stdout and stderr file descriptors.
The content is wrapped in a `SinglefileData` node and attached to the `ShellJob` with the `stdout` and `stderr` link labels, respectively.
Any other output files that need to be captured can be defined using the `outputs` keyword argument.
```python
from io import StringIO
from aiida.orm import SinglefileData
from aiida_shell import launch_shell_job
results, node = launch_shell_job(
    'sort',
    arguments=['{input}', '--output', 'sorted'],
    nodes={
        'input': SinglefileData(StringIO('2\n5\n3')),
    },
    outputs=['sorted']
)
print(results['sorted'].get_content())
```
which prints `2\n3\n5`.

### Defining output files with globbing
When the exact output files that will be generated and need to be captured are not known in advance, one can use globbing.
Take for example the `split` command, which split a file into multiple files of a certain number of lines.
By default, each output file will follow the sequence `xa`, `xb`, `xc` etc. augmenting the last character alphabetically.
These output files can be captured by specifying the `outputs` as `['x*']`:
```python
from io import StringIO
from aiida.orm import SinglefileData
from aiida_shell import launch_shell_job
results, node = launch_shell_job(
    'split',
    arguments=['-l', '1', '{single_file}'],
    nodes={
        'single_file': SinglefileData(StringIO('line 0\nline 1\nline 2\n')),
    },
    outputs=['x*']
)
print(results.keys())
```
which prints `dict_keys(['xab', 'xaa', 'xac', 'stderr', 'stdout'])`.

### Defining a specific computer
By default the shell command ran by `launch_shell_job` will be executed on the localhost, i.e., the computer where AiiDA is running.
However, AiiDA also supports running commands on remote computers.
See the [documentation of `aiida-core`](https://aiida.readthedocs.io/projects/aiida-core/en/latest/howto/run_codes.html#how-to-set-up-a-computer) for instructions to setting up and configuring a remote computer.
To specify what computer to use for a shell command, pass it as an option to the `metadata` keyword:
```python
from aiida.orm import load_computer
from aiida_shell import launch_shell_job
results, node = launch_shell_job(
    'date',
    metadata={'options': {'computer': load_computer('some-computer')}}
)
print(results['stdout'].get_content())
```
Here you can use `aiida.orm.load_computer` to load the `Computer` instance from its label, PK or UUID.

### Running many shell jobs in parallel
By default the shell command ran by `launch_shell_job` is run blockingly; meaning that the Python interpreter is blocked from doing anything else until the shell command finishes.
This becomes inefficient if you need to run many shell commands.
If the shell commands are independent and can be run in parallel, it is possible to submit the jobs to AiiDA's daemon by setting `submit=True`:
```python
from aiida.engine.daemon.client import get_daemon_client
from aiida_shell import launch_shell_job

# Make sure the daemon is running
get_daemon_client().start_daemon()

nodes = []

for string in ['string_one', 'string_two']:
    node = launch_shell_job(
        'echo',
        arguments=[string],
        submit=True,
    )
    nodes.append(node)
    print(f'Submitted {node}')
```
Instead of returning a tuple of the results and the node, `launch_shell_job` now only returns the `node`.
The reason is because the function returns immediately after submitting the job to the daemon at which point it isn't necessarily finished yet.
To check on the status of the submitted jobs, you can use the `verdi process list` command of the CLI that ships with AiiDA.
Or you can do it programmatically:
```python
import time

while True:
    if all(node.is_terminated for node in nodes):
        break
    time.sleep(1)

for node in nodes:
    if node.is_finished_ok:
        print(f'{node} finished successfully')
    else:
        print(f'{node} failed')
```
