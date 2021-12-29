import logging
from datetime import datetime, timedelta
from typing import Optional

import aiohttp
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME, STATE_UNKNOWN, ATTR_UNIT_OF_MEASUREMENT
)
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
from homeassistant.util import Throttle

from .const import (
    CONF_POSTAL_CODE,
    CONF_USE_GAS,
    CONF_USE_LOW_TARIFF,
    CONF_USE_NORMAL_TARIFF,
    DEFAULT_NAME,
    DEFAULT_POSTAL_CODE,
    DEFAULT_USE_GAS,
    DEFAULT_USE_LOW_TARIFF,
    DEFAULT_USE_NORMAL_TARIFF,
    SENSOR_TYPE_NORMAL_TARIFF,
    SENSOR_TYPE_LOW_TARIFF,
    SENSOR_TYPE_GAS_TARIFF,
    SENSOR_MEASUREMENT_DATE, ATTR_MEASUREMENT_DATE,
)

_LOGGER = logging.getLogger(__name__)
_RESOURCE = 'https://www.greenchoice.nl/umbraco/surface/quotation/GetQuotation'
# Time between updating data from Greenchoice
SCAN_INTERVAL = timedelta(hours=12)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_POSTAL_CODE, default=DEFAULT_POSTAL_CODE): cv.string,
    vol.Optional(CONF_USE_NORMAL_TARIFF, default=DEFAULT_USE_NORMAL_TARIFF): cv.boolean,
    vol.Optional(CONF_USE_LOW_TARIFF, default=DEFAULT_USE_LOW_TARIFF): cv.boolean,
    vol.Optional(CONF_USE_GAS, default=DEFAULT_USE_GAS): cv.boolean,
})


async def async_setup_platform(
        hass: HomeAssistantType,
        config: ConfigType,
        async_add_entities: AddEntitiesCallback,
        discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""
    _LOGGER.debug(f'Async setup platform')
    name = config.get(CONF_NAME)
    postal_code = config.get(CONF_POSTAL_CODE)
    use_normal_tariff = config.get(CONF_USE_NORMAL_TARIFF)
    use_low_tariff = config.get(CONF_USE_LOW_TARIFF)
    use_gas = config.get(CONF_USE_GAS)

    greenchoice_api = GreenchoiceApiData(postal_code, use_normal_tariff, use_low_tariff, use_gas)
    await greenchoice_api.async_update()
    if greenchoice_api is None:
        raise PlatformNotReady

    sensors = []
    if use_normal_tariff is True:
        sensors.append(
            GreenchoiceEnergySensor(greenchoice_api, name, postal_code, use_normal_tariff, use_low_tariff, use_gas,
                                    SENSOR_TYPE_NORMAL_TARIFF))
    if use_low_tariff is True:
        sensors.append(
            GreenchoiceEnergySensor(greenchoice_api, name, postal_code, use_normal_tariff, use_low_tariff, use_gas,
                                    SENSOR_TYPE_LOW_TARIFF))
    if use_gas is True:
        sensors.append(
            GreenchoiceEnergySensor(greenchoice_api, name, postal_code, use_normal_tariff, use_low_tariff, use_gas,
                                    SENSOR_TYPE_GAS_TARIFF))
    async_add_entities(sensors, update_before_add=True)


class GreenchoiceApiData:
    def __init__(self, postal_code: str, use_normal_tariff: bool, use_low_tariff: bool, use_gas: bool) -> None:
        self._resource = _RESOURCE
        self._postal_code = postal_code
        self._use_normal_tariff = use_normal_tariff
        self._use_low_tariff = use_low_tariff
        self._use_gas = use_gas
        self.result = {}

    @Throttle(SCAN_INTERVAL)
    async def async_update(self):
        _LOGGER.debug(f'API Update')
        self.result = {}
        parameters = {}
        parameters['clusterId'] = 146
        parameters['postcode'] = self._postal_code
        parameters['huisnummer'] = 1

        if self._use_normal_tariff and self._use_low_tariff:
            parameters['verbruikStroomHoog'] = 450
            parameters['verbruikStroomLaag'] = 450
        elif self._use_normal_tariff or self._use_low_tariff:
            parameters['verbruikStroom'] = 450

        if self._use_gas:
            parameters['verbruikGas'] = 900
        _LOGGER.debug(f'{parameters=}')

        async with aiohttp.ClientSession() as session:
            async with session.get(_RESOURCE, data=parameters) as response:
                _LOGGER.debug(f'Status: {response.status}')
                _LOGGER.debug(f"Content-type: {response.headers['content-type']}")

                html = await response.json()
                _LOGGER.debug(f"Body: {html=}")

        now = datetime.now()
        self.result[SENSOR_TYPE_NORMAL_TARIFF] = now.minute * 2
        self.result[SENSOR_TYPE_LOW_TARIFF] = now.minute * 1
        self.result[SENSOR_TYPE_GAS_TARIFF] = now.minute * 3
        self.result[SENSOR_MEASUREMENT_DATE] = now.isoformat()
        _LOGGER.debug(f'API Updated {self.result=}')


class GreenchoiceEnergySensor(Entity):
    """Greenchoice Energy Tariff Sensor representation."""

    def __init__(self, greenchoice_api: GreenchoiceApiData, name, postal_code, use_normal_tariff, use_low_tariff,
                 use_gas,
                 measurement_type, ):
        self._api = greenchoice_api
        self._name = name
        self._postal_code = postal_code
        self._use_normal_tariff = use_normal_tariff
        self._use_low_tariff = use_low_tariff
        self._use_gas = use_gas
        self._measurement_type = measurement_type
        self._measurement_date = None
        self._unit_of_measurement = None
        self._state = None
        self._icon = None

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def postal_code(self) -> str:
        return self._postal_code

    @property
    def use_normal_tariff(self) -> bool:
        return self._use_normal_tariff

    @property
    def use_low_tariff(self) -> bool:
        return self._use_low_tariff

    @property
    def use_gas(self) -> bool:
        return self._use_gas

    @property
    def icon(self) -> str:
        return self._icon

    @property
    def state(self) -> str:
        return self._state

    @property
    def measurement_type(self) -> str:
        return self._measurement_type

    @property
    def measurement_date(self) -> str:
        return self._measurement_date

    @property
    def unit_of_measurement(self) -> str:
        return self._unit_of_measurement

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            ATTR_MEASUREMENT_DATE: self._measurement_date,
            ATTR_UNIT_OF_MEASUREMENT: self._unit_of_measurement
        }

    async def async_update(self) -> None:
        """Get the latest data from the Greenchoice API."""
        await self._api.async_update()

        data = self._api.result
        _LOGGER.debug(f'Sensor Update {self._measurement_type=}')

        if data is None or self._measurement_type not in data:
            self._state = STATE_UNKNOWN
        else:
            self._state = data[self._measurement_type]
            self._measurement_date = data[SENSOR_MEASUREMENT_DATE]

        if self._measurement_type == SENSOR_TYPE_NORMAL_TARIFF:
            self._icon = 'mdi:lightning-bolt'
            self._name = SENSOR_TYPE_NORMAL_TARIFF
            self._unit_of_measurement = "€"
        if self._measurement_type == SENSOR_TYPE_LOW_TARIFF:
            self._icon = 'mdi:lightning-bolt-outline'
            self._name = SENSOR_TYPE_LOW_TARIFF
            self._unit_of_measurement = "€"
        if self._measurement_type == SENSOR_TYPE_GAS_TARIFF:
            self._icon = 'mdi:fire'
            self._name = SENSOR_TYPE_GAS_TARIFF
            self._unit_of_measurement = "€"
        _LOGGER.debug(f'Sensor Updated {self=}')
