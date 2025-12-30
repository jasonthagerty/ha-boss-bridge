# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HA Boss Bridge is a lightweight Home Assistant custom integration that exposes full automation, scene, and script configurations via REST API. It fills a critical gap in Home Assistant's standard API by providing access to complete trigger/condition/action configurations that are not available through `/api/states`.

### Core Purpose

**Problem**: Home Assistant's `/api/states` endpoint only exposes metadata (id, mode, last_triggered) for automations - NOT the full trigger/condition/action configurations needed for analysis and monitoring tools.

**Solution**: HA Boss Bridge accesses Home Assistant's internal automation registry and exposes three REST API endpoints with complete configuration details:

```
GET /api/ha_boss_bridge/automations  → Full automation configs
GET /api/ha_boss_bridge/scenes       → Scene entity lists
GET /api/ha_boss_bridge/scripts      → Script sequences
```

### Use Cases

- **[HA Boss](https://github.com/jasonthagerty/ha_boss)**: Auto-discover which entities are used in automations
- **Backup Tools**: Export full automation configurations
- **Analysis Tools**: Find unused entities, optimize automations
- **Documentation**: Auto-generate automation documentation

### Design Philosophy

1. **Minimal Footprint**: Single integration, no external dependencies
2. **Security First**: Admin-only access, read-only endpoints, comprehensive logging
3. **HACS Compatible**: Easy installation and updates via HACS
4. **Version Independent**: Bridge versions are independent from HA Boss versions
5. **Standard Patterns**: Follow Home Assistant integration best practices

## Development Commands

### Prerequisites

- **Python 3.12** (REQUIRED - project standardized on 3.12 only)
  - ⚠️ Using any other Python version will cause CI failures
  - All tooling (black, ruff, mypy) is configured for Python 3.12
  - CI only tests Python 3.12 to ensure consistency
- **Home Assistant** instance for testing (HA OS, Container, Supervised, or Core)
- **GitHub MCP Server** (recommended) - for issue/PR management via Claude Code
  - See "GitHub MCP Server Integration" section below for setup
  - Alternative: `gh` CLI (optional if MCP server configured)

**Note for GitHub Actions/CI**: The following tools are pre-installed in GitHub Actions runners:
- `git` - version control
- `gh` (GitHub CLI) - available as fallback

### Local Development Setup

**Primary method (recommended):**
- Configure GitHub MCP Server (see "GitHub MCP Server Integration" section)
- Claude Code will handle GitHub operations automatically

**Alternative (if MCP not available):**
- **GitHub CLI (gh)** - for manual issue/PR management (https://cli.github.com/)

**No virtual environment needed** - Home Assistant custom integrations are installed directly into HA's Python environment. For local code quality checks:

```bash
# Install code quality tools globally or in a separate venv
pip install black ruff mypy

# Or use pre-commit for automated checks
pip install pre-commit
pre-commit install
```

### Testing

**Manual Testing** (recommended for HA integrations):

1. Copy integration to Home Assistant:
   ```bash
   # Copy to your HA config directory
   cp -r custom_components/ha_boss_bridge /path/to/ha/config/custom_components/
   ```

2. Restart Home Assistant

3. Test API endpoints:
   ```bash
   # Replace with your HA URL and long-lived token
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        http://homeassistant.local:8123/api/ha_boss_bridge/automations
   ```

4. Check Home Assistant logs for errors:
   ```bash
   # In HA container or system logs
   tail -f /config/home-assistant.log | grep ha_boss_bridge
   ```

**Integration Testing**:
- Create test automations with various trigger/condition/action types
- Verify all configurations are exposed correctly
- Test with admin and non-admin users
- Verify error handling (invalid tokens, missing automations, etc.)

### Code Quality

```bash
# Auto-format code (do this before committing)
black custom_components/

# Lint and auto-fix issues
ruff check custom_components/ --fix

# Type checking
mypy custom_components/ --ignore-missing-imports

# Complete CI check (run before pushing)
black --check custom_components/ && \
ruff check custom_components/ && \
mypy custom_components/ --ignore-missing-imports
```

### HACS Validation

Before releasing, ensure HACS validation passes:

```bash
# Via GitHub Actions (automatic on push)
# Check workflow: .github/workflows/validate.yml

# Manual validation (requires Docker)
docker run --rm -v $(pwd):/github/workspace \
  ghcr.io/hacs/action:latest \
  --category integration
```

## Architecture

### Project Structure

```
ha-boss-bridge/
├── custom_components/ha_boss_bridge/  # Integration code
│   ├── __init__.py                   # Integration setup (~40 lines)
│   ├── api.py                        # REST API handlers (~300 lines)
│   ├── const.py                      # Constants and API paths
│   └── manifest.json                 # HACS metadata
├── .github/workflows/
│   └── validate.yml                  # HACS validation + code quality
├── hacs.json                         # HACS distribution metadata
├── info.md                           # HACS info page
├── README.md                         # Installation and usage docs
├── CLAUDE.md                         # This file
├── LICENSE                           # MIT license
├── .gitignore                        # Git ignore rules
├── pyproject.toml                    # Code quality tool config
└── .pre-commit-config.yaml           # Pre-commit hooks
```

### Component Architecture

```
┌─────────────────────────────────────────┐
│       Home Assistant Instance            │
├─────────────────────────────────────────┤
│                                          │
│  ┌────────────────────────────────┐    │
│  │  HA Boss Bridge Integration    │    │
│  │  (custom_components/)           │    │
│  │                                 │    │
│  │  ┌──────────────────────────┐  │    │
│  │  │  REST API Views          │  │    │
│  │  │                          │  │    │
│  │  │  - AutomationsView      │  │    │
│  │  │  - ScenesView           │  │    │
│  │  │  - ScriptsView          │  │    │
│  │  └──────────┬───────────────┘  │    │
│  │             │                   │    │
│  │             │ Access Internal   │    │
│  │             │ Registries        │    │
│  │             ▼                   │    │
│  │  ┌──────────────────────────┐  │    │
│  │  │  HA Internal Components  │  │    │
│  │  │                          │  │    │
│  │  │  - automation.entities   │  │    │
│  │  │  - scene.entities        │  │    │
│  │  │  - script.entities       │  │    │
│  │  │  - .raw_config          │  │    │
│  │  └──────────────────────────┘  │    │
│  └─────────────────────────────────┘    │
│                                          │
└─────────────────────────────────────────┘
              │
              │ HTTP REST API
              ▼
      ┌───────────────┐
      │  HA Boss      │
      │  or other     │
      │  tools        │
      └───────────────┘
```

### Data Flow

**API Request Flow**:

1. Client makes authenticated GET request to `/api/ha_boss_bridge/automations`
2. `AutomationsView.get()` handler receives request
3. Verify authentication via `request["hass_user"]`
4. Check admin access (return 403 if not admin)
5. Access HA's internal automation component via `hass.data.get(AUTOMATION_DOMAIN)`
6. Iterate through `automation_component.entities`
7. Extract `entity.raw_config` which contains full trigger/condition/action
8. Build response JSON with automations array, bridge version, instance ID
9. Return JSON response

**Security Checks**:
- Bearer token authentication (HA standard)
- Admin-only access verification
- Read-only operations (no modifications)
- Comprehensive error logging

### Key Implementation Details

**Accessing Internal Registries**:
```python
# Home Assistant stores component data in hass.data dictionary
automation_component = hass.data.get(AUTOMATION_DOMAIN)

# Each component has an entities collection
for entity in automation_component.entities:
    # raw_config contains the full YAML configuration
    raw_config = entity.raw_config

    # Extract configuration sections
    trigger = raw_config.get("trigger", [])
    condition = raw_config.get("condition", [])
    action = raw_config.get("action", [])
```

**Authentication Pattern**:
```python
class AutomationsView(HomeAssistantView):
    requires_auth = True  # Require Bearer token

    async def get(self, request: web.Request) -> web.Response:
        # Check admin access
        if not request["hass_user"].is_admin:
            return self.json(
                {"error": "Unauthorized - admin access required"},
                status_code=403
            )
```

### Code Organization Rules

When adding new features:
1. **Minimal Changes**: Keep integration lightweight (currently ~400 lines total)
2. **Type Hints**: All functions must have complete annotations
3. **Error Handling**: Comprehensive try/except with logging
4. **Documentation**: Docstrings for all public APIs (Google style)
5. **Security**: Admin-only for sensitive data, extensive logging
6. **HA Standards**: Follow Home Assistant integration patterns

## Home Assistant Integration Best Practices

### Integration Lifecycle

**Setup Sequence** (`__init__.py:async_setup`):
1. Integration loaded during HA startup
2. `async_setup()` called with `hass` and `config`
3. Register API views with `hass.http.register_view()`
4. Return `True` to indicate successful setup
5. API endpoints now available at `/api/ha_boss_bridge/*`

**No Configuration Required**:
- Integration works out-of-the-box after installation
- No `configuration.yaml` entries needed
- No UI configuration flows required

### API View Pattern

Use `HomeAssistantView` for REST endpoints:

```python
from homeassistant.components.http import HomeAssistantView

class AutomationsView(HomeAssistantView):
    url = "/api/ha_boss_bridge/automations"
    name = "api:ha_boss_bridge:automations"
    requires_auth = True  # Require Bearer token

    async def get(self, request: web.Request) -> web.Response:
        hass: HomeAssistant = request.app["hass"]
        # ... implementation
        return self.json({"data": ...})
```

### Security Best Practices

**Authentication**:
- Always set `requires_auth = True` for API views
- Use Bearer token authentication (HA standard)
- Verify admin access for sensitive operations

**Authorization**:
```python
# Check if user is admin
if not request["hass_user"].is_admin:
    _LOGGER.warning(
        "Unauthorized access attempt from user: %s",
        request["hass_user"].name
    )
    return self.json(
        {"error": "Unauthorized - admin access required"},
        status_code=403
    )
```

**Logging**:
- Log all unauthorized access attempts
- Log errors with full exception details
- Use appropriate log levels (INFO for normal, WARNING for suspicious, ERROR for failures)

### Error Handling

```python
try:
    automation_component = hass.data.get(AUTOMATION_DOMAIN)
    if not automation_component:
        _LOGGER.error("Automation component not found")
        return self.json(
            {"error": "Automation component not available"},
            status_code=503
        )
except Exception as e:
    _LOGGER.error("Failed to get automations: %s", str(e), exc_info=True)
    return self.json(
        {"error": f"Internal server error: {str(e)}"},
        status_code=500
    )
```

### HACS Integration

**Required Files**:
1. `hacs.json` - HACS metadata
2. `info.md` - HACS info page (displayed in HACS UI)
3. `README.md` - GitHub README
4. `custom_components/ha_boss_bridge/manifest.json` - Integration metadata

**Manifest Requirements**:
```json
{
  "domain": "ha_boss_bridge",
  "name": "HA Boss Bridge",
  "version": "1.0.0",
  "documentation": "https://github.com/jasonthagerty/ha_boss/wiki/HA-Boss-Bridge",
  "issue_tracker": "https://github.com/jasonthagerty/ha-boss-bridge/issues",
  "requirements": [],
  "dependencies": [],
  "codeowners": ["@jasonthagerty"],
  "iot_class": "local_push",
  "integration_type": "service"
}
```

**HACS Validation**:
- GitHub Actions workflow validates on every push
- Must pass before release

## Feature Branch Workflow

### Overview

All development work is tracked via GitHub Issues and managed through feature branches. This ensures clear ownership, tracking, and integration with CI/CD.

### Issue-Driven Development

**GitHub Issues** are the source of truth for all work:
- **View Issues**: https://github.com/jasonthagerty/ha-boss-bridge/issues
- Issues include acceptance criteria, technical notes, and branch names

### Branch Naming Convention

**Format:** `<type>/issue-<number>-<brief-description>`

**Types:**
- `feature/` - New features (new endpoints, enhancements)
- `fix/` - Bug fixes
- `docs/` - Documentation only changes
- `refactor/` - Code refactoring without functional changes

**Examples:**
- `feature/issue-1-add-device-endpoint`
- `fix/issue-5-automation-parsing`
- `docs/issue-3-update-api-docs`

### Complete Feature Workflow

1. **Review Issue**: Read description, acceptance criteria, dependencies
2. **Create Branch**: `git checkout -b feature/issue-{number}-brief-description`
3. **Implement**: Follow acceptance criteria, add type hints
4. **Test**: Manual testing with live HA instance + code quality checks
5. **Commit**: Use conventional commits, reference issue number, include co-author
6. **Create PR**: Include "Closes #{number}", summary, and testing notes

### Example: Feature Implementation Workflow

```bash
# Create branch
git checkout -b feature/issue-1-add-device-endpoint

# Implement and test
# ... (write code, test with HA instance)

# Run code quality checks
black custom_components/
ruff check custom_components/ --fix
mypy custom_components/ --ignore-missing-imports

# Commit
git commit -m "feat: add device endpoint to API

- Added DevicesView with admin-only access
- Exposes device registry via /api/ha_boss_bridge/devices
- Added comprehensive error handling and logging
- Tested with HA 2024.1+

Closes #1

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Push and create PR (via GitHub MCP or gh CLI)
git push origin feature/issue-1-add-device-endpoint
```

### Branch Protection

- `main` branch is protected
- All changes must go through PRs
- CI checks must pass before merge
- Squash commits on merge to keep history clean

## CI/CD Integration

### GitHub Actions Workflows

**Validation Pipeline** (`.github/workflows/validate.yml`):
- Runs on push to main/develop and PRs
- Tests Python 3.12
- Checks: black, ruff, mypy
- HACS validation
- Must pass before merge

**No Automated Deployments**:
- Releases are manual (GitHub Releases)
- HACS pulls from GitHub releases automatically

### Working with CI Failures

When CI fails:
1. Read workflow logs to identify root cause
2. Create fix branch: `fix/issue-{number}-brief-description`
3. Implement fix
4. Run code quality checks locally
5. Create PR with "Closes #{number}"

## Code Quality Standards

### Formatting and Style

- **Line length**: 100 characters (enforced by black and ruff)
- **Import order**: stdlib, third-party, HA, local (managed by ruff)
- **Docstrings**: Use Google-style docstrings for public APIs
- **Type hints**: Required for all function signatures

### Type Checking

All code must pass mypy checking with `--ignore-missing-imports`:
```python
from typing import Any
from homeassistant.core import HomeAssistant

async def get_automations(hass: HomeAssistant) -> list[dict[str, Any]]:
    """Extract automation configurations from Home Assistant.

    Args:
        hass: Home Assistant instance

    Returns:
        List of automation configuration dictionaries
    """
    automations: list[dict[str, Any]] = []
    # ... implementation
    return automations
```

### Error Handling

Always log errors with context:
```python
try:
    result = await some_operation()
except HomeAssistantError as e:
    _LOGGER.error(
        "Failed to get automations: %s",
        str(e),
        exc_info=True  # Include stack trace
    )
    return self.json(
        {"error": f"Operation failed: {str(e)}"},
        status_code=500
    )
```

## GitHub MCP Server Integration

**Recommended: GitHub MCP Server** for all GitHub operations

The GitHub MCP (Model Context Protocol) server enables Claude Code to directly create and manage GitHub issues, PRs, and other repository operations without relying on the `gh` CLI.

**Setup Instructions**: See ha_boss CLAUDE.md for detailed setup guide (same configuration applies to all repositories).

**Security Notes**:

⚠️ **CRITICAL - Token Security**:
- **NEVER commit `.claude/mcp.json`** to the repository
- Store MCP configuration in user-level config directory:
  - Linux/Mac: `~/.config/claude/mcp.json`
  - Windows: `%APPDATA%\Claude\mcp.json`
- Rotate tokens periodically and revoke unused tokens

## Versioning and Releases

### Semantic Versioning

This integration follows [Semantic Versioning](https://semver.org/):
- **1.0.x**: Bug fixes (patch)
- **1.x.0**: New features, backward compatible (minor)
- **x.0.0**: Breaking changes (major)

**Current Version**: 1.0.0

### Version Independence

Bridge versions are **independent** from HA Boss versions:
- Bridge v1.0 works with HA Boss v1.x, v2.x, etc.
- Bridge updates don't require HA Boss updates
- Breaking changes in bridge API require major version bump

### Release Process

1. **Update Version**:
   - `custom_components/ha_boss_bridge/manifest.json` - `version` field
   - `custom_components/ha_boss_bridge/const.py` - `VERSION` constant

2. **Create GitHub Release**:
   - Tag format: `v1.0.0`
   - Release notes with changelog
   - HACS automatically detects new releases

3. **Test Installation**:
   - Install via HACS from release
   - Verify endpoints work
   - Check HA logs for errors

## Common Workflows

### Adding a New API Endpoint

1. **Create Issue** with endpoint specification
2. **Create Branch**: `feature/issue-{number}-add-{endpoint}`
3. **Add View Class** in `api.py`:
   ```python
   class NewEndpointView(HomeAssistantView):
       url = "/api/ha_boss_bridge/new_endpoint"
       name = "api:ha_boss_bridge:new_endpoint"
       requires_auth = True

       async def get(self, request: web.Request) -> web.Response:
           # Implementation
   ```
4. **Register View** in `__init__.py:async_setup()`
5. **Update Constants** in `const.py`
6. **Test** with live HA instance
7. **Update README** with new endpoint documentation
8. **Create PR** with "Closes #{number}"

### Fixing a Bug

1. Review bug issue and reproduce locally
2. Create branch: `fix/issue-{number}-brief-description`
3. Implement fix
4. Test with HA instance
5. Run code quality checks
6. Create PR with "Closes #{number}"

### Updating Documentation

1. Create branch: `docs/issue-{number}-update-{doc}`
2. Update relevant files (README.md, info.md, wiki)
3. Review for accuracy and clarity
4. Create PR with "Closes #{number}"

## Security Considerations

### Protected Files (Never Commit)

The following files are protected by `.gitignore` and must NEVER be committed:
- `.claude/mcp.json` - Contains GitHub Personal Access Tokens
- `.claude/settings.local.json` - Local Claude Code settings
- `.claude/*.local.json` - Any local configuration files

### Best Practices

- Keep dependencies minimal (currently zero external dependencies)
- All API endpoints require admin access
- Log all unauthorized access attempts
- Use GitHub Secrets for CI/CD tokens
- Review code for security issues before merging
- Never expose sensitive HA data without authorization

## Related Documentation

- **Installation**: See [README.md](README.md)
- **API Reference**: See [Wiki](https://github.com/jasonthagerty/ha_boss/wiki/HA-Boss-Bridge)
- **HA Boss**: https://github.com/jasonthagerty/ha_boss
- **HACS**: https://hacs.xyz/
