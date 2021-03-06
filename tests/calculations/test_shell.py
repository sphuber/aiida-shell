# -*- coding: utf-8 -*-
"""Tests for the :mod:`aiida_shell.calculations.shell` module."""
import io

from aiida.common.datastructures import CodeInfo
from aiida.orm import Data, Float, Int, List, SinglefileData, Str
import pytest

from aiida_shell.calculations.shell import ShellJob


def test_code(generate_calc_job, generate_code):
    """Test the ``code`` input."""
    code = generate_code()
    inputs = {'code': code}
    dirpath, calc_info = generate_calc_job('core.shell', inputs)

    assert len(calc_info.codes_info) == 1
    assert isinstance(calc_info.codes_info[0], CodeInfo)
    assert calc_info.codes_info[0].code_uuid == code.uuid
    assert calc_info.codes_info[0].cmdline_params == []
    assert calc_info.codes_info[0].stdout_name == ShellJob.FILENAME_STDOUT
    assert calc_info.retrieve_temporary_list == ShellJob.DEFAULT_RETRIEVED_TEMPORARY
    assert not list(dirpath.iterdir())


def test_nodes_single_file_data(generate_calc_job, generate_code):
    """Test the ``nodes`` input with ``SinglefileData`` nodes ."""
    inputs = {
        'code': generate_code(),
        'nodes': {
            'xa': SinglefileData(io.StringIO('content')),
            'xb': SinglefileData(io.StringIO('content')),
        }
    }
    dirpath, calc_info = generate_calc_job('core.shell', inputs)
    code_info = calc_info.codes_info[0]

    assert code_info.cmdline_params == []
    assert code_info.stdout_name == ShellJob.FILENAME_STDOUT
    assert calc_info.retrieve_temporary_list == ShellJob.DEFAULT_RETRIEVED_TEMPORARY
    assert sorted([p.name for p in dirpath.iterdir()]) == ['xa', 'xb']


def test_nodes_base_types(generate_calc_job, generate_code):
    """Test the ``nodes`` input with ``BaseType`` nodes ."""
    inputs = {
        'code': generate_code(),
        'arguments': ['{float}', '{int}', '{str}'],
        'nodes': {
            'float': Float(1.0),
            'int': Int(2),
            'str': Str('string'),
        }
    }
    _, calc_info = generate_calc_job('core.shell', inputs)
    code_info = calc_info.codes_info[0]

    assert code_info.cmdline_params == ['1.0', '2', 'string']
    assert code_info.stdout_name == ShellJob.FILENAME_STDOUT
    assert calc_info.retrieve_temporary_list == ShellJob.DEFAULT_RETRIEVED_TEMPORARY


def test_filenames(generate_calc_job, generate_code):
    """Test the ``filenames`` input."""
    inputs = {
        'code': generate_code(),
        'nodes': {
            'xa': SinglefileData(io.StringIO('content')),
            'xb': SinglefileData(io.StringIO('content')),
        },
        'filenames': {
            'xa': 'filename_a',
            'xb': 'filename_b',
        }
    }
    dirpath, calc_info = generate_calc_job('core.shell', inputs)
    code_info = calc_info.codes_info[0]

    assert code_info.cmdline_params == []
    assert code_info.stdout_name == ShellJob.FILENAME_STDOUT
    assert calc_info.retrieve_temporary_list == ShellJob.DEFAULT_RETRIEVED_TEMPORARY
    assert sorted([p.name for p in dirpath.iterdir()]) == ['filename_a', 'filename_b']


@pytest.mark.parametrize(
    'arguments, exception', (
        (['{place}{holder}'], r'argument `.*` is invalid as it contains more than one placeholder.'),
        (['{placeholder}'], r'argument placeholder `.*` not specified in `nodes`.'),
    )
)
def test_arguments_invalid(generate_calc_job, generate_code, arguments, exception):
    """Test the ``arguments`` input with invalid placeholders."""
    inputs = {
        'arguments': List(arguments),
        'code': generate_code(),
    }
    with pytest.raises(ValueError, match=exception):
        generate_calc_job('core.shell', inputs)


def test_arguments(generate_calc_job, generate_code):
    """Test the ``arguments`` input."""
    arguments = List(['-a', '--flag', 'local/filepath'])
    inputs = {'code': generate_code(), 'arguments': arguments}
    _, calc_info = generate_calc_job('core.shell', inputs)
    code_info = calc_info.codes_info[0]
    assert code_info.cmdline_params == arguments.get_list()


def test_arguments_files(generate_calc_job, generate_code):
    """Test the ``arguments`` with placeholders for inputs."""
    arguments = List(['{file_a}'])
    inputs = {
        'code': generate_code(),
        'arguments': arguments,
        'nodes': {
            'file_a': SinglefileData(io.StringIO('content'))
        },
    }
    _, calc_info = generate_calc_job('core.shell', inputs)
    code_info = calc_info.codes_info[0]
    assert code_info.cmdline_params == ['file_a']


def test_arguments_files_filenames(generate_calc_job, generate_code):
    """Test the ``arguments`` with placeholders for files and explicit filenames."""
    arguments = List(['{file_a}'])
    inputs = {
        'code': generate_code(),
        'arguments': arguments,
        'nodes': {
            'file_a': SinglefileData(io.StringIO('content'))
        },
        'filenames': {
            'file_a': 'custom_filename'
        }
    }
    _, calc_info = generate_calc_job('core.shell', inputs)
    code_info = calc_info.codes_info[0]
    assert code_info.cmdline_params == ['custom_filename']


@pytest.mark.parametrize(
    'outputs, message', (
        ([ShellJob.FILENAME_STATUS], r'`.*` is a reserved output filename and cannot be used in `outputs`.'),
        ([ShellJob.FILENAME_STDERR], r'`.*` is a reserved output filename and cannot be used in `outputs`.'),
        ([ShellJob.FILENAME_STDOUT], r'`.*` is a reserved output filename and cannot be used in `outputs`.'),
    )
)
def test_validate_outputs(generate_calc_job, generate_code, outputs, message):
    """Test the validator for the ``outputs`` argument."""
    with pytest.raises(ValueError, match=message):
        generate_calc_job('core.shell', {'code': generate_code(), 'outputs': outputs})


@pytest.mark.parametrize(
    'node_cls, message', (
        (Data, r'.*Unsupported node type for `.*` in `nodes`: .* does not have the `value` property.'),
        (Int, r'.*Casting `value` to `str` for `.*` in `nodes` excepted: .*'),
    )
)
def test_validate_nodes(generate_calc_job, generate_code, node_cls, message, monkeypatch):
    """Test the validator for the ``nodes`` argument."""
    nodes = {'node': node_cls()}

    if node_cls is Int:

        @property
        def value_raises(self):
            """Raise an exception."""
            raise ValueError()

        monkeypatch.setattr(node_cls, 'value', value_raises)

    with pytest.raises(ValueError, match=message):
        generate_calc_job('core.shell', {'code': generate_code(), 'nodes': nodes})
