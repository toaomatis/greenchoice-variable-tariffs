"""Test component setup."""
import logging
import json
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry, load_fixture
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.greenchoice_variable_tariffs.const import DOMAIN
from tests.const import MOCK_CONFIG_ALL

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker,):
    response_dict = json.loads(load_fixture('01_response.json'))

    aioclient_mock.get('https://www.greenchoice.nl/umbraco/surface/quotation/GetQuotation',
                       json=response_dict,
                       headers={"Content-Type": "application/json"}, )
    
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG_ALL)
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    all_states = hass.states.get(entry.entry_id)
    _LOGGER.warn(f'{all_states=}')

    state = hass.states.get("sensor.greenchoice_electricity_normal_tariff")
    assert state
