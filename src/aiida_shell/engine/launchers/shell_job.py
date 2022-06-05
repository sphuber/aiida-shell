# -*- coding: utf-8 -*-
"""Convenience wrapper function to simplify the interface to launch a :class:`aiida_shell.ShellJob` job."""
from __future__ import annotations

import logging
import pathlib
import tempfile
import typing as t

from aiida.common import exceptions
from aiida.engine import run_get_node
from aiida.orm import Code, Computer, Data, SinglefileData, load_code, load_computer
from aiida.plugins import CalculationFactory

__all__ = ('launch_shell_job',)

LOGGER = logging.getLogger('aiida_shell')


def launch_shell_job(
    command: str,
    nodes: dict[str, Data] | None = None,
    filenames: dict[str, str] | None = None,
    arguments: list[str] | None = None,
    outputs: list[str] | None = None,
    metadata: dict[str, t.Any] | None = None
):  # pylint: disable=too-many-arguments,too-many-locals
    """Launch a :class:`aiida_shell.ShellJob` job for the given command.

    :param command: The shell command to run. Should be the relative command name, e.g., ``date``.
    :param nodes: A dictionary of ``Data`` nodes whose content is to replace placeholders in the ``arguments`` list.
    :param filenames: Optional dictionary of explicit filenames to use for the ``nodes`` to be written to ``dirpath``.
    :param arguments: Optional list of command line arguments optionally containing placeholders for input nodes.
    :param outputs: Optional list of relative filenames that should be captured as outputs.
    :param metadata: Optional dictionary of metadata inputs to be passed to the ``ShellJob``.
    :raises TypeError: If the value specified for ``metadata.options.computer`` is not a ``Computer``.
    :raises ValueError: If the absolute path of the command on the computer could not be determined.
    """
    computer = prepare_computer((metadata or {}).get('options', {}).pop('computer', None))

    with computer.get_transport() as transport:
        status, stdout, stderr = transport.exec_command_wait(f'which {command}')
        executable = stdout.strip()

        if status != 0:
            raise ValueError(f'failed to determine the absolute path of the command on the computer: {stderr}')

    code_label = f'{command}@{computer.label}'

    try:
        code = load_code(code_label)
    except exceptions.NotExistent:
        LOGGER.warning('No code exists yet for `%s`, creating it now.', code_label)
        code = Code(  # type: ignore[assignment]
            label=command,
            remote_computer_exec=(computer, executable),
            input_plugin_name='core.shell'
        ).store()

    inputs = {
        'code': code,
        'nodes': convert_nodes_single_file_data(nodes or {}),
        'filenames': filenames or {},
        'arguments': arguments or [],
        'outputs': outputs or [],
        'metadata': metadata or {},
    }

    results, node = run_get_node(CalculationFactory('core.shell'), **inputs)  # type: ignore[arg-type]

    return {label: node for label, node in results.items() if isinstance(node, SinglefileData)}, node


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
    if computer is not None and not isinstance(computer, Computer):
        raise TypeError(f'`metadata.options.computer` should be instance of `Computer` but got: {type(computer)}.')

    if computer is None:
        LOGGER.warning('No computer specified, assuming `localhost`.')
        try:
            computer = load_computer('localhost')
        except exceptions.NotExistent:
            LOGGER.warning('No `localhost` computer exists yet: creating and configuring the `localhost` computer.')
            computer = Computer(
                label='localhost',
                hostname='localhost',
                description='Localhost automatically created by `aiida.engine.launch_shell_job`',
                transport_type='core.local',
                scheduler_type='core.direct',
                workdir=tempfile.gettempdir(),
            ).store()
            computer.configure(safe_interval=0.)
            computer.set_minimum_job_poll_interval(0.)

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
