# -*- coding: utf-8 -*-
"""Tests for the :mod:`aiida_shell.engine.launchers.shell_job` module."""
import datetime
import io
import pathlib

from aiida.orm import SinglefileData
import pytest

from aiida_shell.calculations.shell import ShellJob
from aiida_shell.engine.launchers.shell_job import launch_shell_job


def test_error_command_not_found():
    """Test :func:`aiida_shell.launch_shell_job` with non-existing ``command``."""
    with pytest.raises(ValueError, match=r'failed to determine the absolute path of the command on the computer.*'):
        launch_shell_job('unknown-command')


def test_error_command_failed():
    """Test that the shellfunction process fails if the command fails.

    Running ``tar`` without arguments should cause it to return a non-zero exit status.
    """
    _, node = launch_shell_job('tar')
    assert node.is_failed
    assert node.exit_status == ShellJob.exit_codes.ERROR_COMMAND_FAILED.status


def test_default():
    """Test :func:`aiida_shell.launch_shell_job` with default arguments."""
    results, node = launch_shell_job('date')
    assert node.is_finished_ok
    assert isinstance(results['stdout'], SinglefileData)
    assert results['stdout'].get_content()


def test_arguments():
    """Test a shellfunction that specifies positional CLI arguments.

    Have ``date`` print the current date without time in ISO 8601 format. Note that if we are very unlucky, the
    shellfunction runs just before midnight and the comparison ``datetime`` call runs in the next day causing the test
    to fail, but that seems extremely unlikely.
    """
    arguments = ['--iso-8601']
    results, node = launch_shell_job('date', arguments=arguments)

    assert node.is_finished_ok
    assert results['stdout'].get_content().strip() == datetime.datetime.now().strftime('%Y-%m-%d')


def test_files():
    """Test a shellfunction that specifies positional CLI arguments that are interpolated by the ``kwargs``."""
    content_a = 'content_a'
    content_b = 'content_b'
    files = {
        'file_a': SinglefileData(io.StringIO(content_a)),
        'file_b': SinglefileData(io.StringIO(content_b)),
    }
    arguments = ['{file_a}', '{file_b}']
    results, node = launch_shell_job('cat', arguments=arguments, files=files)

    assert node.is_finished_ok
    assert results['stdout'].get_content().strip() == content_a + content_b


@pytest.mark.parametrize('filename', ('filename.txt', pathlib.Path('filename.txt')))
def test_files_type(tmp_path, filename):
    """Test that ``files`` accepts ``str`` and ``pathlib.Path`` as values and converts them in ``SinglefileData``."""
    filepath = tmp_path / filename
    filepath.write_text('content')

    if isinstance(filename, str):
        results, node = launch_shell_job('cat', arguments=['{filename}'], files={'filename': str(filepath)})
    else:
        results, node = launch_shell_job('cat', arguments=['{filename}'], files={'filename': filepath})

    assert node.is_finished_ok
    assert results['stdout'].get_content() == 'content'


def test_files_invalid_type():
    """Test the function raises a ``TypeError`` for an invalid type in ``files``."""
    with pytest.raises(TypeError, match=r'received type .* for `filename` in `files`.*'):
        launch_shell_job('cat', files={'filename': True})


def test_files_not_exist():
    """Test the function raises a ``FileNotFoundError`` if a file in ``files`` does not exist."""
    with pytest.raises(FileNotFoundError, match=r'the path `.*` specified in `files` does not exist.'):
        launch_shell_job('cat', files={'filename': 'non-existing.txt'})


def test_arguments_files():
    """Test a shellfunction that specifies positional and keyword CLI arguments interpolated by the ``kwargs``."""
    content = 'line 1\nline 2'
    arguments = ['-n', '1', '{single_file}']
    files = {'single_file': SinglefileData(io.StringIO(content))}
    results, node = launch_shell_job('head', arguments=arguments, files=files)

    assert node.is_finished_ok
    assert results['stdout'].get_content().strip() == content.split('\n', maxsplit=1)[0]
