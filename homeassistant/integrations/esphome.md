# ESPHome - SLWF-01pro Smart IR Controllers for Vivax AC Units

## Overview

The SLWF-01pro is a WiFi + IR blaster device that runs ESPHome firmware. Each
unit is installed in a room and controls one Vivax AC unit via infrared commands.
ESPHome exposes a `climate` entity in Home Assistant, allowing full temperature,
mode, and fan speed control.

## Hardware

- **Device**: SLWF-01pro (ESP8266-based, IR LED, temp/humidity sensor)
- **Quantity**: 4 (one per room)
- **Firmware**: Custom ESPHome YAML (uses `climate_ir` platform)
- **IR Protocol**: Vivax uses standard格力 (Gree) or Midea protocol depending on model

## Setup Steps

### 1. Flash ESPHome Firmware

```bash
# Install ESPHome (via HA add-on recommended)
# Or use: pip install esphome

# Create firmware for each device
esphome run slwf-01pro-room1.yaml
```

### 2. ESPHome YAML Configuration (per device)

```yaml
# slwf-01pro-room1.yaml
substitutions:
  name: slwf-01pro-room1
  friendly_name: "Living Room AC Controller"

esphome:
  name: ${name}
  friendly_name: ${friendly_name}

esp8266:
  board: esp01_1m

# WiFi credentials (or use secrets)
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

# Home Assistant API
api:
  encryption:
    key: !secret esp_encryption_key

# OTA updates
ota:
  - platform: esphome
    password: !secret esp_ota_password

# IR transmitter for AC control
remote_transmitter:
  pin: GPIO14
  carrier_duty_percent: 50%

# Climate entity (adjust protocol for your Vivax model)
climate:
  - platform: ToshibaAc  # or gree, midea - check your Vivax model
    name: "Living Room AC"
    transmitter_id: remote_transmitter
    # Supported modes: heat, cool, auto, dry, fan_only
    # Visual temperature range
    visual:
      min_temperature: 16
      max_temperature: 30
      temperature_step: 1.0

# Optional: built-in DHT sensor on SLWF-01pro
sensor:
  - platform: dht
    pin: GPIO4
    temperature:
      name: "Room 1 Controller Temperature"
    humidity:
      name: "Room 1 Controller Humidity"
```

### 3. Adopt in Home Assistant

After flashing, devices auto-discover in HA:
1. Go to **Settings > Devices & Services > ESPHome**
2. Click **Configure** on each discovered device
3. Enter encryption key from ESPHome build log

## Entity Names Generated

| Room | Climate Entity | Notes |
|------|---------------|-------|
| Living room | `climate.living_room_ac` | Main living space |
| Children's room | `climate.children_room_ac` | Night target warmer |
| Room 3 | `climate.room3_ac` | Standard control |
| Room 4 | `climate.room4_ac` | Standard control |

## IR Protocol Notes

Vivax ACs typically use one of these protocols:
- **Gree** (most common for budget Vivax units)
- **Midea** (some models)
- **Toshiba** (less common)

Check the remote control model number or try each protocol in ESPHome until
commands are accepted. The `climate_ir` ESPHome component supports all three.

## Troubleshooting

- **AC not responding**: Verify IR LED is aimed at AC receiver. Test with
  `remote_transmitter` raw transmit in ESPHome.
- **Intermittent control**: Increase `carrier_duty_percent` to 50% or position
  the blaster closer to the AC unit.
- **Duplicate commands**: Ensure only one ESPHome device per AC unit.
- **Temperature sensor drift**: The built-in DHT on SLWF-01pro may read high
  due to self-heating. Use AC built-in sensor for control (`sensor.room{n}_ac_temperature`).
