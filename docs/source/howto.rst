.. _how-to:


=============
How-to guides
=============


Running a shell command
=======================

The most simple example is to run a shell command without any arguments:

.. code-block:: python

    from aiida_shell import launch_shell_job
    results, node = launch_shell_job('date')
    print(results['stdout'].get_content())

Which should print something like ``Thu 17 Mar 2022 10:49:52 PM CET``.


Running a shell command with arguments
======================================

To pass arguments to the shell command, pass them as a string to the ``arguments`` keyword:


.. code-block:: python

    from aiida_shell import launch_shell_job
    results, node = launch_shell_job(
        'date',
        arguments='--iso-8601'
    )
    print(results['stdout'].get_content())

which should print something like ``2022-03-17``.


Running a shell command with files as arguments
===============================================

For commands that take arguments that refer to files, pass those files using the ``nodes`` keyword.
The keyword takes a dictionary of ``SinglefileData`` nodes.
To specify where on the command line the files should be passed, use placeholder strings in the ``arguments`` keyword.

.. code-block:: python

    from io import StringIO
    from aiida.orm import SinglefileData
    from aiida_shell import launch_shell_job
    results, node = launch_shell_job(
        'cat',
        arguments='{file_a} {file_b}',
        nodes={
            'file_a': SinglefileData(StringIO('string a')),
            'file_b': SinglefileData(StringIO('string b')),
        }
    )
    print(results['stdout'].get_content())

which prints ``string astring b``.


Running a shell command with files as arguments with specific filenames
=======================================================================

The keys in the ``nodes`` dictionary can only use alphanumeric characters and underscores.
The keys will be used as the link label of the file in the provenance graph, and as the filename in the temporary directory in which the shell command will be executed.
Certain commands may require specific filenames, for example including a file extension, e.g., ``filename.txt``, but this cannot be used in the ``nodes`` arguments.
To specify explicit filenames that should be used in the running directory, make sure that the ``filename`` of the ``SinglefileData`` node is defined.
If the ``SinglefileData.filename`` was explicitly set when creating the node, that is the filename used to write the input file to the working directory:

.. code-block:: python

    from io import StringIO
    from aiida.orm import SinglefileData
    from aiida_shell import launch_shell_job
    results, node = launch_shell_job(
        'cat',
        arguments='{file_a}',
        nodes={
            'file_a': SinglefileData(StringIO('string a'), filename='filename.txt'),
        }
    )
    print(results['stdout'].get_content())

which prints ``string a``.

If the filename of the ``SinglefileData`` cannot be controlled, alternatively explicit filenames can be defined using the ``filenames`` argument:

.. code-block:: python

    from io import StringIO
    from aiida.orm import SinglefileData
    from aiida_shell import launch_shell_job
    results, node = launch_shell_job(
        'cat',
        arguments='{file_a}',
        nodes={
            'file_a': SinglefileData(StringIO('string a')),
        },
        filenames={
            'file_a': 'filename.txt'
        }
    )
    print(results['stdout'].get_content())

which prints ``string a``.
Filenames specified in the ``filenames`` input will override the filename of the ``SinglefileData`` nodes.
Any parent directories in the filepath, for example ``some/nested/path`` in the filename ``some/nested/path/file.txt``, will be automatically created.

The output filename can be anything except for ``stdout``, ``stderr`` and ``status``, which are reserved filenames.


Passing other ``Data`` types as input
=====================================

The ``nodes`` keyword does not only accept ``SinglefileData`` nodes, but it accepts also other ``Data`` types.
For these node types, the content returned by the ``value`` property is directly cast to ``str``, which is used to replace the corresponding placeholder in the ``arguments``.
So as long as the ``Data`` type implements this ``value`` property it should be supported.
Of course, whether it makes sense for the value of the node to be used directly as a command line argument for the shell job, is up to the user.
Typical useful examples, are the base types that ship with AiiDA, such as the ``Float``, ``Int`` and ``Str`` types:

.. code-block:: python

    from aiida.orm import Float, Int, Str
    from aiida_shell import launch_shell_job
    results, node = launch_shell_job(
        'echo',
        arguments='{float} {int} {string}',
        nodes={
            'float': Float(1.0),
            'int': Int(2),
            'string': Str('string'),
        },
    )
    print(results['stdout'].get_content())

which prints ``1.0 2 string``.
This example is of course contrived, but when combining it with other components of AiiDA, which typically return outputs of these form, they can be used directly as inputs for ``launch_shell_job`` without having to convert the values.
This ensures that provenance is kept.


Redirecting input file through stdin
====================================

Certain shell commands require input to be passed through the stdin file descriptor.
This is normally accomplished as follows:

.. code-block:: bash

    cat < input.txt

To reproduce this behaviour, the file that should be redirected through stdin can be defined using the ``metadata.option.filename_stdin`` input:

.. code-block:: python

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

which prints ``string a``.

N.B.: one might be tempted to simply define the ``arguments`` as ``'< {input}'``, but this won't work as the ``<`` symbol will be quoted and will be read as a literal command line argument, not as the redirection symbol.
This is why passing the ``<`` in the ``arguments`` input will result in a validation error.


Defining outputs
================

When the shell command is executed, AiiDA captures by default the content written to the stdout and stderr file descriptors.
The content is wrapped in a ``SinglefileData`` node and attached to the ``ShellJob`` with the ``stdout`` and ``stderr`` link labels, respectively.
Any other output files that need to be captured can be defined using the ``outputs`` keyword argument.

.. code-block:: python

    from io import StringIO
    from aiida.orm import SinglefileData
    from aiida_shell import launch_shell_job
    results, node = launch_shell_job(
        'sort',
        arguments='{input} --output sorted',
        nodes={
            'input': SinglefileData(StringIO('2\n5\n3')),
        },
        outputs=['sorted']
    )
    print(results['sorted'].get_content())

which prints ``2\n3\n5``.


Defining output files with globbing
===================================

When the exact output files that will be generated and need to be captured are not known in advance, one can use globbing.
Take for example the ``split`` command, which split a file into multiple files of a certain number of lines.
By default, each output file will follow the sequence ``xa``, ``xb``, ``xc`` etc. augmenting the last character alphabetically.
These output files can be captured by specifying the ``outputs`` as ``['x*']``:

.. code-block:: python

    from io import StringIO
    from aiida.orm import SinglefileData
    from aiida_shell import launch_shell_job
    results, node = launch_shell_job(
        'split',
        arguments='-l 1 {single_file}',
        nodes={
            'single_file': SinglefileData(StringIO('line 0\nline 1\nline 2\n')),
        },
        outputs=['x*']
    )
    print(results.keys())

which prints ``dict_keys(['xab', 'xaa', 'xac', 'stderr', 'stdout'])``.

### Defining output folders
When the command produces a folder with multiple output files, it is also possible to parse this as a single output node, instead of individual outputs for each file.
If a filepath specified in the ``outputs`` corresponds to a directory, it is attached as a ``FolderData`` that contains all its contents, instead of individual ``SinglefileData`` nodes.
For example, imagine a compressed tarball ``/some/path/archive.tar.gz`` that contains the folder ``sub_folder`` with a number of files in it.
The following example uncompresses the tarball and captures the uncompressed files in the ``sub_folder`` directory in the ``sub_folder`` output node:

.. code-block:: python

    from io import StringIO
    from aiida.orm import SinglefileData
    from aiida_shell import launch_shell_job
    results, node = launch_shell_job(
        'tar',
        arguments='-zxvf {archive}',
        nodes={
            'archive': SinglefileData('/some/path/archive.tar.gz'),
        },
        outputs=['sub_folder']
    )
    print(results.keys())

which prints ``dict_keys(['sub_folder', 'stderr', 'stdout'])``.
The contents of the folder can be retrieved from the node as follows:

.. code-block:: python

    for filename in results['sub_folder'].list_object_names():
        content = results['sub_folder'].get_object_content(filename)
        # or, if a file-like object is preferred to stream the content
        with results['sub_folder'].open(filename) as handle:
            content = handle.read()


Defining a specific computer
============================

By default the shell command ran by ``launch_shell_job`` will be executed on the localhost, i.e., the computer where AiiDA is running.
However, AiiDA also supports running commands on remote computers.
See the `AiiDA's documentation <https://aiida.readthedocs.io/projects/aiida-core/en/latest/howto/run_codes.html#how-to-set-up-a-computer>`_ for instructions to setting up and configuring a remote computer.
To specify what computer to use for a shell command, pass it as an option to the ``metadata`` keyword:

.. code-block:: python

    from aiida.orm import load_computer
    from aiida_shell import launch_shell_job
    results, node = launch_shell_job(
        'date',
        metadata={'options': {'computer': load_computer('some-computer')}}
    )
    print(results['stdout'].get_content())

Here you can use ``aiida.orm.load_computer`` to load the ``Computer`` instance from its label, PK or UUID.


Defining a pre-configured code
==============================

The first argument, ``command``, of ``launch_shell_job`` takes the name of the command to be run as a string.
Under the hood, this is automatically converted into an :class:`~aiida.orm.nodes.data.code.abstract.AbstractCode`.
The ``command`` argument also accepts a pre-configured code instance directly:

.. code-block:: python

    from aiida.orm import load_code
    from aiida_shell import launch_shell_job
    code = load_code('date@localhost')
    results, node = launch_shell_job(code)

This approach can be used as an alternative to the previous example where the target computer is specified through the `metadata` argument.


Running many shell jobs in parallel
===================================

By default the shell command ran by ``launch_shell_job`` is run blockingly; meaning that the Python interpreter is blocked from doing anything else until the shell command finishes.
This becomes inefficient if you need to run many shell commands.
If the shell commands are independent and can be run in parallel, it is possible to submit the jobs to AiiDA's daemon by setting ``submit=True``:

.. code-block:: python

    from aiida.engine.daemon.client import get_daemon_client
    from aiida_shell import launch_shell_job

    # Make sure the daemon is running
    get_daemon_client().start_daemon()

    nodes = []

    for arguments in ['string_one', 'string_two']:
        results, node = launch_shell_job(
            'echo',
            arguments=arguments,
            submit=True,
        )
        nodes.append(node)
        print(f'Submitted {node}')

The results returned by ``launch_shell_job`` will now just be an empty dictionary.
The reason is because the function returns immediately after submitting the job to the daemon at which point it isn't finished yet and so the results are not yet known.
To check on the status of the submitted jobs, you can use the ``verdi process list`` command of the CLI that ships with AiiDA.
Or you can do it programmatically:

.. code-block:: python

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


Custom output parsing
=====================

By default, all outputs will be parsed into ``SinglefileData`` nodes.
While convenient not having to define a parser manually, it can also be quite restrictive.
One of AiiDA's strong points is that it can store data in JSON form in a relational database, making it queryable, but the content of ``SinglefileData`` nodes is excluded from this functionality.

The ``parser`` keyword allows to define a "custom" parser, which is a function with the following signature:

.. code-block:: python

    def parser(self, dirpath: pathlib.Path) -> dict[str, Data]:
        """Parse any output file generated by the shell command and return it as any ``Data`` node."""


The following example shows how a custom parser can be implemented:

.. code-block:: python

    from aiida_shell import launch_shell_job

    def parser(self, dirpath):
        from aiida.orm import Str
        return {'string': Str((dirpath / 'stdout').read_text().strip())}

    results, node = launch_shell_job(
        'echo',
        arguments='some output',
        parser=parser
    )
    print(results['string'].value)

which prints ``some output``.

.. important::

    If the output file that is parsed by the custom parser is not any of the files that are retrieved by default, i.e., ``stdout``, ``stderr``, ``status`` and the filenames specified in the ``outputs`` input, it has to be specified in the ``metadata.options.additional_retrieve`` input:

    .. code-block:: python

        from io import StringIO
        from json import dumps
        from aiida_shell import launch_shell_job
        from aiida.orm import SinglefileData

        def parser(self, dirpath):
            """Parse the content of the ``results.json`` file and return as a ``Dict`` node."""
            import json
            from aiida.orm import Dict
            return {'json': Dict(json.load((dirpath / 'results.json').open()))}

        results, node = launch_shell_job(
            'cat',
            arguments='{json}',
            nodes={'json': SinglefileData(StringIO(dumps({'a': 1})))},
            parser=parser,
            metadata={
                'options': {
                    'output_filename': 'results.json',
                    'additional_retrieve': ['results.json']
                }
            }
        )
        print(results['json'].get_dict())

    which prints ``{'a': 1}``.
