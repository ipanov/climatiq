# XiaoMei WP6003 - Air Quality Monitor (BLE)

## Overview

The XiaoMei WP6003 is a compact air quality monitor that measures CO2, TVOC,
and HCHO (formaldehyde) via BLE. It is located in the living room and provides
indoor air quality data for ventilation decisions and health alerts.

Since HA does not have a native XiaoMei integration, the WP6003 is connected
via an **ESP32 BLE client** running ESPHome. The ESP32 acts as a bridge:
it reads BLE advertisements from the WP6003 and exposes the data to HA
through ESPHome's native API.

## Hardware

- **Sensor**: XiaoMei WP6003 (BLE air quality monitor)
- **Bridge**: ESP32 development board (ESP32-D0WDQ6 or similar)
- **Power**: USB power for ESP32 (permanent installation)

## Supported Measurements

| Measurement | Entity | Unit | Alert Threshold |
|-------------|--------|------|-----------------|
| CO2 | `sensor.living_room_co2` | ppm | > 1000 (ASHRAE 62.1) |
| TVOC | `sensor.living_room_tvoc` | mg/m3 | > 0.5 (ref) |
| HCHO | `sensor.living_room_hcho` | mg/m3 | > 0.08 (WHO guideline) |

## Setup Steps

### 1. Get the WP6003 BLE MAC Address

```bash
# On a Linux/Android device with BLE:
bluetoothctl
scan on
# Look for "WP6003" or "XiaoMei" in the scan results
# Note the MAC address (e.g., AA:BB:CC:DD:EE:FF)
```

Or use the XiaoMei smartphone app to find the MAC in device info.

### 2. Flash ESP32 with ESPHome

```bash
# Create ESPHome config
esphome run wp6003-ble-bridge.yaml
```

### 3. ESPHome Configuration

```yaml
# wp6003-ble-bridge.yaml
substitutions:
  name: wp6003-ble-bridge
  friendly_name: "WP6003 BLE Bridge"

esphome:
  name: ${name}
  friendly_name: ${friendly_name}

esp32:
  board: esp32dev

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret wp6003_bridge_key

ota:
  - platform: esphome

# BLE client for WP6003
ble_client:
  - mac_address: "AA:BB:CC:DD:EE:FF"  # Replace with WP6003 MAC
    id: wp6003_device

# Sensor definitions
sensor:
  # CO2 sensor
  - platform: ble_client
    ble_client_id: wp6003_device
    service_uuid: "0000fff0-0000-1000-8000-00805f9b34fb"
    characteristic_uuid: "0000fff4-0000-1000-8000-00805f9b34fb"
    name: "Living Room CO2"
    id: living_room_co2
    unit_of_measurement: "ppm"
    accuracy_decimals: 0
    # Note: Actual UUID and parsing may vary.
    # Use ESPHome BLE monitor to discover correct service/characteristic.

  # TVOC sensor
  - platform: ble_client
    ble_client_id: wp6003_device
    name: "Living Room TVOC"
    id: living_room_tvoc
    unit_of_measurement: "mg/m3"
    accuracy_decimals: 3

  # HCHO sensor
  - platform: ble_client
    ble_client_id: wp6003_device
    name: "Living Room HCHO"
    id: living_room_hcho
    unit_of_measurement: "mg/m3"
    accuracy_decimals: 3
```

### 4. Discover BLE Service UUIDs

The exact BLE service and characteristic UUIDs may vary between WP6003
firmware versions. To discover them:

1. Flash ESP32 with a BLE scanner config:
   ```yaml
   # Add to ESPHome config for discovery
   esp32_ble_tracker:
   ```
2. Watch the ESPHome logs for discovered services/characteristics
3. Update the sensor configs with the correct UUIDs

Alternatively, use **nRF Connect** app on Android/iOS to explore the WP6003
BLE services and find the correct characteristic UUIDs for each measurement.

### 5. Alternative: Passive BLE Monitor (HACS)

If the ESP32 bridge approach is too complex, try the **Passive BLE Monitor**
HACS integration which may support the WP6003 directly:

1. Install HACS: https://hacs.xyz
2. Search for **Passive BLE Monitor** in HACS
3. Install and configure with WP6003 MAC address
4. Check if sensors are auto-detected

## Entity Names Generated

| Entity | Type | Purpose |
|--------|------|---------|
| `sensor.living_room_co2` | sensor | CO2 concentration (ppm) |
| `sensor.living_room_tvoc` | sensor | Total VOC (mg/m3) |
| `sensor.living_room_hcho` | sensor | Formaldehyde (mg/m3) |

## ClimatIQ Usage

### Automations
- **CO2 Warning** - Notify when CO2 > 1000 ppm
- **HCHO Warning** - Notify when HCHO > 0.08 mg/m3
- **Ventilation Advice** - Considers CO2 for window ventilation recommendation

### Template Sensors
- `sensor.ventilation_advice` - incorporates CO2 level in decision
- `binary_sensor.free_cooling_available` - checks CO2 < 1000

## Placement Notes

- Place the WP6003 at **breathing height** (1.0-1.5m) in the living room
- Avoid placing near windows, doors, or AC vents (skewed readings)
- Keep away from direct sunlight (heat affects sensor accuracy)
- Allow 5-10 minutes for warm-up after power-on for stable readings

## Calibration

The WP6003 may require periodic calibration:
- **CO2**: Auto-calibrates to 400 ppm baseline (outdoor fresh air)
  - For best results, take it outside for 30 min every few months
- **TVOC/HCHO**: Zero calibration in clean outdoor air
  - Follow manufacturer instructions for calibration procedure

## Troubleshooting

- **ESP32 not connecting to WP6003**: Verify MAC address. Ensure WP6003 is
  powered on and within BLE range (< 5m).
- **NaN sensor values**: BLE characteristic parsing mismatch. Re-discover
  UUIDs with nRF Connect and update ESPHome config.
- **Sensors not updating**: BLE connection drops. Add `update_interval`
  and reconnection logic in ESPHome config.
- **Readings seem wrong**: Warm up for 10 min. Calibrate outdoors.
- **High CO2 indoors**: Normal for occupied rooms. Ventilate when > 1000 ppm.
