# -*- coding: utf-8 -*-
"""Tests for the :mod:`aiida_shell.parsers.shell` module."""
import copy
import io

from aiida.orm import List, SinglefileData
import pytest

from aiida_shell.calculations.shell import ShellJob
from aiida_shell.parsers.shell import ShellParser


@pytest.fixture
def create_retrieved_temporary(tmp_path):
    """Create a temporary directory to serve as ``retrieved_temporary_folder``."""

    def factory(files=None):
        """Create a temporary directory to serve as ``retrieved_temporary_folder``.

        :param files: a mapping of files to write to the temporary folder. The keywords will be used as filename and
            the values correspond to the text to be written to the file. If the value is ``None``, the file will not be
            written at all. By default, the stdout file will be written as these are expected to always be written by
            any ``ShellJob`` execution and so the ``ShellParser`` requires it to be present.
        """
        files = copy.copy(files or {})

        if ShellJob.FILENAME_STDOUT not in files:
            files[ShellJob.FILENAME_STDOUT] = 'stdout content'

        if ShellJob.FILENAME_STATUS not in files:
            files[ShellJob.FILENAME_STATUS] = '0'

        for filename, content in files.items():
            if content is not None:
                (tmp_path / filename).write_text(content)

        return tmp_path

    return factory


def test_stdout(parse_calc_job, create_retrieved_temporary):
    """Test parsing of the stdout."""
    content_stdout = 'content stdout'
    retrieved_temporary = create_retrieved_temporary({ShellJob.FILENAME_STDOUT: content_stdout})
    node, results, calcfunction = parse_calc_job(filepath_retrieved_temporary=retrieved_temporary)

    assert calcfunction.is_finished_ok, calcfunction.exit_status
    assert isinstance(results[ShellJob.FILENAME_STDOUT], SinglefileData)
    assert results[ShellJob.FILENAME_STDOUT].get_content() == content_stdout


def test_stdout_missing(parse_calc_job, create_retrieved_temporary):
    """Test parser returns ``ERROR_OUTPUT_STDOUT_MISSING`` if the stdout file was not retrieved."""
    retrieved_temporary = create_retrieved_temporary({ShellJob.FILENAME_STDOUT: None})
    node, _, calcfunction = parse_calc_job(filepath_retrieved_temporary=retrieved_temporary)

    assert calcfunction.is_failed
    assert calcfunction.exit_status == node.process_class.exit_codes.ERROR_OUTPUT_STDOUT_MISSING.status


def test_status_missing(parse_calc_job, create_retrieved_temporary):
    """Test parser returns ``ERROR_OUTPUT_STATUS_MISSING`` if the status file was not retrieved."""
    retrieved_temporary = create_retrieved_temporary({ShellJob.FILENAME_STATUS: None})
    node, _, calcfunction = parse_calc_job(filepath_retrieved_temporary=retrieved_temporary)

    assert calcfunction.is_failed
    assert calcfunction.exit_status == node.process_class.exit_codes.ERROR_OUTPUT_STATUS_MISSING.status


def test_status_invalid(parse_calc_job, create_retrieved_temporary):
    """Test parser returns ``ERROR_OUTPUT_STATUS_INVALID`` if the status file does not contain a valid integer."""
    retrieved_temporary = create_retrieved_temporary({ShellJob.FILENAME_STATUS: 'invalid'})
    node, _, calcfunction = parse_calc_job(filepath_retrieved_temporary=retrieved_temporary)

    assert calcfunction.is_failed
    assert calcfunction.exit_status == node.process_class.exit_codes.ERROR_OUTPUT_STATUS_INVALID.status


def test_outputs(parse_calc_job, create_retrieved_temporary):
    """Test parsing of the outputs defined by the job."""
    files = {
        'filename_a': 'content_a',
        'filename_b': 'content_b',
    }
    inputs = {
        'outputs': List(list(files.keys()))
    }
    retrieved_temporary = create_retrieved_temporary(files)
    node, results, calcfunction = parse_calc_job(inputs=inputs, filepath_retrieved_temporary=retrieved_temporary)

    assert calcfunction.is_finished_ok

    for filename in files:
        assert isinstance(results[filename], SinglefileData)
        assert results[filename].get_content() == files[filename]


def test_outputs_missing(parse_calc_job, create_retrieved_temporary):
    """Test parser returns ``ERROR_OUTPUT_FILES_MISSING`` if a specified output file was not retrieved."""
    inputs = {
        'outputs': List(['filename_a'])
    }
    retrieved_temporary = create_retrieved_temporary()
    node, results, calcfunction = parse_calc_job(inputs=inputs, filepath_retrieved_temporary=retrieved_temporary)

    assert calcfunction.is_failed
    assert calcfunction.exit_status == node.process_class.exit_codes.ERROR_OUTPUT_FILES_MISSING.status
