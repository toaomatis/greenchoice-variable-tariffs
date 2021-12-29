"""Test component setup."""
import json
import os

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.greenchoice_variable_tariffs.const import (
    SENSOR_MEASUREMENT_DATE,
    SENSOR_TYPE_GAS_TARIFF,
    SENSOR_TYPE_LOW_TARIFF,
    SENSOR_TYPE_NORMAL_TARIFF
)
from custom_components.greenchoice_variable_tariffs.sensor import GreenchoiceApiData
from tests.const import MOCK_CONFIG


async def test_greenchoice_api(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, skip_setup: bool = False, ):
    """Test Greenchoice API."""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f'{dir_path}/fixtures/01_response.json') as f:
        response_dict = json.load(f)

    aioclient_mock.get('https://www.greenchoice.nl/umbraco/surface/quotation/GetQuotation', json=response_dict)
    api = GreenchoiceApiData(**MOCK_CONFIG)

    await api.async_update()
    result = api.result
    assert SENSOR_TYPE_NORMAL_TARIFF in result
    assert SENSOR_TYPE_LOW_TARIFF in result
    assert SENSOR_TYPE_GAS_TARIFF in result
    assert SENSOR_MEASUREMENT_DATE in result
