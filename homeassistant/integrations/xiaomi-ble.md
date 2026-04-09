# Xiaomi BLE - Bluetooth Low Energy Sensors

## Overview

Xiaomi BLE sensors (e.g., Xiaomi Temperature/Humidity sensor LYWSD03MMC,
Mijia Round Temperature Humidity sensor) broadcast temperature and humidity
data via BLE advertisements. They use encrypted payloads that require a
binding key to decode.

**Deployed in**: Children's room (temperature + humidity monitoring)

## Supported Devices

| Device | Model | Sensors | Battery |
|--------|-------|---------|---------|
| Xiaomi TH Sensor | LYWSD03MMC | Temp + Humidity | CR2032 |
| Mijia Round TH | LYWSDCGQ | Temp + Humidity | CR2032 |
| Xiaomi TH Sensor 2 | MJWSD05MMC | Temp + Humidity | CR2032 |

## Encryption Key Extraction

Xiaomi BLE sensors encrypt their advertisements. You need a **binding key**
(16-byte hex) to decode the data.

### Method 1: Xiaomi Cloud Token Extractor (Recommended)

```bash
# Install the token extractor
pip install micloud
git clone https://github.com/PiotrMachura/xiaomi-cloud-tokens-extractor
cd xiaomi-cloud-tokens-extractor
python token_extractor.py
```

The binding key is listed alongside the device token.

### Method 2: Telink Flasher (Advanced)

For LYWSD03MMC, you can flash custom firmware that broadcasts unencrypted:

1. Visit https://pvvx.github.io/ATC_MiThermometer/
2. Connect to the sensor via BLE from your phone
3. Flash ATC firmware (no encryption needed)

### Method 3: Mi Home App Logs

1. Add sensor to Mi Home app
2. Extract from app logs (Android, see xiaomi-miio.md method)

## Home Assistant Configuration

### Via UI (Recommended)

1. Ensure **Bluetooth** is enabled on your HA host machine
   - HA Yellow / HA OS: Built-in BLE
   - HA Container / Core: Need host Bluetooth adapter
2. **Settings > Devices & Services > Add Integration**
3. Search for **Xiaomi BLE**
4. Sensors within range auto-discover
5. Select the discovered sensor
6. Enter the **binding key** (16-byte hex, e.g., `a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6`)

### Configuration.yaml (Not Usually Needed)

BLE integration is configured via UI. For advanced setup:

```yaml
# configuration.yaml
# BLE is enabled by default in HA OS
# For manual bluetooth configuration:
bluetooth:
  # Optional: specify adapter
  # adapter: hci0
```

## Entity Names Generated

| Entity | Type | Location |
|--------|------|----------|
| `sensor.children_room_temperature` | sensor | Children's room (BLE) |
| `sensor.children_room_humidity` | sensor | Children's room (BLE) |
| `sensor.children_room_ble_battery` | sensor | Battery level (%) |

## BLE Signal Notes

- **Range**: BLE works reliably up to ~10m through one wall
- **Placement**: Avoid placing sensors directly on exterior walls or near windows
  (temperature readings will be skewed by outdoor conditions)
- **Update interval**: Xiaomi BLE sensors broadcast every ~10 minutes
- **HA host placement**: The HA server Bluetooth adapter must be within range
  of the sensor. Consider a Bluetooth proxy (ESPHome) if range is an issue

## ESPHome Bluetooth Proxy (Range Extender)

If the HA host is too far from the children's room, add an ESP32-based
BLE proxy:

```yaml
# ESPHome config for BLE proxy
esp32:
  board: esp32dev

bluetooth_proxy:
  active: true
```

Place the ESP32 between the HA host and the sensor to extend BLE range.

## Troubleshooting

- **Sensor not discovered**: Ensure HA Bluetooth is working:
  `Settings > System > Hardware > Bluetooth`
- **Binding key rejected**: Keys are case-sensitive, no spaces. Re-extract if needed.
- **Intermittent updates**: BLE range issue. Add a Bluetooth proxy.
- **Temperature offset**: Some sensors read 1-2 C high due to self-heating.
  Apply offset in HA sensor settings.
- **Battery draining fast**: CR2032 should last 12+ months. If draining faster,
  the sensor may be too far from any BLE receiver and increasing transmit power.
