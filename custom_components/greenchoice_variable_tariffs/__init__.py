from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Greenchoice Variable Tariffs Sensor component."""
    # Return boolean to indicate that initialization was successfully.
    return True
