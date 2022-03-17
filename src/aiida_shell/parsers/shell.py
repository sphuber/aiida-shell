# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida-core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
"""Parser for a :class:`aiida_shell.ShellJob` job."""
from __future__ import annotations

import pathlib

from aiida.engine import ExitCode
from aiida.orm import SinglefileData
from aiida.parsers.parser import Parser

from aiida_shell.calculations.shell import ShellJob

__all__ = ('ShellParser',)


class ShellParser(Parser):
    """Parser for a :class:`aiida_shell.ShellJob` job."""

    def parse(self, **kwargs):
        """Parse the contents of the output files stored in the ``retrieved`` output node."""
        dirpath = pathlib.Path(kwargs['retrieved_temporary_folder'])

        missing_output_files = self.parse_custom_outputs(dirpath)
        exit_code = self.parse_default_outputs(dirpath)

        if missing_output_files:
            return self.exit_codes.ERROR_OUTPUT_FILES_MISSING.format(missing_files=', '.join(missing_output_files))

        return exit_code

    def parse_default_outputs(self, dirpath: pathlib.Path) -> ExitCode:
        """Parse the output files that should have been retrieved by default.

        :param dirpath: Directory containing the retrieved files.
        :returns: An exit code.
        """
        try:
            with (dirpath / ShellJob.FILENAME_STDERR).open(mode='rb') as handle:
                node_stderr = SinglefileData(handle, filename=ShellJob.FILENAME_STDERR)
        except FileNotFoundError:
            pass
        else:
            self.out(ShellJob.FILENAME_STDERR, node_stderr)

        try:
            with (dirpath / ShellJob.FILENAME_STDOUT).open(mode='rb') as handle:
                node_stdout = SinglefileData(handle, filename=ShellJob.FILENAME_STDOUT)
        except FileNotFoundError:
            return self.exit_codes.ERROR_OUTPUT_STDOUT_MISSING
        else:
            self.out(ShellJob.FILENAME_STDOUT, node_stdout)

        try:
            exit_status = int((dirpath / ShellJob.FILENAME_STATUS).read_text())
        except FileNotFoundError:
            return self.exit_codes.ERROR_OUTPUT_STATUS_MISSING
        except ValueError:
            return self.exit_codes.ERROR_OUTPUT_STATUS_INVALID

        if exit_status != 0:
            return self.exit_codes.ERROR_COMMAND_FAILED.format(status=exit_status, stderr=node_stderr.get_content())

        return ExitCode()

    def parse_custom_outputs(self, dirpath: pathlib.Path) -> list[str]:
        """Parse the output files that have been requested through the ``outputs`` input.

        :param dirpath: Directory containing the retrieved files.
        :returns: List of missing output files.
        """
        if 'outputs' not in self.node.inputs:
            return []

        missing_output_files = []

        for filename in self.node.inputs.outputs.get_list():
            if '*' in filename:
                for globbed in dirpath.glob(filename):
                    output_key = globbed.name.replace('.', '_')
                    if globbed.exists():
                        self.out(output_key, SinglefileData(globbed, filename=globbed.name))
                    else:
                        missing_output_files.append(globbed.name)
            else:
                output_key = filename.replace('.', '_')
                filepath = dirpath / filename
                if filepath.exists():
                    self.out(output_key, SinglefileData(filepath, filename=filename))
                else:
                    missing_output_files.append(filepath.name)

        return missing_output_files
