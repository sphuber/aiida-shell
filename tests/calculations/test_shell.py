# -*- coding: utf-8 -*-
"""Tests for the :mod:`aiida_shell.calculations.shell` module."""
import io

from aiida.common.datastructures import CodeInfo
from aiida.orm import List, SinglefileData
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
    assert list(dirpath.iterdir()) == []


def test_files(generate_calc_job, generate_code):
    """Test the ``files`` input."""
    inputs = {
        'code': generate_code(),
        'files': {
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


def test_filenames(generate_calc_job, generate_code):
    """Test the ``filenames`` input."""
    inputs = {
        'code': generate_code(),
        'files': {
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


@pytest.mark.parametrize(('arguments', 'exception'), (
    (['{place}{holder}'], r'argument `.*` is invalid as it contains more than one placeholder.'),
    (['{placeholder}'], r'argument placeholder `.*` not specified in `files`.'))
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
    inputs = {
        'code': generate_code(),
        'arguments': arguments
    }
    dirpath, calc_info = generate_calc_job('core.shell', inputs)
    code_info = calc_info.codes_info[0]
    assert code_info.cmdline_params == arguments.get_list()


def test_arguments_files(generate_calc_job, generate_code):
    """Test the ``arguments`` with placeholders for files."""
    arguments = List(['{file_a}'])
    inputs = {
        'code': generate_code(),
        'arguments': arguments,
        'files': {'file_a': SinglefileData(io.StringIO('content'))},
    }
    dirpath, calc_info = generate_calc_job('core.shell', inputs)
    code_info = calc_info.codes_info[0]
    assert code_info.cmdline_params == ['file_a']


def test_arguments_files_filenames(generate_calc_job, generate_code):
    """Test the ``arguments`` with placeholders for files and explicit filenames."""
    arguments = List(['{file_a}'])
    inputs = {
        'code': generate_code(),
        'arguments': arguments,
        'files': {'file_a': SinglefileData(io.StringIO('content'))},
        'filenames': {'file_a': 'custom_filename'}
    }
    dirpath, calc_info = generate_calc_job('core.shell', inputs)
    code_info = calc_info.codes_info[0]
    assert code_info.cmdline_params == ['custom_filename']
