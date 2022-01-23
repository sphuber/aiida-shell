# -*- coding: utf-8 -*-
"""Tests for the :mod:`aiida_shell` module."""
from packaging.version import Version, parse

import aiida_shell


def test_version():
    """Test that :attr:`aiida_shell.__version__` is a PEP-440 compatible version identifier."""
    assert hasattr(aiida_shell, '__version__')
    assert isinstance(aiida_shell.__version__, str)
    assert isinstance(parse(aiida_shell.__version__), Version)
