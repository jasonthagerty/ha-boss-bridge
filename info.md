# HA Boss Bridge

**Exposes Home Assistant automation configurations via REST API**

This lightweight custom integration provides REST API endpoints that expose full automation, scene, and script configurations to external monitoring and analysis tools like [HA Boss](https://github.com/jasonthagerty/ha_boss).

## What It Does

The bridge exposes three API endpoints with full configuration details:

- `GET /api/ha_boss_bridge/automations` - Full automation configs (triggers, conditions, actions)
- `GET /api/ha_boss_bridge/scenes` - Scene entity lists
- `GET /api/ha_boss_bridge/scripts` - Script sequences

## Why You Need This

Home Assistant's standard `/api/states` endpoint only returns **metadata** about automations (ID, mode, last_triggered) - NOT the full trigger/condition/action configurations. This bridge fills that gap by exposing the complete configs.

## Use Cases

- **HA Boss**: Auto-discover which entities are used in automations
- **Backup Tools**: Export full automation configurations
- **Analysis Tools**: Find unused entities, optimize automations
- **Documentation**: Auto-generate automation documentation

## Security

- Requires Home Assistant authentication (Bearer token)
- Admin-only access (non-admin users get 403 Forbidden)
- Read-only (cannot modify configurations)

## Installation

See the [installation guide](https://github.com/jasonthagerty/ha_boss/wiki/HA-Boss-Bridge) in the wiki.
