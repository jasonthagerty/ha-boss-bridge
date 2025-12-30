"""HA Boss Bridge - Expose automation configurations via REST API.

This custom integration provides REST API endpoints that expose full
automation, scene, and script configurations to external tools like HA Boss.
"""

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .api import AutomationsView, ScenesView, ScriptsView
from .const import DOMAIN, VERSION

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the HA Boss Bridge integration.

    Args:
        hass: Home Assistant instance
        config: Integration configuration

    Returns:
        True if setup succeeded
    """
    _LOGGER.info("Setting up HA Boss Bridge v%s", VERSION)

    # Register API endpoints
    hass.http.register_view(AutomationsView)
    hass.http.register_view(ScenesView)
    hass.http.register_view(ScriptsView)

    _LOGGER.info("HA Boss Bridge API endpoints registered")
    _LOGGER.debug("  - %s", AutomationsView.url)
    _LOGGER.debug("  - %s", ScenesView.url)
    _LOGGER.debug("  - %s", ScriptsView.url)

    return True
