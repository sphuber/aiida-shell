"""Tests for :mod:`aiida_shell.data.code`."""
import pytest
from aiida_shell.data.code import ShellCode


def test_constructor(generate_computer):
    """Test initializing an instance."""
    code = ShellCode(
        label='bash',
        computer=generate_computer(),
        filepath_executable='/bin/bash',
        default_calc_job_plugin='core.shell',
    )
    assert isinstance(code, ShellCode)


def test_constructor_invalid(generate_computer):
    """Test the constructor raises if ``default_calc_job_plugin`` is not ``core.shell``."""
    with pytest.raises(ValueError, match=r'`default_calc_job_plugin` has to be `core.shell`, but got: .*'):
        ShellCode(
            label='bash',
            computer=generate_computer(),
            filepath_executable='/bin/bash',
            default_calc_job_plugin='core.arithmetic.add',
        )


@pytest.mark.parametrize(
    ('value', 'exception'),
    (
        ('core.shell', None),
        ('core.arithmetic.add', r'`default_calc_job_plugin` has to be `core.shell`, but got: .*'),
    ),
)
def test_validate_default_calc_job_plugin(value, exception):
    """Test the constructor raises if ``default_calc_job_plugin`` is not ``core.shell``."""
    if exception:
        with pytest.raises(ValueError, match=exception):
            ShellCode.validate_default_calc_job_plugin(value)
    else:
        assert ShellCode.validate_default_calc_job_plugin(value) is None
