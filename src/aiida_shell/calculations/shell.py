"""Implementation of :class:`aiida.engine.CalcJob` to make it easy to run an arbitrary shell command on a computer."""
from __future__ import annotations

import inspect
import pathlib
import typing as t

from aiida.common.datastructures import CalcInfo, CodeInfo
from aiida.common.folders import Folder
from aiida.engine import CalcJob, CalcJobProcessSpec
from aiida.orm import Data, Dict, FolderData, List, RemoteData, SinglefileData, to_aiida_type

from aiida_shell.data import EntryPointData, PickledData

__all__ = ('ShellJob',)


class ShellJob(CalcJob):
    """Implementation of :class:`aiida.engine.CalcJob` to run a simple shell command."""

    FILENAME_STATUS: str = 'status'
    FILENAME_STDERR: str = 'stderr'
    FILENAME_STDOUT: str = 'stdout'
    DEFAULT_RETRIEVED_TEMPORARY: tuple[str, ...] = (FILENAME_STATUS, FILENAME_STDERR, FILENAME_STDOUT)

    @classmethod
    def define(cls, spec: CalcJobProcessSpec) -> None:  # type: ignore[override]
        """Define the process specification.

        :param spec: The object to use to build up the process specification.
        """
        super().define(spec)
        spec.input_namespace('nodes', valid_type=Data, required=False, validator=cls.validate_nodes)
        spec.input('filenames', valid_type=Dict, required=False, serializer=to_aiida_type)
        spec.input(
            'arguments', valid_type=List, required=False, serializer=to_aiida_type, validator=cls.validate_arguments
        )
        spec.input('outputs', valid_type=List, required=False, serializer=to_aiida_type, validator=cls.validate_outputs)
        spec.input(
            'parser',
            valid_type=(EntryPointData, PickledData),
            required=False,
            serializer=cls.serialize_parser,
            validator=cls.validate_parser,
        )
        spec.input(
            'metadata.options.redirect_stderr',
            valid_type=bool,
            required=False,
            help='If set to ``True``, the stderr file descriptor is redirected to stdout.',
        )
        spec.input(
            'metadata.options.filename_stdin',
            valid_type=str,
            required=False,
            help='Filename that should be redirected to the shell command using the stdin file descriptor.',
        )
        spec.input(
            'metadata.options.additional_retrieve',
            required=False,
            valid_type=list,
            help='List of filepaths that are to be retrieved in addition to defaults and those specified in the '
            '`outputs` input. This is useful if files need to be retrieved for a custom `parser`.',
        )
        spec.input(
            'metadata.options.use_symlinks',
            default=False,
            valid_type=bool,
            help='When set to `True`, symlinks will be used for contents of `RemoteData` nodes in the `nodes` input as '
            'opposed to copying the contents to the working directory.',
        )
        spec.inputs['code'].required = True

        options = spec.inputs['metadata']['options']  # type: ignore[index]
        options['parser_name'].default = 'core.shell'  # type: ignore[index]
        options['resources'].default = {'num_machines': 1}  # type: ignore[index]

        spec.outputs.dynamic = True

        spec.exit_code(
            300,
            'ERROR_OUTPUT_STATUS_MISSING',
            message='Exit status could not be determined: exit status file was not retrieved.',
            invalidates_cache=True,
        )
        spec.exit_code(
            301,
            'ERROR_OUTPUT_STATUS_INVALID',
            message='Exit status could not be determined: exit status file does not contain a valid integer.',
            invalidates_cache=True,
        )
        spec.exit_code(
            302,
            'ERROR_OUTPUT_STDOUT_MISSING',
            message='The stdout file was not retrieved.',
            invalidates_cache=True,
        )
        spec.exit_code(
            303,
            'ERROR_OUTPUT_FILEPATHS_MISSING',
            message='One or more output files defined in the `outputs` input were not retrieved: {missing_filepaths}.',
            invalidates_cache=True,
        )
        spec.exit_code(
            310,
            'ERROR_PARSER_HOOK_EXCEPTED',
            message='Callable specified in the `parser` input excepted: {exception}.',
            invalidates_cache=True,
        )
        spec.exit_code(
            400, 'ERROR_COMMAND_FAILED', message='The command exited with a non-zero status: {status} {stderr}.'
        )
        spec.exit_code(
            410, 'ERROR_STDERR_NOT_EMPTY', message='The command exited with a zero status but the stderr was not empty.'
        )

    @classmethod
    def serialize_parser(cls, value: t.Any) -> EntryPointData | PickledData:
        """Convert the ``value`` to a ``PickledData`` or ``EntryPointData`` instance if possible.

        :param value: The object to serialize to a ``EntryPointData`` or ``PickledData`` instance.
        :raises TypeError: If the object is not a string or callable.
        """
        if callable(value):
            return PickledData(value)

        if isinstance(value, str):
            from aiida.plugins.entry_point import get_entry_point_from_string

            entry_point = get_entry_point_from_string(value)
            return EntryPointData(entry_point=entry_point)

        raise TypeError(f'`value` should be a string or callable but got: {type(value)}')

    @classmethod
    def validate_parser(cls, value: t.Any, _: t.Any) -> str | None:
        """Validate the ``parser`` input."""
        if not value:
            return None

        try:
            deserialized_parser = value.load()
        except ValueError as exception:
            return f'The parser specified in the `parser` could not be loaded: {exception}.'

        try:
            signature = inspect.signature(deserialized_parser)
        except TypeError as exception:
            return f'The `parser` is not a callable function: {exception}'

        parameters = list(signature.parameters.keys())

        if any(required_parameter not in parameters for required_parameter in ('self', 'dirpath')):
            correct_signature = '(self, dirpath: pathlib.Path) -> dict[str, Data]:'
            return f'The `parser` has an invalid function signature, it should be: {correct_signature}'

        return None

    @classmethod
    def validate_nodes(cls, value: t.Mapping[str, Data], _: t.Any) -> str | None:
        """Validate the ``nodes`` input."""
        for key, node in value.items():
            if isinstance(node, (FolderData, RemoteData, SinglefileData)):
                continue

            try:
                str(node.value)
            except AttributeError:
                cls_name = node.__class__.__name__
                return f'Unsupported node type for `{key}` in `nodes`: {cls_name} does not have the `value` property.'
            except Exception as exception:
                return f'Casting `value` to `str` for `{key}` in `nodes` excepted: {exception}'

        return None

    @classmethod
    def validate_arguments(cls, value: List, _: t.Any) -> str | None:
        """Validate the ``arguments`` input."""
        if not value:
            return None

        elements = value.get_list()

        if any(not isinstance(element, str) for element in elements):
            return 'all elements of the `arguments` input should be strings'

        if '<' in elements:
            var = 'metadata.options.filename_stdin'
            return f'`<` cannot be specified in the `arguments`; to redirect a file to stdin, use the `{var}` input.'

        if '>' in elements:
            return 'the symbol `>` cannot be specified in the `arguments`; stdout is automatically redirected.'

        return None

    @classmethod
    def validate_outputs(cls, value: List, _: t.Any) -> str | None:
        """Validate the ``outputs`` input."""
        if not value:
            return None

        for reserved in [cls.FILENAME_STATUS, cls.FILENAME_STDERR, cls.FILENAME_STDOUT]:
            if reserved in value:
                return f'`{reserved}` is a reserved output filename and cannot be used in `outputs`.'

        return None

    def _build_process_label(self) -> str:
        """Construct the process label that should be set on ``ProcessNode`` instances for this process class.

        Override the base implementation to include the full label of the ``Code`` which provides more useful info to
        the user, for example when looking at an overview of submitted processes.

        :returns: The process label to use for ``ProcessNode`` instances.
        """
        if self.inputs:
            return f'ShellJob<{self.inputs.code.full_label}>'
        return super()._build_process_label()

    def prepare_for_submission(self, folder: Folder) -> CalcInfo:
        """Prepare the calculation for submission.

        :param folder: A temporary folder on the local file system.
        :returns: A :class:`aiida.common.datastructures.CalcInfo` instance.
        """
        dirpath = pathlib.Path(folder._abspath)
        inputs: dict[str, t.Any]

        if self.inputs:
            inputs = dict(self.inputs)
        else:
            inputs = {}

        nodes = inputs.get('nodes', {})
        filenames = (inputs.get('filenames', None) or Dict()).get_dict()
        arguments = (inputs.get('arguments', None) or List()).get_list()
        outputs = (inputs.get('outputs', None) or List()).get_list()
        filename_stdin = inputs['metadata']['options'].get('filename_stdin', None)
        retrieve_list = (
            outputs + list(self.DEFAULT_RETRIEVED_TEMPORARY) + (self.node.get_option('additional_retrieve') or [])
        )

        processed_arguments = self.process_arguments_and_nodes(dirpath, nodes, filenames, arguments)

        # If an explicit filename for the stdin file descriptor is specified it should not be part of the command line
        # argument since the scheduler plugin is supposed to take care of this.
        if filename_stdin and filename_stdin in processed_arguments:
            processed_arguments.remove(filename_stdin)

        remote_copy_list, remote_symlink_list = self.handle_remote_data_nodes(inputs)

        code_info = CodeInfo()
        code_info.code_uuid = inputs['code'].uuid
        code_info.cmdline_params = processed_arguments
        code_info.stdin_name = filename_stdin
        code_info.stdout_name = self.node.get_option('output_filename') or self.FILENAME_STDOUT

        if self.node.get_option('redirect_stderr'):
            code_info.join_files = True
        else:
            code_info.stderr_name = self.FILENAME_STDERR

        calc_info = CalcInfo()
        calc_info.codes_info = [code_info]
        calc_info.append_text = f'echo $? > {self.FILENAME_STATUS}'
        calc_info.remote_copy_list = remote_copy_list
        calc_info.remote_symlink_list = remote_symlink_list
        calc_info.retrieve_temporary_list = retrieve_list
        calc_info.provenance_exclude_list = [p.name for p in dirpath.iterdir()]

        return calc_info

    @staticmethod
    def handle_remote_data_nodes(inputs: dict[str, Data]) -> tuple[list[t.Any], list[t.Any]]:
        """Handle a ``RemoteData`` that was passed in the ``nodes`` input.

        :param inputs: The inputs dictionary.
        :returns: A tuple of two lists, the ``remote_copy_list`` and the ``remote_symlink_list``.
        """
        use_symlinks: bool = inputs['metadata']['options']['use_symlinks']  # type: ignore[index]
        computer_uuid = inputs['code'].computer.uuid  # type: ignore[union-attr]
        remote_nodes = [node for node in inputs.get('nodes', {}).values() if isinstance(node, RemoteData)]
        instructions = [(computer_uuid, f'{node.get_remote_path()}/*', '.') for node in remote_nodes]

        if use_symlinks:
            return [], instructions

        return instructions, []

    def process_arguments_and_nodes(
        self, dirpath: pathlib.Path, nodes: dict[str, SinglefileData], filenames: dict[str, str], arguments: list[str]
    ) -> list[str]:
        """Process the command line arguments and input nodes.

        Loops over the list of arguments. If the argument is a placeholder, the ``nodes`` dictionary is searched for the
        same key and if found, the content of that node is processed. The manner in which the content is represented
        depends on the node type. For a ``SinglefileData``, the content is written to ``dirpath``. The key of the
        ``nodes`` dictionary is used as the relative filename, unless an explicit filename is defined in ``filenames``
        with the same key. The placeholder is then replaced with the path of the written file, relative to ``dirpath``.
        For all other node types, the ``value`` property is called which is cast to a ``str`` and is added as a command
        line argument by replacing the placeholder.

        After all arguments are processed, any remaining ``SinglefileData`` nodes in ``nodes`` are also written to
        ``dirpath`` using the same logic for determining the relative filename.

        :param dirpath: A temporary folder on the local file system.
        :param nodes: A dictionary of ``Data`` nodes whose content is to replace placeholders in the ``arguments`` list.
        :param filenames: A dictionary of explicit filenames to use for the ``nodes`` to be written to ``dirpath``.
        :param arguments: A list of command line arguments optionally containing placeholders for filenames.
        :returns: List of processed command line arguments.
        :raises ValueError: If any argument contains more than one placeholder.
        :raises ValueError: If ``nodes`` does not specify a node for a placeholder in ``arguments``.
        """
        from string import Formatter

        formatter = Formatter()
        processed_arguments = []
        processed_nodes = []

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

            if placeholder not in nodes:
                raise ValueError(f'argument placeholder `{{{placeholder}}}` not specified in `nodes`.')

            node = nodes[placeholder]

            if isinstance(node, SinglefileData):
                filename = self.write_single_file_data(dirpath, node, placeholder, filenames)
                argument_interpolated = argument.format(**{placeholder: filename})
            elif isinstance(node, FolderData):
                filename = self.write_folder_data(dirpath, node, placeholder, filenames)
                argument_interpolated = argument.format(**{placeholder: filename})
            elif isinstance(node, RemoteData):
                self.handle_remote_data(node)
            else:
                argument_interpolated = argument.format(**{placeholder: str(node.value)})

            processed_nodes.append(placeholder)
            processed_arguments.append(argument_interpolated)

        for key, node in nodes.items():
            if key in processed_nodes:
                continue

            if isinstance(node, SinglefileData):
                self.write_single_file_data(dirpath, node, key, filenames)
            elif isinstance(node, FolderData):
                self.write_folder_data(dirpath, node, key, filenames)

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
        default_filename = node.filename if node.filename and node.filename != SinglefileData.DEFAULT_FILENAME else key
        filename: str = filenames.get(key, default_filename)
        filepath = dirpath / filename

        filepath.parent.mkdir(parents=True, exist_ok=True)

        with node.open(mode='rb') as handle:
            filepath.write_bytes(handle.read())

        return filename

    @staticmethod
    def write_folder_data(dirpath: pathlib.Path, node: FolderData, key: str, filenames: dict[str, str]) -> str:
        """Write the content of a ``FolderData`` node to ``dirpath``.

        :param dirpath: A temporary folder on the local file system.
        :param node: The node whose content to write.
        :param key: The relative filename to use.
        :param filenames: Mapping that can provide explicit filenames for the given key.
        :returns: The relative filename used to write the content to ``dirpath``.
        """
        if key in filenames:
            filename = filenames[key]
            filepath = dirpath / filename
        else:
            filename = key
            filepath = dirpath

        filepath.parent.mkdir(parents=True, exist_ok=True)
        node.base.repository.copy_tree(filepath)

        return filename
