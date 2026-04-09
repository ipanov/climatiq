# Device Inventory — ClimatIQ

Canonical hardware list with integration details. This is the authoritative
source for all entity naming and integration configuration.

---

## Hub

### Samsung Galaxy S8 (SM-G950F)

| Field | Value |
|-------|-------|
| Role | Home Assistant hub |
| Location | Central (hallway or living room) |
| OS | Android 9 + Termux + Udocker |
| HA | Home Assistant Core (latest stable) |
| Connectivity | WiFi (home router) |
| BLE | Built-in (used as BLE proxy for sensors) |
| Notes | Always-on, plugged into charger. Termux:BOOT for auto-start. |

---

## Climate Control

### Vivax Multi-Split AC System (4 indoor units)

| Field | Value |
|-------|-------|
| Model | Vivax multi-split (exact model TBD) |
| Units | 4 indoor units (one per room) |
| Location | Room 1 (Living), Room 2 (Children), Room 3, Room 4 |
| Connection | SLWF-01pro WiFi dongle per unit (ESPHome) |
| HA Integration | ESPHome (auto-discovered once flashed) |
| Control | Full: temperature setpoint, mode (heat/cool/auto/fan), fan speed |
| Sensors provided | Room temperature (each unit) |
| Entity pattern | `climate.room{n}_ac`, `sensor.room{n}_ac_temperature` |
| Notes | SLWF-01pro replaces the IR remote with WiFi. Each dongle runs ESPHome firmware. Flash before HA integration. |
| Quantity | 4 (one per indoor unit) |

---

## Air Purifiers

### Xiaomi Air Purifier 3H

| Field | Value |
|-------|-------|
| Model | Xiaomi Mi Air Purifier 3H (AC-M7-SC) |
| Location | Living room |
| Connection | WiFi (2.4 GHz) |
| HA Integration | Xiaomi Miio (native) |
| Control | Power, mode (auto/silent/favorite), fan speed, favorite level |
| Sensors provided | PM2.5 (ug/m3), temperature, humidity, filter life remaining |
| Entity pattern | `purifier.xiaomi_3h`, `sensor.room1_pm25`, `sensor.room1_purifier_temperature`, `sensor.room1_purifier_humidity`, `sensor.purifier_3h_filter_life` |
| Notes | Primary air quality sensor for living room. Miio integration provides rich data without needing the Xiaomi app. |

### Blueair Blue Pure 411

| Field | Value |
|-------|-------|
| Model | Blueair Blue Pure 411 |
| Location | Children's room |
| Connection | None (dumb device) -> Shelly Plug S via WiFi |
| HA Integration | Shelly (switch on/off only) |
| Control | Power on/off (no speed control) |
| Sensors provided | None (dumb device, no feedback) |
| Entity pattern | `switch.shelly_blueair` |
| Notes | No built-in WiFi or sensors. Controlled via smart plug. Filter status is manual tracking only. |

---

## Humidifier

### Smartmi Evaporative Humidifier 2

| Field | Value |
|-------|-------|
| Model | Smartmi Evaporative Humidifier 2 (CHV7002C-EW) |
| Location | Living room |
| Connection | WiFi (2.4 GHz) |
| HA Integration | Xiaomi Miio (native) |
| Control | Power, target humidity, mode (auto/low/medium/high), LED |
| Sensors provided | Current humidity (internal), water level, filter status |
| Entity pattern | `humidifier.smartmi`, `sensor.smartmi_water_level` |
| Notes | Evaporative (no mist, no white dust). Miio integration gives full control. Use `sensor.room1_humidity` from Purifier 3H as the reference humidity sensor (not the internal one). |

---

## Environmental Sensors

### XiaoMei WP6003 Air Quality Box

| Field | Value |
|-------|-------|
| Model | XiaoMei WP6003 (also sold as WP6003 Air Quality Detector) |
| Location | Living room |
| Connection | BLE (Bluetooth Low Energy) |
| HA Integration | ESP32 BLE client (or S8 built-in BLE as proxy) |
| Sensors provided | CO2 (ppm), TVOC (mg/m3), HCHO (mg/m3), temperature, humidity |
| Entity pattern | `sensor.room1_co2`, `sensor.room1_tvoc`, `sensor.room1_hcho`, `sensor.xiaomei_temperature`, `sensor.xiaomei_humidity` |
| Notes | BLE-only, no WiFi. Use ESP32 as BLE-MQTT bridge, or use the S8's built-in BLE via HA BLE proxy integration. Polling interval: 60 seconds minimum to preserve battery. |

### Xiaomi BLE Temperature/Humidity Sensor

| Field | Value |
|-------|-------|
| Model | Xiaomi LYWSDCGQ (round display) or LYWSD03MMC (small square) |
| Location | Children's room |
| Connection | BLE |
| HA Integration | Xiaomi BLE (via HA passive BLE proxy on S8 or ESP32) |
| Sensors provided | Temperature, humidity |
| Entity pattern | `sensor.room2_temperature`, `sensor.room2_humidity` |
| Notes | Single sensor for children's room. BLE broadcast interval ~10 min. Battery lasts ~12 months. |

---

## Other Devices

### Xiaomi X20+ Robot Vacuum

| Field | Value |
|-------|-------|
| Model | Xiaomi Robot Vacuum X20+ (BHR5824EU) |
| Location | Living room (docking station) |
| Connection | WiFi (2.4 GHz) |
| HA Integration | Xiaomi Miot Auto (HACS custom integration) |
| Control | Start, stop, pause, return to dock, set fan speed |
| Sensors provided | Battery, status, last clean area |
| Entity pattern | `vacuum.xiaomi_x20`, `sensor.vacuum_battery` |
| Notes | Not directly climate-related, but vacuuming affects PM2.5 readings. Automations should account for PM2.5 spikes during/after vacuum runs (ignore PM2.5 for 30 min after vacuum completes). |

---

## Network Infrastructure

### WiFi

- Router: existing home router (2.4 GHz, IoT VLAN recommended)
- All WiFi devices on same subnet as HA
- Static IP for HA on S8 recommended

### BLE

- S8 built-in Bluetooth can act as BLE proxy
- Optional: dedicated ESP32 as BLE-MQTT bridge for reliability
- BLE range: ~10m through walls (apartment should be fully covered)

---

## Cloud Services (Read-Only)

### Open-Meteo

| Field | Value |
|-------|-------|
| Purpose | Outdoor temperature, humidity, solar radiation, forecast |
| API | Free, no API key required |
| HA Integration | Open-Meteo (native) |
| Polling | Every 15 minutes |
| Entity pattern | `sensor.outdoor_temperature`, `sensor.outdoor_humidity` |
| Notes | Provides 24h forecast for predictive scheduling. Solar radiation data enables sun-preheat/precool automations. |

### World Air Quality Index (WAQI)

| Field | Value |
|-------|-------|
| Purpose | Outdoor AQI, PM2.5, PM10 |
| API | Free token from waqi.info |
| HA Integration | WAQI (native) |
| Polling | Every 30 minutes |
| Entity pattern | `sensor.outdoor_aqi`, `sensor.outdoor_pm25` |
| Notes | Nearest station: Skopje. Used for feedforward -- if outdoor AQI is poor, keep windows closed strategy (purifiers work harder). |

---

## Budget Summary

| Item | Qty | Unit Cost | Total |
|------|-----|-----------|-------|
| SLWF-01pro ESPHome dongle | 4 | ~$8-10 | $32-40 |
| Shelly Plug S | 1 | ~$12-15 | $12-15 |
| Xiaomi BLE Temp/Humidity | 1 | ~$5-8 | $5-8 |
| XiaoMei WP6003 | 1 | ~$15-20 | $15-20 |
| Optional: ESP32 BLE bridge | 1 | ~$5 | $5 |
| **Total** | | | **$69-88** |

All other devices (ACs, Purifier 3H, Humidifier, Vacuum, Galaxy S8) are
assumed to be already owned.
