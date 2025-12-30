"""HA Boss Bridge - Expose automation configurations via REST API.

This custom integration provides REST API endpoints that expose full
automation, scene, and script configurations to external tools like HA Boss.
"""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .api import AutomationsView, ScenesView, ScriptsView
from .const import DOMAIN, VERSION

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the HA Boss Bridge integration via YAML (legacy).

    Args:
        hass: Home Assistant instance
        config: Integration configuration

    Returns:
        True if setup succeeded
    """
    # Support YAML configuration for backward compatibility
    if DOMAIN in config:
        _LOGGER.info("Setting up HA Boss Bridge v%s via YAML", VERSION)
        await _register_endpoints(hass)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HA Boss Bridge from a config entry (UI configuration).

    Args:
        hass: Home Assistant instance
        entry: Config entry

    Returns:
        True if setup succeeded
    """
    _LOGGER.info("Setting up HA Boss Bridge v%s via UI", VERSION)
    await _register_endpoints(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.

    Args:
        hass: Home Assistant instance
        entry: Config entry

    Returns:
        True if unload succeeded
    """
    _LOGGER.info("Unloading HA Boss Bridge")
    return True


async def _register_endpoints(hass: HomeAssistant) -> None:
    """Register API endpoints.

    Args:
        hass: Home Assistant instance
    """
    # Register API endpoints
    hass.http.register_view(AutomationsView)
    hass.http.register_view(ScenesView)
    hass.http.register_view(ScriptsView)

    _LOGGER.info("HA Boss Bridge API endpoints registered")
    _LOGGER.debug("  - %s", AutomationsView.url)
    _LOGGER.debug("  - %s", ScenesView.url)
    _LOGGER.debug("  - %s", ScriptsView.url)
