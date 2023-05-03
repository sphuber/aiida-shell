# -*- coding: utf-8 -*-
"""AiiDA plugin that makes running shell commands easy."""
from .calculations import ShellJob
from .data import ShellCode
from .engine import launch_shell_job
from .parsers import ShellParser

__version__ = '0.5.1'
