"""Test component setup."""
from custom_components.greenchoice_variable_tariffs import async_setup


async def test_async_setup(hass):
    """Test the component gets setup."""
    assert await async_setup(hass, {}) is True
