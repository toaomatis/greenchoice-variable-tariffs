"""Test component setup."""
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.greenchoice_variable_tariffs.const import DOMAIN


async def test_async_setup(hass):
    """Test the component gets setup."""
    assert await async_setup_component(hass, DOMAIN, {}) is True


async def test_sensor(hass):
    """Test sensor."""
    entry = MockConfigEntry(domain=DOMAIN, data={"name": "simple config",})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.example_temperature")

    assert state
    assert state.state == "23"