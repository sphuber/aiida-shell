"""Data plugin to store (almost) any Python object by pickling it."""
from __future__ import annotations

import importlib.metadata
import io
import typing as t

import dill
from aiida.common.log import AIIDA_LOGGER
from aiida.orm import SinglefileData

__all__ = ('PickledData',)

LOGGER = AIIDA_LOGGER.getChild('pickled_data')


class PickledData(SinglefileData):
    """Data plugin to store (almost) any Python object by pickling it."""

    KEY_ATTRIBUTES_UNPICKLER_MODULE: str = 'unpickler_module'
    """Attribute key that stores the module of the function that can unpickle this object."""

    KEY_ATTRIBUTES_UNPICKLER_NAME: str = 'unpickler_name'
    """Attribute key that stores the name of the function that can unpickle this object."""

    KEY_ATTRIBUTES_UNPICKLER_VERSION: str = 'pickler_version'
    """Attribute key that stores the version of the package whose function can unpickle this object."""

    PICKLER: t.Callable[[t.Any], bytes] = dill.dumps
    """The method used to pickle the Python object."""

    UNPICKLER: t.Callable[[bytes], t.Any] = dill.loads
    """The method used to unpickle the Python object."""

    def __init__(self, obj: t.Any):
        """Construct a new instance by pickling the provided Python object.

        :raises TypeError: If the Python object cannot be pickled.
        """
        try:
            pickled = self.get_pickler()(obj)
        except TypeError as exception:
            raise TypeError(f'object of type `{type(obj)}` is not supported') from exception

        super().__init__(file=io.BytesIO(pickled))

        self._set_unpickler_information()

    @classmethod
    def get_pickler(cls) -> t.Callable[[t.Any], bytes]:
        """Return the function that should be used to pickle the object stored by this node.

        :returns: A callable that is used to pickle the object to be stored by this node.
        """
        return cls.PICKLER

    def _set_unpickler_information(self) -> None:
        """Store the module, function and version of the package that can be used for unpickling this object.

        .. note:: If the version of the package cannot be determined, it will be set to ``None``.
        """
        unpickler = self.UNPICKLER
        package = unpickler.__module__.split('.', maxsplit=1)[0]

        try:
            version = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            version = None

        self.base.attributes.set(self.KEY_ATTRIBUTES_UNPICKLER_MODULE, unpickler.__module__)
        self.base.attributes.set(self.KEY_ATTRIBUTES_UNPICKLER_NAME, unpickler.__name__)
        self.base.attributes.set(self.KEY_ATTRIBUTES_UNPICKLER_VERSION, version)

    def get_unpickler_information(self) -> tuple[str, str, str]:
        """Return tuple of module name, function name and version of the package that can unpickle this object."""
        return (
            self.base.attributes.get(self.KEY_ATTRIBUTES_UNPICKLER_MODULE),
            self.base.attributes.get(self.KEY_ATTRIBUTES_UNPICKLER_NAME),
            self.base.attributes.get(self.KEY_ATTRIBUTES_UNPICKLER_VERSION),
        )

    def get_unpickler(self) -> t.Callable[[bytes], t.Any]:
        """Return the method to be used for unpickling the object.

        :returns: A callable that takes a number of bytes and unpickles it into the original Python object.
        :raises RuntimeError: If the required unpickling method could not be loaded.
        """
        module, name, version = self.get_unpickler_information()
        package = module.split('.', maxsplit=1)[0]

        try:
            unpickler_module = importlib.import_module(module)
        except ImportError as exception:
            raise RuntimeError(
                f'Could not import module `{module}` which should be able to unpickle this node.'
                f'Install `{package}=={version}` to install the required package.'
            ) from exception

        try:
            unpickler: t.Callable[[bytes], t.Any] = getattr(unpickler_module, name)
        except AttributeError as exception:
            raise RuntimeError(
                f'Could not load `{name}` from `{module} which should be able to unpickle this node.'
                f'Install `{package}=={version}` to install the required package.'
            ) from exception

        try:
            required_version = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            required_version = None

        try:
            unpickler_package = importlib.import_module(package)
            version = getattr(unpickler_package, '__version__')
        except ImportError:
            version = ''

        if version != required_version:
            LOGGER.info(
                f'Version of required unpickling module `{required_version}` does not match the one installed '
                f'`{version}`. It is possible that the unpickling may fail.'
            )

        return unpickler

    def load(self) -> t.Any:
        """Load the pickled Python object.

        :returns: The unpickled Python object.
        :raises ValueError: If the stored pickled object could not be unpickled.
        """
        with self.open(mode='rb') as handle:
            pickled = handle.read()

        try:
            unpickled = self.get_unpickler()(pickled)
        except Exception as exception:
            raise ValueError('The pickled object could not be unpickled.') from exception

        return unpickled
