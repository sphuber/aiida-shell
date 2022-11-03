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
import re

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

    @staticmethod
    def format_link_label(filename: str) -> str:
        """Format the link label from a given filename.

        Valid link labels can only contain alphanumeric characters and underscores, without consecutive underscores. So
        all characters that are not alphanumeric or an underscore are converted to underscores, where consecutive
        underscores are merged into one.

        :param filename: The filename.
        :returns: The link label.
        """
        alphanumeric = re.sub('[^0-9a-zA-Z_]+', '_', filename)
        link_label = re.sub('_[_]+', '_', alphanumeric)
        return link_label

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
                    if globbed.exists():
                        self.out(self.format_link_label(globbed.name), SinglefileData(globbed, filename=globbed.name))
                    else:
                        missing_output_files.append(globbed.name)
            else:
                filepath = dirpath / filename
                if filepath.exists():
                    self.out(self.format_link_label(filename), SinglefileData(filepath, filename=filename))
                else:
                    missing_output_files.append(filepath.name)

        return missing_output_files
