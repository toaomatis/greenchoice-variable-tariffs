"""Test component setup."""

from custom_components.greenchoice_variable_tariffs.const import (
    SENSOR_MEASUREMENT_DATE,
    SENSOR_TYPE_GAS_TARIFF,
    SENSOR_TYPE_LOW_TARIFF,
    SENSOR_TYPE_NORMAL_TARIFF
)
from custom_components.greenchoice_variable_tariffs.sensor import GreenchoiceApiData
from tests.const import MOCK_CONFIG


async def test_greenchoice_api(hass):
    """Test Greenchoice API."""
    api = GreenchoiceApiData(**MOCK_CONFIG)
    api.async_update()
    result = api.result
    assert SENSOR_TYPE_NORMAL_TARIFF in result
    assert SENSOR_TYPE_LOW_TARIFF in result
    assert SENSOR_TYPE_GAS_TARIFF in result
    assert SENSOR_MEASUREMENT_DATE in result
