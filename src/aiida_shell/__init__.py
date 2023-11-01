"""AiiDA plugin that makes running shell commands easy."""
from .calculations import ShellJob  # noqa
from .data import ShellCode  # noqa
from .engine import launch_shell_job  # noqa
from .parsers import ShellParser  # noqa

__version__ = '0.5.3'
