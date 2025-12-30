"""REST API views for HA Boss Bridge."""

import logging
from typing import Any

from aiohttp import web
from homeassistant.components.automation import DOMAIN as AUTOMATION_DOMAIN
from homeassistant.components.http import HomeAssistantView
from homeassistant.components.scene import DOMAIN as SCENE_DOMAIN
from homeassistant.components.script import DOMAIN as SCRIPT_DOMAIN
from homeassistant.core import HomeAssistant

from .const import API_AUTOMATIONS, API_SCENES, API_SCRIPTS, VERSION

_LOGGER = logging.getLogger(__name__)


class AutomationsView(HomeAssistantView):
    """API view to expose full automation configurations."""

    url = API_AUTOMATIONS
    name = "api:ha_boss_bridge:automations"
    requires_auth = True  # Require Home Assistant authentication

    async def get(self, request: web.Request) -> web.Response:
        """Get all automation configurations.

        Returns:
            JSON response with full automation configs
        """
        hass: HomeAssistant = request.app["hass"]

        # Verify user is admin (security check)
        if not request["hass_user"].is_admin:
            _LOGGER.warning(
                "Unauthorized access attempt to automations API from user %s",
                request["hass_user"].name,
            )
            return self.json({"error": "Unauthorized - admin access required"}, status_code=403)

        try:
            automations = await _get_automations(hass)
            return self.json(
                {
                    "automations": automations,
                    "bridge_version": VERSION,
                    "instance_id": _get_instance_id(hass),
                    "count": len(automations),
                }
            )
        except Exception as e:
            _LOGGER.exception("Failed to retrieve automations")
            return self.json({"error": f"Failed to retrieve automations: {e}"}, status_code=500)


class ScenesView(HomeAssistantView):
    """API view to expose full scene configurations."""

    url = API_SCENES
    name = "api:ha_boss_bridge:scenes"
    requires_auth = True

    async def get(self, request: web.Request) -> web.Response:
        """Get all scene configurations.

        Returns:
            JSON response with full scene configs
        """
        hass: HomeAssistant = request.app["hass"]

        if not request["hass_user"].is_admin:
            _LOGGER.warning(
                "Unauthorized access attempt to scenes API from user %s",
                request["hass_user"].name,
            )
            return self.json({"error": "Unauthorized - admin access required"}, status_code=403)

        try:
            scenes = await _get_scenes(hass)
            return self.json(
                {
                    "scenes": scenes,
                    "bridge_version": VERSION,
                    "instance_id": _get_instance_id(hass),
                    "count": len(scenes),
                }
            )
        except Exception as e:
            _LOGGER.exception("Failed to retrieve scenes")
            return self.json({"error": f"Failed to retrieve scenes: {e}"}, status_code=500)


class ScriptsView(HomeAssistantView):
    """API view to expose full script configurations."""

    url = API_SCRIPTS
    name = "api:ha_boss_bridge:scripts"
    requires_auth = True

    async def get(self, request: web.Request) -> web.Response:
        """Get all script configurations.

        Returns:
            JSON response with full script configs
        """
        hass: HomeAssistant = request.app["hass"]

        if not request["hass_user"].is_admin:
            _LOGGER.warning(
                "Unauthorized access attempt to scripts API from user %s",
                request["hass_user"].name,
            )
            return self.json({"error": "Unauthorized - admin access required"}, status_code=403)

        try:
            scripts = await _get_scripts(hass)
            return self.json(
                {
                    "scripts": scripts,
                    "bridge_version": VERSION,
                    "instance_id": _get_instance_id(hass),
                    "count": len(scripts),
                }
            )
        except Exception as e:
            _LOGGER.exception("Failed to retrieve scripts")
            return self.json({"error": f"Failed to retrieve scripts: {e}"}, status_code=500)


async def _get_automations(hass: HomeAssistant) -> list[dict[str, Any]]:
    """Extract automation configurations from Home Assistant.

    Args:
        hass: Home Assistant instance

    Returns:
        List of automation dictionaries with full configs
    """
    automations = []

    # Get automation component
    automation_component = hass.data.get(AUTOMATION_DOMAIN)
    if not automation_component:
        _LOGGER.debug("Automation component not found")
        return automations

    # Iterate through automation entities
    for entity in automation_component.entities:
        try:
            entity_id = entity.entity_id
            state = hass.states.get(entity_id)

            if not state:
                _LOGGER.debug("No state found for automation %s", entity_id)
                continue

            # Extract full configuration from entity
            automation_data = {
                "entity_id": entity_id,
                "friendly_name": state.attributes.get("friendly_name", entity.name),
                "state": state.state,
                "mode": getattr(entity, "mode", None),
                "max": getattr(entity, "max_runs", None),
            }

            # Get full trigger/condition/action configs from raw_config
            if hasattr(entity, "raw_config"):
                raw_config = entity.raw_config
                automation_data["trigger"] = raw_config.get("trigger", [])
                automation_data["condition"] = raw_config.get("condition", [])
                automation_data["action"] = raw_config.get("action", [])
            else:
                # Fallback to state attributes (may be incomplete)
                _LOGGER.warning(
                    "Automation %s doesn't have raw_config, using state attributes", entity_id
                )
                automation_data["trigger"] = state.attributes.get("trigger", [])
                automation_data["condition"] = state.attributes.get("condition", [])
                automation_data["action"] = state.attributes.get("action", [])

            # Add last triggered timestamp
            if hasattr(entity, "last_triggered"):
                automation_data["last_triggered"] = (
                    entity.last_triggered.isoformat() if entity.last_triggered else None
                )
            elif "last_triggered" in state.attributes:
                automation_data["last_triggered"] = state.attributes["last_triggered"]

            automations.append(automation_data)

        except Exception as e:
            _LOGGER.exception("Failed to extract automation %s: %s", entity.entity_id, e)
            continue

    _LOGGER.debug("Extracted %d automations", len(automations))
    return automations


async def _get_scenes(hass: HomeAssistant) -> list[dict[str, Any]]:
    """Extract scene configurations from Home Assistant.

    Args:
        hass: Home Assistant instance

    Returns:
        List of scene dictionaries with configurations
    """
    scenes = []

    # Get all scene entities from states
    for state in hass.states.async_all(SCENE_DOMAIN):
        try:
            scene_data = {
                "entity_id": state.entity_id,
                "friendly_name": state.attributes.get("friendly_name", state.name),
                "entities": state.attributes.get("entity_id", []),
            }

            scenes.append(scene_data)

        except Exception as e:
            _LOGGER.exception("Failed to extract scene %s: %s", state.entity_id, e)
            continue

    _LOGGER.debug("Extracted %d scenes", len(scenes))
    return scenes


async def _get_scripts(hass: HomeAssistant) -> list[dict[str, Any]]:
    """Extract script configurations from Home Assistant.

    Args:
        hass: Home Assistant instance

    Returns:
        List of script dictionaries with configurations
    """
    scripts = []

    # Get script component
    script_component = hass.data.get(SCRIPT_DOMAIN)
    if not script_component:
        _LOGGER.debug("Script component not found")
        return scripts

    # Iterate through script entities
    for entity in script_component.entities:
        try:
            entity_id = entity.entity_id
            state = hass.states.get(entity_id)

            if not state:
                _LOGGER.debug("No state found for script %s", entity_id)
                continue

            script_data = {
                "entity_id": entity_id,
                "friendly_name": state.attributes.get("friendly_name", entity.name),
                "mode": getattr(entity, "mode", None),
                "max": getattr(entity, "max_runs", None),
            }

            # Get sequence from raw config if available
            if hasattr(entity, "raw_config"):
                raw_config = entity.raw_config
                script_data["sequence"] = raw_config.get("sequence", [])
            else:
                # Fallback to state attributes
                _LOGGER.warning("Script %s doesn't have raw_config, using state attributes", entity_id)
                script_data["sequence"] = state.attributes.get("sequence", [])

            scripts.append(script_data)

        except Exception as e:
            _LOGGER.exception("Failed to extract script %s: %s", entity.entity_id, e)
            continue

    _LOGGER.debug("Extracted %d scripts", len(scripts))
    return scripts


def _get_instance_id(hass: HomeAssistant) -> str:
    """Get unique instance ID for this Home Assistant installation.

    Args:
        hass: Home Assistant instance

    Returns:
        Unique instance identifier
    """
    # Use Home Assistant's instance ID if available
    if hasattr(hass.data, "instance_id"):
        return hass.data.instance_id

    # Fallback to using the location name
    return hass.config.location_name or "default"
