# Shelly - Smart Plug S Devices

## Overview

Shelly Plug S devices provide on/off control and power monitoring via WiFi.
Two Shelly plugs are deployed:

1. **Blueair 411 Air Purifier** (children's room) - simple on/off control
2. **Galaxy S8 Charger** - battery cycling (stop at 80%, start at 20%)

Shelly devices use CoIoT protocol for auto-discovery on the local network.

## Hardware

- **Device**: Shelly Plug S (gen1 or gen2)
- **Quantity**: 2
- **Max load**: 12A (sufficient for air purifier and phone charger)

## Setup Steps

### 1. Physical Setup

1. Plug Shelly into wall outlet
2. Plug device (Blueair / charger) into Shelly
3. Shelly creates a WiFi AP: `ShellyPlugS-XXXXXX`

### 2. WiFi Configuration

1. Connect to the Shelly AP from your phone/PC
2. Open `http://192.168.33.1` in a browser
3. Enter your home WiFi credentials
4. Shelly connects and gets an IP from DHCP

### 3. Firmware Update

1. Open the Shelly web UI at its assigned IP
2. Go to **Settings > Firmware**
3. Update to latest stable firmware
4. Reboot the device

### 4. Home Assistant Auto-Discovery

Shelly devices auto-discover in HA via mDNS/CoIoT:

1. **Settings > Devices & Services**
2. Shelly devices appear in **Discovered** section
3. Click **Configure** on each device
4. Optionally set authentication credentials

### 5. Assign Static IPs

Configure DHCP reservations in your router:
- Blueair Shelly: `192.168.1.110`
- S8 Charger Shelly: `192.168.1.111`

### 6. Rename Entities

After discovery, rename entities in HA:

| Default Name | Rename To | Purpose |
|-------------|-----------|---------|
| `switch.shellyplug_s_xxxxxx_1` | `switch.shelly_blueair` | Blueair 411 power control |
| `switch.shellyplug_s_yyyyyy_1` | `switch.shelly_s8_charger` | S8 charger power control |

## Entity Names Generated

| Entity | Type | Purpose |
|--------|------|---------|
| `switch.shelly_blueair` | switch | Blueair 411 on/off |
| `sensor.shelly_blueair_power` | sensor | Power consumption (W) |
| `sensor.shelly_blueair_energy` | sensor | Cumulative energy (kWh) |
| `switch.shelly_s8_charger` | switch | S8 charger on/off |
| `sensor.shelly_s8_charger_power` | sensor | Power consumption (W) |
| `sensor.shelly_s8_charger_energy` | sensor | Cumulative energy (kWh) |

## Power Monitoring Notes

Shelly Plug S reports real-time power draw. Useful for:
- Detecting when Blueair filter is clogged (increased power draw)
- Confirming S8 is actually charging (power > 0)
- Energy cost tracking

## Gen1 vs Gen2

| Feature | Gen1 | Gen2 |
|---------|------|------|
| Protocol | CoIoT | RPC/MQTT |
| HA Integration | Built-in Shelly | Built-in Shelly |
| Power metering | Yes | Yes |
| Auto-discovery | mDNS | mDNS |

Both generations work identically in Home Assistant.

## Troubleshooting

- **Not discovered**: Ensure device is on same WiFi network. Check mDNS is not
  blocked by router AP isolation.
- **Intermittent disconnection**: Shelly gen1 can be unstable on crowded WiFi.
  Enable CoIoT in device settings and set HA IP as CoIoT peer.
- **Entity naming**: After renaming in HA UI, automations use the new names.
- **Power readings inaccurate**: Calibrate in Shelly web UI under Settings.
