# -*- coding: utf-8 -*-
"""Implementation of :class:`aiida.engine.CalcJob` to make it easy to run an arbitrary shell command on a computer."""
from __future__ import annotations

import pathlib
import typing as t

from aiida.common.datastructures import CalcInfo, CodeInfo
from aiida.common.folders import Folder
from aiida.engine import CalcJob, CalcJobProcessSpec
from aiida.orm import Dict, List, SinglefileData, to_aiida_type

__all__ = ('ShellJob',)


class ShellJob(CalcJob):
    """Implementation of :class:`aiida.engine.CalcJob` to run a simple shell command."""

    FILENAME_STATUS: str = 'status'
    FILENAME_STDERR: str = 'stderr'
    FILENAME_STDOUT: str = 'stdout'
    DEFAULT_RETRIEVED_TEMPORARY: list[str] = [FILENAME_STATUS, FILENAME_STDERR, FILENAME_STDOUT]

    @classmethod
    def define(cls, spec: CalcJobProcessSpec):  # type: ignore[override]
        """Define the process specification.

        :param spec: The object to use to build up the process specification.
        """
        super().define(spec)
        spec.input_namespace('files', valid_type=SinglefileData, required=False)
        spec.input('filenames', valid_type=Dict, required=False, serializer=to_aiida_type)
        spec.input('arguments', valid_type=List, required=False, serializer=to_aiida_type)
        spec.input('outputs', valid_type=List, required=False, serializer=to_aiida_type)
        spec.inputs['code'].required = True

        options = spec.inputs['metadata']['options']  # type: ignore[index]
        options['parser_name'].default = 'core.shell'  # type: ignore[index]
        options['resources'].default = {'num_machines': 1, 'tot_num_mpiprocs': 1}  # type: ignore[index]

        spec.outputs.dynamic = True

        spec.exit_code(
            300,
            'ERROR_OUTPUT_STATUS_MISSING',
            message='Exit status could not be determined: exit status file was not retrieved.'
        )
        spec.exit_code(
            301,
            'ERROR_OUTPUT_STATUS_INVALID',
            message='Exit status could not be determined: exit status file does not contain a valid integer.'
        )
        spec.exit_code(302, 'ERROR_OUTPUT_STDOUT_MISSING', message='The stdout file was not retrieved.')
        spec.exit_code(
            303,
            'ERROR_OUTPUT_FILES_MISSING',
            message='One or more output files defined in the `outputs` input were not retrieved: {missing_files}.'
        )
        spec.exit_code(
            400, 'ERROR_COMMAND_FAILED', message='The command exited with a non-zero status: {status} {stderr}.'
        )

    def prepare_for_submission(self, folder: Folder) -> CalcInfo:
        """Prepare the calculation for submission.

        :param folder: A temporary folder on the local file system.
        :returns: A :class:`aiida.common.datastructures.CalcInfo` instance.
        """
        dirpath = pathlib.Path(folder._abspath)  # pylint: disable=protected-access
        inputs: dict[str, t.Any]

        if self.inputs:
            inputs = dict(self.inputs)
        else:
            inputs = {}

        files = inputs.get('files', {})
        filenames = (inputs.get('filenames', None) or Dict()).get_dict()
        arguments = (inputs.get('arguments', None) or List()).get_list()
        outputs = (inputs.get('outputs', None) or List()).get_list()

        code_info = CodeInfo()
        code_info.code_uuid = inputs['code'].uuid
        code_info.cmdline_params = self.process_arguments_and_files(dirpath, files, filenames, arguments)
        code_info.stderr_name = self.FILENAME_STDERR
        code_info.stdout_name = self.FILENAME_STDOUT

        calc_info = CalcInfo()
        calc_info.codes_info = [code_info]
        calc_info.append_text = f'echo $? > {self.FILENAME_STATUS}'
        calc_info.retrieve_temporary_list = outputs + self.DEFAULT_RETRIEVED_TEMPORARY

        return calc_info

    def process_arguments_and_files(
        self, dirpath: pathlib.Path, files: dict[str, SinglefileData], filenames: dict[str, str], arguments: list[str]
    ) -> list[str]:
        """Process the command line arguments and input files.

        Loops over the list of arguments. If the argument is a placeholder, the ``files`` dictionary is searched for the
        same key and if found, the content of that file is written to ``dirpath``. The key of the ``files`` dictionary
        is used as the relative filename, unless an explicit filename is defined in ``filenames`` with the same key. The
        placeholder is then replaced with the path of the written file, relative to ``dirpath``. After all arguments are
        processed, any remaining files in ``files`` are also written to ``dirpath`` using the same logic for determining
        the relative filename.

        :param dirpath: A temporary folder on the local file system.
        :param files: A dictionary of ``SinglefileData`` nodes. The content of the nodes is written to ``dirpath`` using
            the key as the relative filename, unless an explicit filename is defined in ``filenames`` with the same key.
        :param filenames: A dictionary of explicit filenames to use for the ``files`` to be written to ``dirpath``.
        :param arguments: A list of command line arguments optionally containing placeholders for filenames.
        :returns: List of processed command line arguments.
        :raises ValueError: If any argument contains more than one placeholder.
        :raises ValueError: If ``files`` does not specify a node for a placeholder in ``arguments``.
        """
        from string import Formatter

        formatter = Formatter()
        processed_arguments = []
        processed_files = []

        for argument in arguments:

            # Parse the argument for placeholders.
            field_names = [name for _, name, _, _ in formatter.parse(argument) if name]

            # If the argument contains no placeholders simply append the argument and continue.
            if not field_names:
                processed_arguments.append(argument)
                continue

            # Otherwise we validate that there is exactly one placeholder and that a ``SinglefileData`` input node is
            # specified in the keyword arguments. This is written to the current working directory and the filename is
            # used to replace the placeholder.
            if len(field_names) > 1:
                raise ValueError(f'argument `{argument}` is invalid as it contains more than one placeholder.')

            placeholder = field_names[0]

            if placeholder not in files:
                raise ValueError(f'argument placeholder `{{{placeholder}}}` not specified in `files`.')

            filename = self.write_single_file_data(dirpath, files[placeholder], placeholder, filenames)
            argument_interpolated = argument.format(**{placeholder: filename})

            processed_files.append(placeholder)
            processed_arguments.append(argument_interpolated)

        for key in filter(lambda key: key not in processed_files, files):
            self.write_single_file_data(dirpath, files[key], key, filenames)

        return processed_arguments

    @staticmethod
    def write_single_file_data(dirpath: pathlib.Path, node: SinglefileData, key: str, filenames: dict[str, str]) -> str:
        """Write the content of a ``SinglefileData`` node to ``dirpath``.

        :param dirpath: A temporary folder on the local file system.
        :param node: The node whose content to write.
        :param key: The relative filename to use.
        :param filenames: Mapping that can provide explicit filenames for the given key.
        :returns: The relative filename used to write the content to ``dirpath``.
        """
        filename = filenames.get(key, key)
        filepath = dirpath / filename

        with node.open(mode='rb') as handle:
            filepath.write_bytes(handle.read())

        return filename
