# HA Boss Bridge - Installation and Testing Guide

## Pre-Installation Verification

✅ **Confirmed**:
- Home Assistant instance accessible at: `https://home.jasmel.com:8123`
- API authentication working with long-lived token
- Current automation count: **52 automations**
- Problem confirmed: `/api/states` returns only metadata, NOT full configs

**Example of current limitation**:
```json
{
  "entity_id": "automation.game_mode_basement",
  "state": "on",
  "attributes": {
    "id": "1645574667202",
    "last_triggered": "2025-12-29T21:23:18.423128+00:00",
    "mode": "single",
    "current": 0,
    "friendly_name": "Family Room - PS5  (start)"
  }
}
```

**Missing**: `trigger`, `condition`, `action` configurations!

---

## Installation Options

### Option 1: Manual Installation (Fastest for Testing)

1. **SSH into your Home Assistant server** or access the config directory

2. **Copy integration files**:
   ```bash
   # From your development machine
   scp -r /home/jason/Projects/ha-boss-bridge/custom_components/ha_boss_bridge \
       user@home.jasmel.com:/path/to/homeassistant/config/custom_components/
   ```

   Or if you have direct access:
   ```bash
   cp -r /home/jason/Projects/ha-boss-bridge/custom_components/ha_boss_bridge \
       /path/to/homeassistant/config/custom_components/
   ```

3. **Restart Home Assistant**:
   - Via UI: Settings → System → Restart
   - Via CLI: `ha core restart` (if using HA OS)
   - Via Docker: `docker restart homeassistant`

4. **Verify installation**:
   ```bash
   # Check Home Assistant logs
   tail -f /path/to/homeassistant/config/home-assistant.log | grep ha_boss_bridge

   # Should see:
   # INFO (MainThread) [custom_components.ha_boss_bridge] Setting up HA Boss Bridge v1.0.0
   # INFO (MainThread) [custom_components.ha_boss_bridge] HA Boss Bridge API endpoints registered
   ```

### Option 2: Via HACS (After v1.0.0 Release)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click "..." menu → "Custom repositories"
4. Add: `https://github.com/jasonthagerty/ha-boss-bridge`
5. Category: "Integration"
6. Click "Install"
7. Restart Home Assistant

---

## Testing the Bridge API

### Test 1: Verify Endpoint is Available

```bash
curl -k -H "Authorization: Bearer YOUR_TOKEN" \
     https://home.jasmel.com:8123/api/ha_boss_bridge/automations

# Expected: HTTP 200 with JSON response (not 404)
```

### Test 2: Check Automation Configs

```bash
# Get all automations with full configs
curl -k -H "Authorization: Bearer YOUR_TOKEN" \
     https://home.jasmel.com:8123/api/ha_boss_bridge/automations \
     | jq '.'

# Expected response structure:
{
  "automations": [
    {
      "entity_id": "automation.game_mode_basement",
      "friendly_name": "Family Room - PS5  (start)",
      "state": "on",
      "mode": "single",
      "max": null,
      "trigger": [ ... ],      # ← Full trigger config!
      "condition": [ ... ],    # ← Full condition config!
      "action": [ ... ],       # ← Full action config!
      "last_triggered": "2025-12-29T21:23:18.423128+00:00"
    }
  ],
  "bridge_version": "1.0.0",
  "instance_id": "home",
  "count": 52
}
```

### Test 3: Verify Security (Admin-Only Access)

```bash
# Try with a non-admin user token (should get 403)
curl -k -H "Authorization: Bearer NON_ADMIN_TOKEN" \
     https://home.jasmel.com:8123/api/ha_boss_bridge/automations

# Expected: HTTP 403 Forbidden
{
  "error": "Unauthorized - admin access required"
}
```

### Test 4: Check Scenes Endpoint

```bash
curl -k -H "Authorization: Bearer YOUR_TOKEN" \
     https://home.jasmel.com:8123/api/ha_boss_bridge/scenes \
     | jq '.count'

# Expected: Number of scenes in your HA instance
```

### Test 5: Check Scripts Endpoint

```bash
curl -k -H "Authorization: Bearer YOUR_TOKEN" \
     https://home.jasmel.com:8123/api/ha_boss_bridge/scripts \
     | jq '.count'

# Expected: Number of scripts in your HA instance
```

---

## Validation Checklist

After installation, verify:

- [ ] Home Assistant starts without errors
- [ ] Log shows "HA Boss Bridge v1.0.0" setup message
- [ ] API endpoint `/api/ha_boss_bridge/automations` returns 200 (not 404)
- [ ] Response includes `trigger`, `condition`, `action` fields for automations
- [ ] Response includes `bridge_version` and `instance_id` fields
- [ ] Automation count matches your actual automation count (should be 52)
- [ ] Non-admin users get 403 Forbidden
- [ ] Scenes and scripts endpoints also work

---

## Troubleshooting

### Issue: 404 Not Found

**Cause**: Integration not loaded or endpoints not registered

**Fix**:
1. Check custom_components directory exists and has correct structure:
   ```
   custom_components/ha_boss_bridge/
   ├── __init__.py
   ├── api.py
   ├── const.py
   └── manifest.json
   ```
2. Check Home Assistant logs for errors
3. Restart Home Assistant again

### Issue: 403 Forbidden

**Cause**: User is not admin or token is invalid

**Fix**:
1. Verify token is from an admin user account
2. Check token hasn't expired (expires 2081-07-80)
3. Try creating a new long-lived access token

### Issue: 500 Internal Server Error

**Cause**: Error in integration code or HA internal API changed

**Fix**:
1. Check Home Assistant logs for Python exceptions
2. Enable debug logging in `configuration.yaml`:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.ha_boss_bridge: debug
   ```
3. Restart HA and check logs again

### Issue: Empty automations array

**Cause**: Automations not loaded or component not found

**Fix**:
1. Verify automations exist: `curl .../api/states | jq '[.[] | select(.entity_id | startswith("automation."))] | length'`
2. Check if automations are defined in UI or YAML
3. Check HA logs for automation component errors

---

## Integration with HA Boss

Once the bridge is installed and verified, you can test with HA Boss:

### Test Discovery

```bash
# From ha_boss project directory
source .venv/bin/activate

# Test bridge detection
python -c "
import asyncio
import aiohttp

async def test_bridge():
    async with aiohttp.ClientSession() as session:
        headers = {'Authorization': 'Bearer YOUR_TOKEN'}
        async with session.get(
            'https://home.jasmel.com:8123/api/ha_boss_bridge/automations',
            headers=headers,
            ssl=False
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f'✅ Bridge detected! Found {data[\"count\"]} automations')
                print(f'   Version: {data[\"bridge_version\"]}')
                print(f'   Instance: {data[\"instance_id\"]}')
            else:
                print(f'❌ Bridge not available: HTTP {resp.status}')

asyncio.run(test_bridge())
"
```

### Expected Output

```
✅ Bridge detected! Found 52 automations
   Version: 1.0.0
   Instance: home
```

---

## Next Steps

1. **Install the bridge** using Option 1 (manual) for fastest testing
2. **Run all 5 tests** above to verify functionality
3. **Report results** - let me know if any tests fail
4. Once verified, I'll create **GitHub Release v1.0.0** for HACS distribution
5. Then we can proceed with **Phase 2** (HA Boss updates) to use the bridge

---

## Support

If you encounter issues:
- Check Home Assistant logs: `/config/home-assistant.log`
- Enable debug logging for the integration
- Create GitHub issue: https://github.com/jasonthagerty/ha-boss-bridge/issues
- Verify Home Assistant version compatibility (tested on 2024.1+)
