"""Test component setup."""
import json

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import load_fixture
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
    response_dict = json.loads(load_fixture('01_response.json'))

    aioclient_mock.get('https://www.greenchoice.nl/umbraco/surface/quotation/GetQuotation',
                       json=response_dict,
                       headers={"Content-Type": "application/json"}, )
    api = GreenchoiceApiData(hass, **MOCK_CONFIG)

    await api.async_update()
    result = api.result
    assert SENSOR_TYPE_NORMAL_TARIFF in result
    assert SENSOR_TYPE_LOW_TARIFF in result
    assert SENSOR_TYPE_GAS_TARIFF in result
    assert SENSOR_MEASUREMENT_DATE in result
