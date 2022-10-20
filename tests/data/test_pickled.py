# -*- coding: utf-8 -*-
"""Tests for the :mod:`aiida_shell.data.pickled` module."""
from aiida.orm import Node, load_node
import dill
import pytest

from aiida_shell.data.pickled import PickledData


def test_constructor():
    """Test the constructor of :class:`~aiida_shell.data.pickled.PickledData`."""
    node = PickledData(None)
    assert isinstance(node, PickledData)


def test_get_unpickler_information():
    """Test :meth:`~aiida_shell.data.pickled.PickledData.get_unpickler_information`."""
    node = PickledData(None)
    assert node.get_unpickler_information() == ('dill._dill', 'loads', dill.__version__)


@pytest.mark.parametrize('obj', (None, 5, 'string', {'some': 'dict'}, Node))
def test_load(obj):
    """Test :meth:`~aiida_shell.data.pickled.PickledData.load`."""
    node = PickledData(obj)
    assert node.load() == obj

    node.store()
    assert node.load() == obj

    loaded = load_node(node.pk)
    assert loaded.load() == obj
