import logging
from datetime import (
    datetime,
    timedelta
)
from typing import Optional

import async_timeout
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_NAME,
    CURRENCY_EURO,
    DEVICE_CLASS_MONETARY,
    ENERGY_KILO_WATT_HOUR,
    STATE_UNKNOWN,
    VOLUME_CUBIC_METERS
)
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
from homeassistant.util import Throttle

from .const import (
    ATTR_MEASUREMENT_DATE,
    CONF_POSTAL_CODE,
    CONF_USE_ELECTRICITY,
    CONF_USE_GAS,
    CONF_USE_LOW_TARIFF,
    DEFAULT_NAME,
    DEFAULT_USE_ELECTRICITY,
    DEFAULT_USE_GAS,
    DEFAULT_USE_LOW_TARIFF,
    FRIENDLY_NAME_GAS_TARIFF,
    FRIENDLY_NAME_LOW_TARIFF,
    FRIENDLY_NAME_NORMAL_TARIFF,
    SENSOR_MEASUREMENT_DATE,
    SENSOR_TYPE_GAS_TARIFF,
    SENSOR_TYPE_LOW_TARIFF,
    SENSOR_TYPE_NORMAL_TARIFF
)

_LOGGER = logging.getLogger(__name__)
_RESOURCE = 'https://www.greenchoice.nl/umbraco/surface/quotation/GetQuotation'
# Time between updating data from Greenchoice API
SCAN_INTERVAL = timedelta(hours=12)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_POSTAL_CODE): cv.string,
    vol.Optional(CONF_USE_ELECTRICITY, default=DEFAULT_USE_ELECTRICITY): cv.boolean,
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
    use_electricity = config.get(CONF_USE_ELECTRICITY)
    use_low_tariff = config.get(CONF_USE_LOW_TARIFF)
    use_gas = config.get(CONF_USE_GAS)

    greenchoice_api = GreenchoiceApiData(hass, postal_code, use_electricity, use_low_tariff, use_gas)
    await greenchoice_api.async_update()
    if greenchoice_api is None:
        raise PlatformNotReady

    sensors = []
    if use_electricity is True:
        sensors.append(
            GreenchoiceEnergySensor(
                greenchoice_api,
                FRIENDLY_NAME_NORMAL_TARIFF,
                SENSOR_TYPE_NORMAL_TARIFF))

    if use_low_tariff is True:
        sensors.append(
            GreenchoiceEnergySensor(
                greenchoice_api,
                FRIENDLY_NAME_LOW_TARIFF,
                SENSOR_TYPE_LOW_TARIFF))

    if use_gas is True:
        sensors.append(
            GreenchoiceEnergySensor(
                greenchoice_api,
                FRIENDLY_NAME_GAS_TARIFF,
                SENSOR_TYPE_GAS_TARIFF))

    async_add_entities(sensors, update_before_add=True)


class GreenchoiceApiData:
    def __init__(self, hass: HomeAssistantType, postal_code: str, use_electricity: bool,
                 use_low_tariff: bool, use_gas: bool) -> None:
        self._resource = _RESOURCE
        self._hass = hass
        self._postal_code = postal_code
        self._use_electricity = use_electricity
        self._use_low_tariff = use_low_tariff
        self._use_gas = use_gas
        self.result = {}

    @Throttle(SCAN_INTERVAL)
    async def async_update(self):
        _LOGGER.debug(f'API Update')
        self.result = {}
        parameters = {'clusterId': 146, 'postcode': self._postal_code, 'huisnummer': 1}

        if self._use_electricity and self._use_low_tariff:
            parameters['verbruikStroomHoog'] = 450
            parameters['verbruikStroomLaag'] = 450
        elif self._use_electricity and not self._use_low_tariff:
            parameters['verbruikStroom'] = 450

        if self._use_gas:
            parameters['verbruikGas'] = 900

        _LOGGER.debug(f'{parameters=}')
        session = async_get_clientsession(self._hass)
        async with async_timeout.timeout(10):
            response = await session.get(_RESOURCE, data=parameters)
            _LOGGER.debug(f'Status: {response.status}')
            _LOGGER.debug(f"Content-type: {response.headers['content-type']}")

            json = await response.json()
            _LOGGER.debug(f"Body: {json=}")

        if json is None:
            return

        if 'result' not in json:
            return

        result = json['result']
        if 'producten' not in result:
            return

        products = result['producten']
        now = datetime.now()
        for product in products:
            if 'tarieven' not in product:
                pass

            tariffs = product['tarieven']
            for tariff in tariffs:
                key = tariff['key']
                if key == 'stroom-norm-allin' and self._use_electricity:
                    self.result[SENSOR_TYPE_NORMAL_TARIFF] = tariff['tariefInclBtw']
                if key == 'stroom-dal-allin' and self._use_low_tariff:
                    self.result[SENSOR_TYPE_LOW_TARIFF] = tariff['tariefInclBtw']
                if key == 'gas-levering-allin' and self._use_gas:
                    self.result[SENSOR_TYPE_GAS_TARIFF] = tariff['tariefInclBtw']

        self.result[SENSOR_MEASUREMENT_DATE] = now.isoformat()
        _LOGGER.debug(f'API Updated {self.result=}')


class GreenchoiceEnergySensor(Entity):
    """Greenchoice Energy Tariff Sensor representation."""

    def __init__(self,
                 greenchoice_api: GreenchoiceApiData,
                 name: str,
                 measurement_type: str):
        self._api = greenchoice_api
        self._name = name
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
    def device_class(self) -> str:
        return DEVICE_CLASS_MONETARY

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
        _LOGGER.debug(f'Sensor Update before API {self._measurement_type=}')
        await self._api.async_update(no_throttle=True)

        data = self._api.result
        _LOGGER.debug(f'Sensor Update after API {self._measurement_type=} {data=}')

        if data is None or self._measurement_type not in data:
            self._state = STATE_UNKNOWN
        else:
            self._state = data[self._measurement_type]
            self._measurement_date = data[SENSOR_MEASUREMENT_DATE]

        if self._measurement_type == SENSOR_TYPE_NORMAL_TARIFF:
            self._icon = 'mdi:lightning-bolt'
            self._unit_of_measurement = f'{CURRENCY_EURO}/{ENERGY_KILO_WATT_HOUR}'
        if self._measurement_type == SENSOR_TYPE_LOW_TARIFF:
            self._icon = 'mdi:lightning-bolt-outline'
            self._unit_of_measurement = f'{CURRENCY_EURO}/{ENERGY_KILO_WATT_HOUR}'
        if self._measurement_type == SENSOR_TYPE_GAS_TARIFF:
            self._icon = 'mdi:fire'
            self._unit_of_measurement = f'{CURRENCY_EURO}/{VOLUME_CUBIC_METERS}'
        _LOGGER.debug(f'Sensor Updated {self=}')
