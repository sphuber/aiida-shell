# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""Tests for the :mod:`aiida_shell.data.entry_point` module."""
from aiida.orm import load_node
from aiida.plugins.entry_point import get_entry_point
from importlib_metadata import EntryPoint
import pytest

from aiida_shell.data.entry_point import EntryPointData

InvalidEntryPoint = EntryPoint('b', 'a', group='c')
InconsistentEntryPoint = EntryPoint('b', 'aiida_shell.data.pickled:PickledData', group='c')
DifferentEntryPoint = EntryPoint('core.entry_point', 'aiida_shell.data.pickled:PickledData', group='aiida.data')


@pytest.fixture
def entry_point():
    """Return a valid entry point."""
    return get_entry_point(group='aiida.data', name='core.entry_point')


def test_constructor(entry_point):
    """Test the constructor of :class:`~aiida_shell.data.entry_point.EntryPointData`."""
    node = EntryPointData(entry_point=entry_point)
    assert isinstance(node, EntryPointData)

    node = EntryPointData(group=entry_point.group, name=entry_point.name)
    assert isinstance(node, EntryPointData)


@pytest.mark.parametrize(
    'kwargs, exception, matches', (
        ({}, ValueError, r'Define either the `entry_point` directly or the `group` and `name`\.'),
        ({
            'group': 'some.group'
        }, ValueError, r'Define either the `entry_point` directly or the `group` and `name`\.'),
        ({
            'name': 'some.name'
        }, ValueError, r'Define either the `entry_point` directly or the `group` and `name`\.'),
        ({
            'entry_point': 'invalid_type'
        }, TypeError, r'Got object of type .*, expecting .*'),
        ({
            'group': 'a',
            'name': 'a'
        }, ValueError, r'entry point with group `a` and name `a` does not exist.'),
        ({
            'entry_point': InvalidEntryPoint
        }, ValueError, r'entry point .* could not be loaded.'),
        ({
            'entry_point': InconsistentEntryPoint
        }, ValueError, r'Inconsistent.*: the `name` and `group` of .* do not'),
        ({
            'entry_point': DifferentEntryPoint
        }, ValueError, r'Inconsistent.*: the `name` and `group` of .* point'),
    )
)
def test_constructor_invalid(kwargs, exception, matches):
    """Test the constructor of :class:`~aiida_shell.data.entry_point.EntryPointData`."""
    with pytest.raises(exception, match=matches):
        EntryPointData(**kwargs)


def test_load():
    """Test :meth:`~aiida_shell.data.entry_point.EntryPointData.load`."""
    node = EntryPointData(group='aiida.data', name='core.entry_point')
    assert node.load() == EntryPointData
    print(node.base.attributes.all)

    node.store()
    assert node.load() == EntryPointData

    loaded = load_node(node.pk)
    assert loaded.load() == EntryPointData


def test_version():
    """Test that the package version of the wrapped entry point is stored in the attributes."""
    from aiida_shell import __version__
    node = EntryPointData(group='aiida.data', name='core.entry_point')
    assert node.base.attributes.get(EntryPointData.KEY_ATTRIBUTES_VERSION) == __version__
