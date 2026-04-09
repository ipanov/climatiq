# Xiaomi Miot Auto - X20+ Vacuum Robot

## Overview

The Xiaomi Miot Auto integration (HACS custom component) connects to Xiaomi
robot vacuums using the MIoT (Xiaomi IoT) protocol. It provides vacuum control
plus sensor data (battery, status, consumable life, etc.).

**Xiaomi X20+ Vacuum** is located in the living room and is coordinated with
the air purifier for IAQ management (post-cleaning PM2.5 boost).

## Installation (HACS Required)

This is NOT a built-in HA integration. Install via HACS:

### 1. Install HACS (if not already installed)

Follow https://www.hacs.xyz/docs/use/download/download/

### 2. Install Xiaomi Miot Auto

1. Open **HACS** in HA sidebar
2. Click **Integrations**
3. Search for **Xiaomi Miot Auto**
4. Click **Download** and restart Home Assistant
5. Repository: https://github.com/al-one/hass-xiaomi-miot

### 3. Configure Integration

Two authentication methods:

#### Option A: Xiaomi Cloud Login (Recommended)

1. **Settings > Devices & Services > Add Integration**
2. Search for **Xiaomi Miot Auto**
3. Select **Login to Xiaomi account**
4. Enter Xiaomi account credentials
5. Select your vacuum from the device list
6. All entities auto-created

#### Option B: Local Token (Manual)

1. Extract device token (see xiaomi-miio.md for methods)
2. **Settings > Devices & Services > Add Integration**
3. Search for **Xiaomi Miot Auto**
4. Select **Customize a device**
5. Enter:
   - Host: `192.168.1.103` (vacuum IP)
   - Token: `your_32_char_hex_token`
   - Model: `dreame.vacuum.p2029` (X20+ model)

## Entity Names Generated

| Entity | Type | Purpose |
|--------|------|---------|
| `vacuum.xiaomi_x20_plus` | vacuum | Start, stop, pause, return to dock, locate |
| `sensor.xiaomi_x20_plus_battery` | sensor | Battery level (%) |
| `sensor.xiaomi_x20_plus_status` | sensor | Current cleaning status |
| `sensor.xiaomi_x20_plus_last_clean` | sensor | Last cleaning area/time |
| Various consumable sensors | sensor | Filter, brush, side brush life (%) |

## Automation Integration

The ClimatIQ vacuum automation coordinates with the air purifier:

1. **Daily clean** at 10:00 (scheduled, avoids nighttime)
2. **Post-clean boost**: Purifier runs at 100% for 20 minutes after vacuum returns to dock
3. **Night lock**: Vacuum never operates between 23:00-06:00
4. **PM2.5 monitoring**: Extra clean scheduled if baseline PM2.5 rising (future)

## Vacuum Services Used

```yaml
# Start cleaning
service: vacuum.start
target:
  entity_id: vacuum.xiaomi_x20_plus

# Return to dock
service: vacuum.return_to_base
target:
  entity_id: vacuum.xiaomi_x20_plus

# Pause
service: vacuum.pause
target:
  entity_id: vacuum.xiaomi_x20_plus
```

## Room Cleaning (Zone/Room Support)

If your X20+ supports room mapping, you can specify rooms:

```yaml
service: vacuum.send_command
target:
  entity_id: vacuum.xiaomi_x20_plus
data:
  command: "app_segment_clean"
  params: [1, 2]  # Room IDs from the map
```

## Static IP Recommendation

Assign a static IP to the vacuum dock station:
- Vacuum X20+: `192.168.1.103`

## Troubleshooting

- **Integration not found**: Ensure HACS is installed and Xiaomi Miot Auto is
  downloaded. Restart HA after HACS installation.
- **Device not connecting**: Vacuum must be on WiFi. Check Mi Home app first.
- **Token expired**: Re-login via Xiaomi Cloud method or re-extract token.
- **Consumable sensors missing**: Some models expose these only when the vacuum
  has been active at least once.
