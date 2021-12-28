"""Test component setup."""
from homeassistant.setup import async_setup_component

from custom_components.greenchoice_variable_tariffs.const import DOMAIN, SENSOR_TYPE_NORMAL_TARIFF, \
    SENSOR_TYPE_LOW_TARIFF, SENSOR_TYPE_GAS_TARIFF, SENSOR_MEASUREMENT_DATE
from custom_components.greenchoice_variable_tariffs.sensor import GreenchoiceApiData
from tests.const import MOCK_CONFIG


async def test_greenchoice_api(hass):
    """Test Greenchoice API."""
    api = GreenchoiceApiData(**MOCK_CONFIG)
    api.update()
    result = api.result
    assert SENSOR_TYPE_NORMAL_TARIFF in result
    assert SENSOR_TYPE_LOW_TARIFF in result
    assert SENSOR_TYPE_GAS_TARIFF in result
    assert SENSOR_MEASUREMENT_DATE in result

