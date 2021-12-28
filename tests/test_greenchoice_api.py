"""Test component setup."""
from homeassistant.setup import async_setup_component

from custom_components.greenchoice_variable_tariffs.const import DOMAIN
from custom_components.greenchoice_variable_tariffs.sensor import GreenchoiceApiData


async def test_greenchoice_api(hass):
    """Test Greenchoice API."""
    api = GreenchoiceApiData('5126DH', True, True, False)
    api.update()
    result = api.result
    assert True
