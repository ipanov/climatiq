# Xiaomi Miio - Air Purifier 3H + Smartmi Humidifier 2

## Overview

The Xiaomi Miio integration controls Xiaomi WiFi devices on the local network.
It requires a 32-character device token for authentication. Two devices are
configured:

1. **Xiaomi Air Purifier 3H** (living room) - PM2.5 sensor + fan control
2. **Smartmi Evaporative Humidifier 2** (living room) - humidity control

## Token Extraction

### Method 1: Mi Home App (Android, Easiest)

1. Install **Mi Home** app (version 5.4.54 or older)
2. Add both devices to the app
3. Create a log file directory on phone
4. Navigate to: Settings > Additional Settings > Developer Options
5. Enable USB debugging
6. Use ADB to extract:
   ```bash
   adb shell
   # Navigate to Mi Home data
   cd /sdcard/SmartHome/logs/plug_DeviceManager
   # Look for the token in the log files
   cat device_manager.log | grep -i token
   ```

### Method 2: Xiaomi Cloud Token Extractor (Recommended)

Uses the `micloud` Python library to fetch tokens from Xiaomi cloud:

```bash
pip install micloud
python -m micloud
# Login with Xiaomi account
# Run token extraction script
```

Or use the community tool:
https://github.com/PiotrMachura/xiaomi-cloud-tokens-extractor

### Method 3: Router Packet Capture

1. Configure device on a separate VLAN
2. Capture traffic during device setup
3. Extract token from the handshake packets

## Home Assistant Configuration

### Via UI (Recommended)

1. **Settings > Devices & Services > Add Integration**
2. Search for **Xiaomi Miio**
3. Enter device IP address and token
4. Select device model from the list

### Via YAML (Alternative)

```yaml
# configuration.yaml

# Air Purifier 3H
fan:
  - platform: xiaomi_miio
    host: 192.168.1.101  # Replace with actual IP
    token: !secret purifier_3h_token
    name: "Xiaomi Air Purifier 3H"
    model: zhimi.airpurifier.mb3  # Air Purifier 3H model identifier

# Smartmi Humidifier 2
humidifier:
  - platform: xiaomi_miio
    host: 192.168.1.102  # Replace with actual IP
    token: !secret smartmi_humidifier_token
    name: "Smartmi Evaporative Humidifier 2"
    model: zhimi.humidifier.cb1  # Smartmi 2 model identifier
```

## Entity Names Generated

### Air Purifier 3H

| Entity | Type | Purpose |
|--------|------|---------|
| `fan.xiaomi_air_purifier_3h` | fan | Speed control (silent/auto/favorite/high) |
| `sensor.living_room_pm25` | sensor | PM2.5 concentration (ug/m3) |
| `sensor.living_room_temperature` | sensor | Built-in temperature sensor |
| `sensor.living_room_humidity` | sensor | Built-in humidity sensor |
| `sensor.xiaomi_air_purifier_3h_filter_life` | sensor | Filter remaining life (%) |

### Smartmi Humidifier 2

| Entity | Type | Purpose |
|--------|------|---------|
| `humidifier.smartmi_evaporative_humidifier_2` | humidifier | Target humidity + mode control |
| Water level attribute | attribute | `water_level` on humidifier entity |

## Fan Speed Mapping (Purifier 3H)

| Percentage | Mode | Use Case |
|-----------|------|----------|
| 16% | Silent | Night, low PM2.5 |
| 25% | Auto (low) | Normal operation |
| 50% | Auto (medium) | Moderate PM2.5 |
| 75% | Favorite | User preference speed |
| 100% | High/Max | PM2.5 > 35, post-vacuum boost |

## Humidifier Modes

| Mode | Description | When Used |
|------|-------------|-----------|
| `auto` | Auto-adjusts fan to hit target | Daytime |
| `silent` | Low fan, slow evaporation | Nighttime (22:00-07:00) |
| `medium` | Medium fan speed | Normal |
| `high` | Maximum evaporation | Very dry air |

## Static IP Recommendation

Assign static IPs to both devices in your router DHCP settings:
- Purifier 3H: `192.168.1.101`
- Smartmi Humidifier: `192.168.1.102`

This prevents the token-device binding from breaking when IPs change.

## Troubleshooting

- **"Invalid token"**: Re-extract the token. Tokens change after device re-pairing.
- **Device offline**: Verify static IP. Check device WiFi indicator.
- **Sensor unavailable**: Some sensor attributes only update when device is ON.
- **Fan speed not changing**: Use `fan.set_percentage` service, not `fan.set_preset_mode`.
