"""Data plugin to store a reference to an entry point."""
from __future__ import annotations

import typing as t

from aiida.common.exceptions import EntryPointError
from aiida.common.lang import type_check
from aiida.common.log import AIIDA_LOGGER
from aiida.orm import Data
from aiida.plugins.entry_point import get_entry_point
from aiida.plugins.utils import PluginVersionProvider
from importlib_metadata import EntryPoint

__all__ = ('EntryPointData',)

LOGGER = AIIDA_LOGGER.getChild('entry_point')
VERSION_PROVIDER = PluginVersionProvider()


class EntryPointData(Data):
    """Data plugin to store a reference to an entry point."""

    KEY_ATTRIBUTES_NAME: str = 'name'
    """Attribute key that stores the ``name`` attribute of the wrapped entry point."""

    KEY_ATTRIBUTES_GROUP: str = 'group'
    """Attribute key that stores the ``group`` attribute of the wrapped entry point."""

    KEY_ATTRIBUTES_VALUE: str = 'value'
    """Attribute key that stores the ``value`` attribute of the wrapped entry point."""

    KEY_ATTRIBUTES_MODULE: str = 'module'
    """Attribute key that stores the ``module`` attribute of the wrapped entry point."""

    KEY_ATTRIBUTES_ATTR: str = 'attr'
    """Attribute key that stores the ``attr`` attribute of the wrapped entry point."""

    KEY_ATTRIBUTES_EXTRAS: str = 'extras'
    """Attribute key that stores the ``extras`` attribute of the wrapped entry point."""

    KEY_ATTRIBUTES_VERSION: str = 'version'
    """Attribute key that stores the version of the package that provided the entry point, if available."""

    def __init__(
        self,
        *,
        entry_point: EntryPoint | None = None,
        name: str | None = None,
        group: str | None = None,
        **kwargs: t.Any,
    ):
        """Construct a new instance.

        :raises TypeError: If the ``entry_point`` is provided and is not an instance of ``EntryPoint``.
        :raises ValueError: If the ``name`` and ``group`` cannot be resolved to an entry point that can be loaded.
        :raises ValueError: If the ``entry_point`` is inconsistent, i.e., its ``name`` and ``group`` do not correspond
            to an existing entry point or it corresponds to a different entry point.
        """
        super().__init__(**kwargs)

        if entry_point is None and (group is None or name is None):
            raise ValueError('Define either the `entry_point` directly or the `group` and `name`.')

        if entry_point:
            type_check(entry_point, EntryPoint)

        if not entry_point:
            assert group is not None and name is not None
            try:
                entry_point = get_entry_point(group, name)
            except EntryPointError as exception:
                raise ValueError(f'entry point with group `{group}` and name `{name}` does not exist.') from exception

        try:
            loaded = entry_point.load()
        except ModuleNotFoundError as exception:
            raise ValueError(f'entry point `{entry_point}` could not be loaded.') from exception

        try:
            reloaded = get_entry_point(entry_point.group, entry_point.name).load()
        except EntryPointError as exception:
            raise ValueError(
                f'Inconsistent entry point: the `name` and `group` of {entry_point} do not match any registered '
                'entry point.'
            ) from exception

        if loaded != reloaded:
            raise ValueError(
                f'Inconsistent entry point: the `name` and `group` of {entry_point} point to {reloaded} which does not '
                f'match the value `{entry_point.value}` of the specified entry point.'
            )

        keys = (
            self.KEY_ATTRIBUTES_NAME,
            self.KEY_ATTRIBUTES_GROUP,
            self.KEY_ATTRIBUTES_VALUE,
            self.KEY_ATTRIBUTES_MODULE,
            self.KEY_ATTRIBUTES_ATTR,
            self.KEY_ATTRIBUTES_EXTRAS,
        )
        attributes = {key: getattr(entry_point, key) for key in keys}
        attributes[self.KEY_ATTRIBUTES_VERSION] = VERSION_PROVIDER.get_version_info(loaded)['version'].get('plugin')
        self.base.attributes.set_many(attributes)

    def load(self) -> t.Any:
        """Load and return the wrapped entry point.

        :returns: The object that the entry point refers to.
        :raises EntryPointError: If the entry point does not exist or cannot be loaded.
        """
        attributes = self.base.attributes.all
        entry_point = EntryPoint(
            name=attributes[self.KEY_ATTRIBUTES_NAME],
            group=attributes[self.KEY_ATTRIBUTES_GROUP],
            value=attributes[self.KEY_ATTRIBUTES_VALUE],
        )
        return entry_point.load()
