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


Running a shell command with folders as arguments
=================================================

Certain commands might require the presence of a folder of files in the working directory.
Just like a file is modeled in AiiDA's provenance graph by a ``SinglefileData`` node, a folder is represented by a ``FolderData`` node.
The following example shows how a ``FolderData`` can be created to contain multiple files and how it can be passed to ``launch_shell_job`` using the ``nodes`` argument:

.. code-block:: python

    import pathlib
    import tempfile
    from aiida.orm import FolderData
    from aiida_shell import launch_shell_job

    # First create a ``FolderData`` node with some arbitrary files
    with tempfile.TemporaryDirectory() as tmpdir:
        dirpath = pathlib.Path(tmpdir)
        (dirpath / 'file_a.txt').write_text('content a')
        (dirpath / 'file_b.txt').write_text('content b')
        folder_data = FolderData(tree=dirpath.absolute())

    results, node = launch_shell_job(
        'ls',
        nodes={
            'directory': folder_data,
        }
    )
    print(results['stdout'].get_content())

which prints:

.. code-block:: console

    _aiidasubmit.sh
    file_a.txt
    file_b.txt
    _scheduler-stderr.txt
    _scheduler-stdout.txt
    stderr
    stdout

The contents of the ``folder_data`` node, the ``file_a.txt`` and ``file_b.txt`` files, were copied to the working directory.

Note that by default, the contents of the ``FolderData`` are copied to the root of the working directory, as shown in the example above.
If the contents should be written to a directory inside the working directory, use the ``filenames`` argument, as is done for copying ``SinglefileData`` nodes.
Take for example the ``zip`` command that can create a zip archive from one or many files and folders.

.. code-block:: python

    import pathlib
    import tempfile
    from aiida.orm import FolderData
    from aiida_shell import launch_shell_job

    # First create a ``FolderData`` node with some arbitrary files
    with tempfile.TemporaryDirectory() as tmpdir:
        dirpath = pathlib.Path(tmpdir)
        (dirpath / 'file_a.txt').write_text('content a')
        (dirpath / 'file_b.txt').write_text('content b')
        folder_data = FolderData(tree=dirpath.absolute())

    results, node = launch_shell_job(
        'zip',
        arguments='-r archive.zip {folder}',
        outputs=['archive.zip'],
        nodes={
            'folder': folder_data,
        },
        filenames={
            'folder': 'directory'
        }
    )

In this example, the contents of the ``folder_data`` node were copied to the ``directory`` folder in the working directory.
The ``results`` dictionary contains the ``archive_zip`` output which is a ``SinglefileData`` node containing the zip archive.
It can be unzipped as follows: ``verdi node repo cat <IDENTIFIER> | unzip``, where ``<IDENTIFIER>`` should be replaced with the pk or UUID of the ``archive_zip`` node.
The original files ``file_a.txt`` and ``file_b.txt`` are now written to the current working directory.

.. note::

    It is not required for a ``FolderData`` node, that is specified in the ``nodes`` input, to have a corresponding placeholder in the ``arguments``.
    Just as with ``SinglefileData`` inputs nodes, if there is no corresponding placeholder, the contents of the folder are simply written to the working directory where the shell command is executed.
    This is useful for commands that expect a folder to be present in the working directory but whose name is not explicitly defined through a command line argument.


Running a shell command with remote data
========================================

Data that is stored on a remote computing resource, which is configured in AiiDA as a ``Computer``, can be represented in the provenance graph as a ``RemoteData`` node.
This can be useful if a job needs data that is already present on the computer where the job is to run.
AiiDA can simply make the remote data available in the working directory of the job without copying it through the local machine, which would be costly for large data.

For the purpose of an example, imagine there is a zip archive on a remote computer that needs to be unzipped.
In the following, the remote computer is actually the localhost to keep the example generic, but the concept applies to any ``Computer``:

.. code-block:: python

    import pathlib
    import shutil
    from aiida.orm import RemoteData, load_computer
    from aiida_shell import launch_shell_job

    # Create a temporary folder with the subdirectories ``archive`` and ``content``.
    dirpath = pathlib.Path.cwd() / 'tmp_folder'
    dirpath_archive = dirpath / 'archive'
    dirpath_content = dirpath / 'content'
    dirpath_archive.mkdir(parents=True)
    dirpath_content.mkdir(parents=True)

    # Write a dummy file ``content/file.txt`` and create an archive of the ``content`` dir as ``archive/archive.zip``.
    (dirpath_content / 'file.txt').write_text('content')
    shutil.make_archive((dirpath_archive / 'archive'), 'zip', dirpath_content)

    # Create a ``RemoteData`` node that points to the ``archive`` directory on the localhost.
    localhost = load_computer('localhost')
    remote_data = RemoteData(computer=localhost, remote_path=str(dirpath_archive.absolute()))

    results, node = launch_shell_job(
        'unzip',
        arguments='archive.zip',
        nodes={
            'remote_data': remote_data,
        },
        outputs=['file.txt']
    )
    print(results['file_txt'].get_content())

which prints ``content``.

.. tip::
    By default, the contents of the ``RemoteData`` nodes are *copied* to the working directory.
    This may be undesirable for large data, in which case the metadata option ``use_symlinks`` can be set to ``True`` to symlink the contents instead of copy it.

Any number of ``RemoteData`` nodes can be specified in the ``nodes`` input.
The entire content of each node will be recursively copied to the working directory.
It is currently not possible to select only parts of a ``RemoteData`` to be copied or to have it copied with a different filename to the working directory.

.. warning::
    If multiple ``RemoteData`` input nodes contain files with the same name, these files will be overwritten without warning.
    The same goes if the files overlap with any other files present in the job's working directory.


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


Redirecting stderr to the stdout file
=====================================

A common practice when running shell commands is to redirect the content, written to the stderr file descriptor, to stdout.
This is normally accomplished as follows:

.. code-block:: bash

    date > stdout 2>&1

To reproduce this behaviour, set the ``metadata.option.redirect_stderr`` input to ``True``:

.. code-block:: python

    from aiida_shell import launch_shell_job
    results, node = launch_shell_job(
        'date',
        metadata={'options': {'redirect_stderr': True}}
    )

If the option is not specified, or set to ``False``, the stderr will be redirected to the file named ``stderr``, as follows:

.. code-block:: bash

    date > stdout 2> stderr


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


Defining output folders
=======================

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

.. tip::

    If you find yourself reusing the same parser often, you can also register it with an entry point and use that for the ``parser`` input.
    See the `AiiDA documentation <https://aiida.readthedocs.io/projects/aiida-core/en/latest/howto/plugins_develop.html?highlight=entry%20point#registering-plugins-through-entry-points>`_ for details on how to register entry points.
    For example, if the parser is registered with the name ``some.parser`` in the group ``aiida.parsers``, the ``parser`` input will accept ``aiida.parsers:some.parser``.
    The entry point will automatically be validated and wrapped in a :class:`aiida_shell.data.entry_point.EntryPointData`.
