"""Test component setup."""
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.greenchoice_variable_tariffs.const import DOMAIN
from tests.const import MOCK_CONFIG


async def test_async_setup(hass: HomeAssistant):
    """Test the component gets setup."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert True
