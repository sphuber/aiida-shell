"""Convenience wrapper function to simplify the interface to launch a :class:`aiida_shell.ShellJob` job."""
from __future__ import annotations

import logging
import pathlib
import shlex
import tempfile
import typing as t
import warnings

from aiida.common import exceptions, lang
from aiida.common.warnings import AiidaDeprecationWarning
from aiida.engine import Process, WorkChain, launch
from aiida.orm import AbstractCode, Computer, Data, ProcessNode, SinglefileData, load_code, load_computer

from aiida_shell import ShellCode, ShellJob

from .calculations.shell import ParserFunctionType

__all__ = ('launch_shell_job',)

LOGGER = logging.getLogger('aiida_shell')


def launch_shell_job(  # noqa: PLR0913
    command: str | AbstractCode,
    arguments: list[str] | str | None = None,
    nodes: t.Mapping[str, str | pathlib.Path | Data] | None = None,
    filenames: dict[str, str] | None = None,
    outputs: list[str] | None = None,
    parser: ParserFunctionType | str | None = None,
    metadata: dict[str, t.Any] | None = None,
    submit: bool = False,
    resolve_command: bool = True,
) -> tuple[dict[str, Data], ProcessNode]:
    """Launch a :class:`aiida_shell.ShellJob` job for the given command.

    :param command: The shell command to run. Should be the relative command name, e.g., ``date``. An ``AbstractCode``
        instance will be automatically created for this command if it doesn't already exist. Alternatively, a pre-
        configured ``AbstractCode`` instance can be passed directly.
    :param arguments: Optional list of command line arguments optionally containing placeholders for input nodes. The
        arguments can also be specified as a single string. In this case, it will be split into separate parameters
        using ``shlex.split``.
    :param nodes: A dictionary of ``Data`` nodes whose content is to replace placeholders in the ``arguments`` list.
    :param filenames: Optional dictionary of explicit filenames to use for the ``nodes`` to be written to ``dirpath``.
    :param outputs: Optional list of relative filenames that should be captured as outputs.
    :param parser: Optional callable that can implement custom parsing logic of produced output files. Alternatively,
        a complete entry point, i.e. a string of the form ``{entry_point_group}:{entry_point_name}`` pointing to such a
        callable.
    :param metadata: Optional dictionary of metadata inputs to be passed to the ``ShellJob``.
    :param submit: Boolean, if ``True`` will submit the job to the daemon instead of running in current interpreter.
    :param resolve_command: Whether to resolve the command to the absolute path of the executable. If set to ``True``,
        the ``which`` command is executed on the target computer to attempt and determine the absolute path. Otherwise,
        the command is set as the ``filepath_executable`` attribute of the created ``AbstractCode`` instance.
    :raises TypeError: If the value specified for ``metadata.options.computer`` is not a ``Computer``.
    :raises ValueError: If ``resolve_command=True`` and the absolute path of the command on the computer could not be
        determined.
    :returns: The tuple of results dictionary and ``ProcessNode``, or just the ``ProcessNode`` if ``submit=True``. The
        results dictionary intentionally doesn't include the ``retrieved`` and ``remote_folder`` outputs as they are
        generated for each ``CalcJob`` and typically are not of interest to a user running ``launch_shell_job``. In
        order to not confuse them, these nodes are omitted, but they can always be accessed through the node.
    """
    inputs = prepare_shell_job_inputs(
        command=command,
        arguments=arguments,
        nodes=nodes,
        filenames=filenames,
        outputs=outputs,
        parser=parser,
        metadata=metadata,
        resolve_command=resolve_command,
    )

    if submit:
        current_process = Process.current()
        if current_process is not None and isinstance(current_process, WorkChain):
            return {}, current_process.submit(ShellJob, inputs)
        return {}, launch.submit(ShellJob, inputs)

    results, node = launch.run_get_node(ShellJob, inputs)

    return {label: node for label, node in results.items() if label not in ('retrieved', 'remote_folder')}, node


def prepare_shell_job_inputs(  # noqa: PLR0913
    command: str | AbstractCode,
    arguments: list[str] | str | None = None,
    nodes: t.Mapping[str, str | pathlib.Path | Data] | None = None,
    filenames: dict[str, str] | None = None,
    outputs: list[str] | None = None,
    parser: ParserFunctionType | str | None = None,
    metadata: dict[str, t.Any] | None = None,
    resolve_command: bool = True,
) -> dict[str, t.Any]:
    """Prepare inputs for the ShellJob based on the provided parameters.

    :param command: The shell command to run. Should be the relative command name, e.g., ``date``. An ``AbstractCode``
        instance will be automatically created for this command if it doesn't already exist. Alternatively, a pre-
        configured ``AbstractCode`` instance can be passed directly.
    :param arguments: Optional list of command line arguments optionally containing placeholders for input nodes. The
        arguments can also be specified as a single string. In this case, it will be split into separate parameters
        using ``shlex.split``.
    :param nodes: A dictionary of ``Data`` nodes whose content is to replace placeholders in the ``arguments`` list.
    :param filenames: Optional dictionary of explicit filenames to use for the ``nodes`` to be written to ``dirpath``.
    :param outputs: Optional list of relative filenames that should be captured as outputs.
    :param parser: Optional callable that can implement custom parsing logic of produced output files. Alternatively,
        a complete entry point, i.e. a string of the form ``{entry_point_group}:{entry_point_name}`` pointing to such a
        callable.
    :param metadata: Optional dictionary of metadata inputs to be passed to the ``ShellJob``.
    :param resolve_command: Whether to resolve the command to the absolute path of the executable. If set to ``True``,
        the ``which`` command is executed on the target computer to attempt and determine the absolute path. Otherwise,
        the command is set as the ``filepath_executable`` attribute of the created ``AbstractCode`` instance.
    :raises TypeError: If the value specified for ``metadata.options.computer`` is not a ``Computer``.
    :raises ValueError: If ``resolve_command=True`` and the absolute path of the command on the computer could not be
        determined.
    :returns: A dictionary containing prepared inputs for the ShellJob.
    """
    metadata = metadata or {}
    computer = metadata.get('options', {}).pop('computer', None)

    if computer:
        warnings.warn(
            'Specifying a computer through `metadata.options.computer` in `launch_shell_job` is deprecated. Please use '
            '`metadata.computer` instead.',
            AiidaDeprecationWarning,
            stacklevel=2,
        )
    else:
        computer = metadata.pop('computer', None)

    if isinstance(command, str):
        code = prepare_code(command, computer, resolve_command)
    else:
        lang.type_check(command, AbstractCode)
        code = command

    if isinstance(arguments, str):
        arguments = shlex.split(arguments)
    else:
        lang.type_check(arguments, list, allow_none=True)

    inputs = {
        'code': code,
        'nodes': convert_nodes_single_file_data(nodes or {}),
        'filenames': filenames,
        'arguments': arguments,
        'outputs': outputs,
        'parser': parser,
        'metadata': metadata or {},
    }

    return inputs


def prepare_code(command: str, computer: Computer | None = None, resolve_command: bool = True) -> AbstractCode:
    """Prepare a code for the given command and computer.

    This will automatically prepare the computer.

    :param command: The command that the code should represent. Can be the relative executable name or absolute path.
    :param computer: The computer on which the command should be run. If not defined the localhost will be used.
    :param resolve_command: Whether to resolve the command to the absolute path of the executable. If set to ``True``,
        the ``which`` command is executed on the target computer to attempt and determine the absolute path. Otherwise,
        the command is set as the ``filepath_executable`` attribute of the created ``AbstractCode`` instance.
    :return: A :class:`aiida.orm.nodes.code.abstract.AbstractCode` instance.
    :raises ValueError: If ``resolve_command=True`` and the code fails to determine the absolute path of the command.
    """
    computer = prepare_computer(computer)
    code_label = f'{command}@{computer.label}'

    try:
        code: AbstractCode = load_code(code_label)
    except exceptions.NotExistent as exception:
        LOGGER.info('No code exists yet for `%s`, creating it now.', code_label)

        if resolve_command:
            with computer.get_transport() as transport:
                status, stdout, stderr = transport.exec_command_wait(f'which "{command}"')
                executable = stdout.strip()

                if status != 0:
                    raise ValueError(
                        f'failed to determine the absolute path of the command on the computer: {stderr}'
                    ) from exception
        else:
            executable = command

        code = ShellCode(  # type: ignore[assignment]
            label=command, computer=computer, filepath_executable=executable, default_calc_job_plugin='core.shell'
        ).store()

    return code


def prepare_computer(computer: Computer | None = None) -> Computer:
    """Prepare and return a configured computer.

    If not computer is defined, the computer labeled ``localhost`` will be loaded. If that doesn't exist, it will be
    created, using ``core.local`` and ``core.direct`` as the entry points for the transport and scheduler type,
    respectively. In that case, the safe transport interval and the minimum job poll interval will both be set to 0
    seconds in order to guarantee a throughput that is as fast as possible.

    :param computer: The computer to prepare.
    :return: A configured computer.
    :raises TypeError: If the provided computer is not an instance of :class:`aiida.orm.Computer`.
    """
    from aiida.schedulers.datastructures import NodeNumberJobResource

    if computer is not None and not isinstance(computer, Computer):
        raise TypeError(f'`metadata.options.computer` should be instance of `Computer` but got: {type(computer)}.')

    if computer is None:
        LOGGER.info('No computer specified, assuming `localhost`.')
        try:
            computer = load_computer('localhost')
        except exceptions.NotExistent:
            LOGGER.info('No `localhost` computer exists yet: creating and configuring the `localhost` computer.')
            computer = Computer(
                label='localhost',
                hostname='localhost',
                description='Localhost automatically created by `aiida.engine.launch_shell_job`',
                transport_type='core.local',
                scheduler_type='core.direct',
                workdir=str(pathlib.Path(tempfile.gettempdir()) / 'aiida_shell_scratch'),
            ).store()
            computer.configure(safe_interval=0.0)
            computer.set_minimum_job_poll_interval(0.0)
            computer.set_default_mpiprocs_per_machine(1)
        else:
            if (
                issubclass(computer.get_scheduler().job_resource_class, NodeNumberJobResource)
                and computer.get_default_mpiprocs_per_machine() is None
            ):
                computer.set_default_mpiprocs_per_machine(1)
                LOGGER.warning(
                    f'{computer} already exist but does not define `default_mpiprocs_per_machine`. '
                    'Setting it to 1 since otherwise the `ShellJob` would fail during input validation.'
                )

    default_user = computer.backend.default_user

    if default_user and not computer.is_user_configured(default_user):
        computer.configure(default_user)

    return computer


def convert_nodes_single_file_data(nodes: t.Mapping[str, str | pathlib.Path | Data]) -> t.MutableMapping[str, Data]:
    """Convert ``str`` and ``pathlib.Path`` instances to ``SinglefileData`` nodes.

    :param nodes: Dictionary of ``Data``, ``str``, or ``pathlib.Path``.
    :raises TypeError: If a value in the mapping is of invalid type.
    :raises FileNotFoundError: If a filepath ``str`` or ``pathlib.Path`` does not correspond to existing file.
    :returns: Dictionary of filenames onto ``SinglefileData`` nodes.
    """
    processed_nodes: t.MutableMapping[str, Data] = {}

    for key, value in nodes.items():
        if isinstance(value, Data):
            processed_nodes[key] = value
            continue

        if isinstance(value, str):
            filepath = pathlib.Path(value)
        else:
            filepath = value

        if not isinstance(filepath, pathlib.Path):
            raise TypeError(
                f'received type {type(filepath)} for `{key}` in `nodes`. Should be `Data`, `str`, or `Path`.'
            )

        filepath.resolve()

        if not filepath.exists():
            raise FileNotFoundError(f'the path `{filepath}` specified in `nodes` does not exist.')

        with filepath.open('rb') as handle:
            processed_nodes[key] = SinglefileData(handle, filename=str(filepath.name))

    return processed_nodes
