from datetime import datetime, timedelta
import logging
from typing import Any, Callable, Dict, Optional

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME, 
    STATE_UNKNOWN
)
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
from homeassistant.util import Throttle

import voluptuous as vol

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
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)
# Time between updating data from GitHub
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
    async_add_entities: Callable,
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
    greenchoice_api.update()
    if greenchoice_api is None:
        raise PlatformNotReady
    
    sensors = []
    if use_normal_tariff is True:
        sensors.append(GreenchoiceEnergySensor(greenchoice_api, name, postal_code, use_normal_tariff, use_low_tariff, use_gas, SENSOR_TYPE_NORMAL_TARIFF))
    if use_low_tariff is True:
        sensors.append(GreenchoiceEnergySensor(greenchoice_api, name, postal_code, use_normal_tariff, use_low_tariff, use_gas, SENSOR_TYPE_LOW_TARIFF))
    if use_gas is True:
        sensors.append(GreenchoiceEnergySensor(greenchoice_api, name, postal_code, use_normal_tariff, use_low_tariff, use_gas, SENSOR_TYPE_GAS_TARIFF))
    async_add_entities(sensors, update_before_add=True)


class GreenchoiceApiData:
    def __init__(self, postal_code, use_normal_tariff, use_low_tariff, use_gas):
        self._resource = _RESOURCE
        self.result = {}

    @Throttle(SCAN_INTERVAL)
    def update(self):
        _LOGGER.debug(f'API Update')
        self.result = {}
        now = datetime.now()
        self.result[SENSOR_TYPE_NORMAL_TARIFF] = now.minute * 2
        self.result[SENSOR_TYPE_LOW_TARIFF] = now.minute * 1
        self.result[SENSOR_TYPE_GAS_TARIFF] = now.minute * 3
        self.result[SENSOR_MEASUREMENT_DATE] = now.isoformat()