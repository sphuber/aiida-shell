# `aiida-shell`
AiiDA plugin that makes running shell commands easy.

## Installation

The recommended method of installation is through the [`pip` package installer for Python](https://pip.pypa.io/en/stable/):

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
which should print something `2022-03-17`.

### Running a shell command with files as arguments
For commands that take arguments that refer to files, pass those files using the `files` keyword.
The keyword takes a dictionary of `SinglefileData` nodes.
To specify where on the command line the files should be passed, use placeholder strings in the `arguments` keyword.
```python
from io import StringIO
from aiida.orm import SinglefileData
from aiida_shell import launch_shell_job
files = {
    'file_a': SinglefileData(StringIO('string a')),
    'file_b': SinglefileData(StringIO('string b')),
}
results, node = launch_shell_job(
    'cat',
    arguments=['{file_a}', '{file_b}'],
    files=files
)
print(results['stdout'].get_content())
```
which prints `string astring b`.

### Running a shell command with files as arguments with specific filenames
The keys in the `files` dictionary can only use alphanumeric characters and underscores.
The keys will be used as the link label of the file in the provenance graph, and as the filename in the temporary directory in which the shell command will be executed.
Certain commands may require specific filenames, for example including a file extension, e.g., `filename.txt`, but this cannot be used in the `files` arguments.
To specify explicit filenames that should be used in the running directory, that are different from the keys in the `files` argument, use the `filenames` argument:
```python
from io import StringIO
from aiida.orm import SinglefileData
from aiida_shell import launch_shell_job
files = {
    'file_a': SinglefileData(StringIO('string a')),
}
filenames = {
    'file_a': 'filename.txt'
}
results, node = launch_shell_job(
    'cat',
    arguments=['{file_a}'],
    files=files, filenames=filenames
)
print(results['stdout'].get_content())
```

### Defining output files
When the shell command is executed, AiiDA captures by default the content written to the stdout and stderr file descriptors.
The content is wrapped in a `SinglefileData` node and attached to the `ShellJob` with the `stdout` and `stderr` link labels, respectively.
Any other output files that need to be captured can be defined using the `outputs` keyword argument.
```python
from io import StringIO
from aiida.orm import SinglefileData
from aiida_shell import launch_shell_job
files = {
    'input': SinglefileData(StringIO('2\n5\n3')),
}
results, node = launch_shell_job(
    'sort',
    arguments=['{input}','--output', 'sorted'],
    files=files,
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
files = {
    'single_file': SinglefileData(StringIO('line 0\nline 1\nline 2\n')),
}
results, node = launch_shell_job(
    'split',
    arguments=['-l', '1', '{single_file}'],
    files=files,
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
