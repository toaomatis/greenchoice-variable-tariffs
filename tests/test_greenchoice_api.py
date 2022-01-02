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
from tests.const import (
    MOCK_CONFIG_ALL, 
    MOCK_CONFIG_ELECTRICITY,
    MOCK_CONFIG_ELECTRICITY_NORMAL,
    MOCK_CONFIG_GAS,
    MOCK_CONFIG_NONE
)


async def test_greenchoice_api_all(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, skip_setup: bool = False, ):
    """Test Greenchoice API for All sensors."""
    response_dict = json.loads(load_fixture('01_response.json'))

    aioclient_mock.get('https://www.greenchoice.nl/umbraco/surface/quotation/GetQuotation',
                       json=response_dict,
                       headers={"Content-Type": "application/json"}, )
    api = GreenchoiceApiData(hass, **MOCK_CONFIG_ALL)

    await api.async_update()
    result = api.result
    assert SENSOR_TYPE_NORMAL_TARIFF in result
    assert SENSOR_TYPE_LOW_TARIFF in result
    assert SENSOR_TYPE_GAS_TARIFF in result
    assert SENSOR_MEASUREMENT_DATE in result
    assert result[SENSOR_TYPE_NORMAL_TARIFF] == 0.5367
    assert result[SENSOR_TYPE_LOW_TARIFF] == 0.4136
    assert result[SENSOR_TYPE_GAS_TARIFF] == 2.0485


async def test_greenchoice_api_electricity(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, skip_setup: bool = False, ):
    """Test Greenchoice API for Electricity sensors."""
    response_dict = json.loads(load_fixture('01_response.json'))

    aioclient_mock.get('https://www.greenchoice.nl/umbraco/surface/quotation/GetQuotation',
                       json=response_dict,
                       headers={"Content-Type": "application/json"}, )
    api = GreenchoiceApiData(hass, **MOCK_CONFIG_ELECTRICITY)

    await api.async_update()
    result = api.result
    assert SENSOR_TYPE_NORMAL_TARIFF in result
    assert SENSOR_TYPE_LOW_TARIFF in result
    assert SENSOR_TYPE_GAS_TARIFF not in result
    assert SENSOR_MEASUREMENT_DATE in result
    assert result[SENSOR_TYPE_NORMAL_TARIFF] == 0.5367
    assert result[SENSOR_TYPE_LOW_TARIFF] == 0.4136


async def test_greenchoice_api_electricity_normal(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, skip_setup: bool = False, ):
    """Test Greenchoice API for Electricity sensors."""
    response_dict = json.loads(load_fixture('01_response.json'))

    aioclient_mock.get('https://www.greenchoice.nl/umbraco/surface/quotation/GetQuotation',
                       json=response_dict,
                       headers={"Content-Type": "application/json"}, )
    api = GreenchoiceApiData(hass, **MOCK_CONFIG_ELECTRICITY_NORMAL)

    await api.async_update()
    result = api.result
    assert SENSOR_TYPE_NORMAL_TARIFF in result
    assert SENSOR_TYPE_LOW_TARIFF not in result
    assert SENSOR_TYPE_GAS_TARIFF not in result
    assert SENSOR_MEASUREMENT_DATE in result
    assert result[SENSOR_TYPE_NORMAL_TARIFF] == 0.5367


async def test_greenchoice_api_gas(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, skip_setup: bool = False, ):
    """Test Greenchoice API for Electricity sensors."""
    response_dict = json.loads(load_fixture('01_response.json'))

    aioclient_mock.get('https://www.greenchoice.nl/umbraco/surface/quotation/GetQuotation',
                       json=response_dict,
                       headers={"Content-Type": "application/json"}, )
    api = GreenchoiceApiData(hass, **MOCK_CONFIG_GAS)

    await api.async_update()
    result = api.result
    assert SENSOR_TYPE_NORMAL_TARIFF not in result
    assert SENSOR_TYPE_LOW_TARIFF not in result
    assert SENSOR_TYPE_GAS_TARIFF in result
    assert SENSOR_MEASUREMENT_DATE in result
    assert result[SENSOR_TYPE_GAS_TARIFF] == 2.0485


async def test_greenchoice_api_none(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, skip_setup: bool = False, ):
    """Test Greenchoice API for Electricity sensors."""
    response_dict = json.loads(load_fixture('01_response.json'))

    aioclient_mock.get('https://www.greenchoice.nl/umbraco/surface/quotation/GetQuotation',
                       json=response_dict,
                       headers={"Content-Type": "application/json"}, )
    api = GreenchoiceApiData(hass, **MOCK_CONFIG_NONE)

    await api.async_update()
    result = api.result
    assert SENSOR_TYPE_NORMAL_TARIFF not in result
    assert SENSOR_TYPE_LOW_TARIFF not in result
    assert SENSOR_TYPE_GAS_TARIFF not in result
    assert SENSOR_MEASUREMENT_DATE in result


async def test_greenchoice_api_empty_response(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, skip_setup: bool = False, ):
    """Test Greenchoice API for Electricity sensors."""
    aioclient_mock.get('https://www.greenchoice.nl/umbraco/surface/quotation/GetQuotation',
                       json='{}',
                       headers={"Content-Type": "application/json"}, )
    api = GreenchoiceApiData(hass, **MOCK_CONFIG_ALL)

    await api.async_update()
    result = api.result
    assert result == {}


async def test_greenchoice_api_result_response(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, skip_setup: bool = False, ):
    """Test Greenchoice API for Electricity sensors."""
    response_dict = json.loads(load_fixture('02_response.json'))

    aioclient_mock.get('https://www.greenchoice.nl/umbraco/surface/quotation/GetQuotation',
                       json=response_dict,
                       headers={"Content-Type": "application/json"}, )
    api = GreenchoiceApiData(hass, **MOCK_CONFIG_ALL)

    await api.async_update()
    result = api.result
    assert result == {}