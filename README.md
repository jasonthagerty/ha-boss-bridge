# HA Boss Bridge

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Lightweight Home Assistant custom integration that exposes full automation, scene, and script configurations via REST API.**

## Problem

Home Assistant's standard `/api/states` endpoint only returns **metadata** about automations (ID, mode, last_triggered) - NOT the full trigger/condition/action configurations needed for analysis and monitoring tools.

## Solution

HA Boss Bridge fills this gap by exposing three REST API endpoints with complete configuration details:

```
GET /api/ha_boss_bridge/automations  → Full automation configs
GET /api/ha_boss_bridge/scenes       → Scene entity lists
GET /api/ha_boss_bridge/scripts      → Script sequences
```

## Use Cases

- **[HA Boss](https://github.com/jasonthagerty/ha_boss)**: Auto-discover which entities are used in automations
- **Backup Tools**: Export full automation configurations
- **Analysis Tools**: Find unused entities, optimize automations
- **Documentation**: Auto-generate automation documentation

## Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots menu (⋮) → "Custom repositories"
4. Add repository URL: `https://github.com/jasonthagerty/ha-boss-bridge`
5. Category: "Integration"
6. Click "Install"
7. Restart Home Assistant
8. Go to Settings → Devices & Services → Add Integration
9. Search for "HA Boss Bridge" and click to add

### Manual Installation

1. Download the [latest release](https://github.com/jasonthagerty/ha-boss-bridge/releases)
2. Extract to `config/custom_components/ha_boss_bridge/`
3. Restart Home Assistant
4. Go to Settings → Devices & Services → Add Integration
5. Search for "HA Boss Bridge" and click to add

## Configuration

### UI Configuration (Recommended - v1.1.0+)

After installation, simply add the integration via the Home Assistant UI:

1. Navigate to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **"HA Boss Bridge"**
4. Click to add (no configuration needed!)
5. API endpoints are immediately available

### YAML Configuration (Legacy)

For backward compatibility, you can also configure via `configuration.yaml`:

```yaml
# configuration.yaml
ha_boss_bridge:
```

Then restart Home Assistant.

## Usage

### Authentication

All endpoints require Home Assistant authentication (Bearer token) and admin access:

```bash
curl -H "Authorization: Bearer YOUR_LONG_LIVED_TOKEN" \
     http://homeassistant.local:8123/api/ha_boss_bridge/automations
```

### Example Response

```json
{
  "automations": [
    {
      "entity_id": "automation.bedroom_lights",
      "friendly_name": "Bedroom Lights",
      "state": "on",
      "mode": "single",
      "trigger": [
        {
          "platform": "state",
          "entity_id": "binary_sensor.bedroom_motion"
        }
      ],
      "condition": [],
      "action": [
        {
          "service": "light.turn_on",
          "target": {
            "entity_id": "light.bedroom"
          }
        }
      ],
      "last_triggered": "2025-12-29T10:00:00+00:00"
    }
  ],
  "bridge_version": "1.0.0",
  "instance_id": "my-home",
  "count": 1
}
```

## Security

- ✅ Requires Home Assistant Bearer token authentication
- ✅ Admin-only access (non-admin users get 403 Forbidden)
- ✅ Read-only endpoints (cannot modify configurations)
- ✅ Logs unauthorized access attempts

## Documentation

Full documentation available in the [HA Boss Wiki](https://github.com/jasonthagerty/ha_boss/wiki/HA-Boss-Bridge):

- [Installation Guide](https://github.com/jasonthagerty/ha_boss/wiki/HA-Boss-Bridge#installation)
- [API Reference](https://github.com/jasonthagerty/ha_boss/wiki/HA-Boss-Bridge#api-reference)
- [Troubleshooting](https://github.com/jasonthagerty/ha_boss/wiki/HA-Boss-Bridge#troubleshooting)

## Contributing

Contributions welcome! See [CLAUDE.md](CLAUDE.md) for development guidelines.

**Development Setup:**

```bash
# Clone repository
git clone https://github.com/jasonthagerty/ha-boss-bridge.git
cd ha-boss-bridge

# Install development tools
pip install black ruff mypy pre-commit

# Install pre-commit hooks
pre-commit install

# Run code quality checks
black custom_components/
ruff check custom_components/
mypy custom_components/ --ignore-missing-imports
```

## Versioning

This integration follows [Semantic Versioning](https://semver.org/):
- **1.0.x**: Bug fixes
- **1.x.0**: New features (backward compatible)
- **x.0.0**: Breaking changes

**Current Version:** 1.0.0

**Version Independence:** Bridge versions are independent from HA Boss versions. Bridge v1.0 works with HA Boss v1.x, v2.x, etc.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

Created by [Jason Hagerty](https://github.com/jasonthagerty) as part of the [HA Boss](https://github.com/jasonthagerty/ha_boss) project.

## Support

- **Issues**: [GitHub Issues](https://github.com/jasonthagerty/ha-boss-bridge/issues)
- **Discussions**: [HA Boss Discussions](https://github.com/jasonthagerty/ha_boss/discussions)
- **Wiki**: [Documentation](https://github.com/jasonthagerty/ha_boss/wiki/HA-Boss-Bridge)
