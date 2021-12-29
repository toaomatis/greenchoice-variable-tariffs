"""Constants for greenchoice_variable_tariffs tests."""
from custom_components.greenchoice_variable_tariffs.const import (
    CONF_POSTAL_CODE,
    CONF_USE_ELECTRICITY,
    CONF_USE_GAS,
    CONF_USE_LOW_TARIFF
)

# Mock config data to be used across multiple tests
MOCK_CONFIG = {
    CONF_POSTAL_CODE: "9999ZZ",
    CONF_USE_GAS: True,
    CONF_USE_LOW_TARIFF: True,
    CONF_USE_ELECTRICITY: True,
}
