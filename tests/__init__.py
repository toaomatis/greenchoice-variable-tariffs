"""Tests for the Greenchoice Variable Tariffs Sensor integration."""

import json
from unittest.mock import PropertyMock, patch
from pytest_homeassistant_custom_component.common import MockConfigEntry, load_fixture, patch_yaml_files

from custom_components.greenchoice_variable_tariffs.const import DOMAIN
from tests.const import MOCK_CONFIG_ALL


async def init_integration(
    hass, forecast=False, unsupported_icon=False
) -> MockConfigEntry:
    """Set up the AccuWeather integration in Home Assistant."""
    options = {}
    if forecast:
        options["forecast"] = True

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Home",
        unique_id="0123456",
        data=MOCK_CONFIG_ALL,
        options=options,
    )

    current = json.loads(load_fixture('01_response.json'))

    if unsupported_icon:
        current["WeatherIcon"] = 999

    # with patch(
    #     "homeassistant.components.greenchoice_variable_tariffs.GreenchoiceApiData.async_update",
    #     return_value=current,
    # ), patch(
    #     "homeassistant.components.greenchoice_variable_tariffs.AccuWeather.async_get_forecast",
    #     return_value=forecast,
    # ), patch(
    #     "homeassistant.components.greenchoice_variable_tariffs.AccuWeather.requests_remaining",
    #     new_callable=PropertyMock,
    #     return_value=10,
    # ):
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    return entry