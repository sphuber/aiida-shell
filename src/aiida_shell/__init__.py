"""AiiDA plugin that makes running shell commands easy."""
__version__ = '0.7.1'

from .calculations import ShellJob
from .data import EntryPointData, PickledData, ShellCode
from .launch import launch_shell_job
from .parsers import ShellParser

__all__ = (
    'ShellJob',
    'EntryPointData',
    'PickledData',
    'ShellCode',
    'launch_shell_job',
    'ShellParser',
)
