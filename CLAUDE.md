# ClimatIQ — Smart Home Climate Intelligence

> Autonomous climate control for a 4-room apartment in Skopje, Macedonia.
> Home Assistant Core on Samsung Galaxy S8 (Termux/Udocker).
> Fanger PMV/PPD comfort model, ASHRAE 55 / ISO 7730 compliance.

## Project Overview

ClimatIQ is a climate intelligence system that maintains thermal comfort,
healthy humidity, and clean air across a 4-room apartment using local-only
Home Assistant automation. It combines multi-split AC control, air purifiers,
a humidifier, and BLE/WiFi environmental sensors into a single coordinated
control loop with predictive scheduling and outdoor weather integration.

**Hub:** Samsung Galaxy S8 running Termux + Udocker (HA Core).
**Budget:** ~$70-88 total.
**Philosophy:** Safety > Health > Comfort > Energy, in that order.

## Device Inventory

| Device | Location | Connection | HA Integration |
|--------|----------|------------|----------------|
| Vivax Multi-Split AC x4 | All rooms | SLWF-01pro ESPHome dongles | ESPHome auto-discover |
| Xiaomi Air Purifier 3H | Living room | WiFi | Xiaomi Miio (PM2.5 + temp + humidity) |
| Blueair Blue Pure 411 | Children's room | Dumb -> Shelly plug | Switch on/off |
| Smartmi Evaporative Humidifier 2 | Living room | WiFi | Xiaomi Miio (full control) |
| XiaoMei WP6003 Air Quality Box | Living room | BLE | ESP32 BLE client (or S8 BLE proxy) |
| Xiaomi X20+ Robot Vacuum | Living room base | WiFi | Xiaomi Miot Auto (HACS) |
| Xiaomi BLE Temp/Humidity Sensor x1 | Children's room | BLE | Xiaomi BLE via proxy |
| Samsung Galaxy S8 | Hub | -- | Termux/Udocker HA Core |

## Sensor Coverage

| Room | Temperature | Humidity | Air Quality |
|------|------------|----------|-------------|
| Living Room | AC + Purifier 3H | Purifier 3H | PM2.5 (Purifier) + CO2/TVOC/HCHO (XiaoMei) |
| Children's Room | AC + Xiaomi BLE | Xiaomi BLE | Blueair 411 (filtering only, no data) |
| Room 3 | AC only | -- | -- |
| Room 4 | AC only | -- | -- |

**Known gaps:** Rooms 3 and 4 lack humidity and air quality sensors.
Address in future hardware iteration if needed.

## Room Layout

```
                    NORTH (TBD)
                +------------------+
                |     Room 3      |
                |  (window: TBD)  |
                +------------------+
                |     Room 4      |
                |  (window: TBD)  |
WEST  +--------+--------+---------+  EAST
(TBD) | Children's Room | Living Room  | (TBD)
      | (window: TBD)  | (window: TBD)|
      +--------+--------+---------+
                |     Hallway      |
                +------------------+
                    SOUTH (TBD)
```

Window orientations are TBD -- the user must fill these in. Sun geometry
automation depends on accurate window-facing directions (N/S/E/W).

## Control Laws

### 1. Deadband (Hysteresis)

Prevents short-cycling. Devices do not toggle within the deadband.

| Parameter | Deadband |
|-----------|----------|
| Temperature | +/-1.5 degC |
| Humidity | +/-5% RH |
| CO2 | +/-100 ppm |

### 2. Setpoint Scheduling

Time-of-day + season targets based on ASHRAE 55 recommendations.

| Period | Season | Temp Target | RH Target |
|--------|--------|-------------|-----------|
| Morning (6-9) | Summer | 24 degC | 45% |
| Day (9-17) | Summer | 25 degC | 45% |
| Evening (17-22) | Summer | 24 degC | 50% |
| Night (22-6) | Summer | 23 degC | 50% |
| Morning (6-9) | Winter | 22 degC | 40% |
| Day (9-17) | Winter | 21 degC | 35% |
| Evening (17-22) | Winter | 22 degC | 40% |
| Night (22-6) | Winter | 20 degC | 40% |

### 3. Feedforward (Predictive)

- Sun geometry: window orientation + solar position -> pre-cool/heat
- Weather forecast: Open-Meteo 24h forecast -> adjust setpoints
- AQI trends: WAQI outdoor AQI -> adjust ventilation strategy

### 4. Priority Cascade

```
Safety (frost, overheat, CO2 > 2000 ppm)
  > Health (CO2 < 1000, PM2.5 < 12, TVOC < 0.3)
    > Comfort (PMV +/-0.5, dew point < 15 degC)
      > Energy (minimize runtime, avoid peak hours)
```

## Key Thresholds

| Metric | Target | Warning | Critical | Unit |
|--------|--------|---------|----------|------|
| Temperature | 20-25 | <18 or >27 | <15 or >32 | degC |
| Humidity | 25-60 | <20 or >65 | <15 or >75 | % RH |
| Dew Point | < 15 | > 15 | > 18 | degC |
| CO2 | < 800 | > 1000 | > 2000 | ppm |
| TVOC | < 0.1 | > 0.3 | > 1.0 | mg/m3 |
| HCHO | < 0.03 | > 0.05 | > 0.1 | mg/m3 |
| PM2.5 | < 12 | > 35 | > 75 | ug/m3 |
| PMV (Fanger) | -0.5 to +0.5 | | +/-1.0 | -- |
| PPD | < 10% | > 20% | > 40% | % |

## HA Entity Naming Convention

All entity IDs follow this pattern:

```
# Climate (AC units)
climate.room{n}_ac                    # n = 1-4

# Sensors (from integrations, renamed via customize)
sensor.room{n}_temperature
sensor.room{n}_humidity
sensor.room1_pm25                      # Purifier 3H
sensor.room1_co2                       # XiaoMei WP6003
sensor.room1_tvoc                      # XiaoMei WP6003
sensor.room1_hcho                      # XiaoMei WP6003
sensor.room2_temperature               # Xiaomi BLE
sensor.room2_humidity                  # Xiaomi BLE

# Switches
switch.shelly_blueair                  # Blueair 411 via Shelly plug
switch.humidifier                      # Smartmi power state

# Humidifier
humidifier.smartmi                     # Smartmi Evaporative Humidifier 2

# Purifier
purifier.xiaomi_3h                     # Xiaomi Air Purifier 3H

# Vacuum
vacuum.xiaomi_x20                      # Robot vacuum

# Outdoor (REST integrations)
sensor.outdoor_temperature             # Open-Meteo
sensor.outdoor_humidity                # Open-Meteo
sensor.outdoor_aqi                     # WAQI
sensor.outdoor_pm25                    # WAQI

# Template sensors (computed)
sensor.room{n}_dew_point
sensor.room{n}_pmv
sensor.room{n}_ppd
sensor.room{n}_comfort_score
```

## File Structure

```
climatiq/
├── CLAUDE.md                          # This file -- project instructions
├── README.md                          # Project overview
├── .gitignore                         # Git ignore rules
├── docs/
│   ├── device-inventory.md            # Canonical device list with full details
│   ├── architecture.md                # System architecture diagrams
│   └── reference/                     # Reference HTML documents
│       ├── ashrae-55-2020.html
│       ├── iso-7730-2005.html
│       ├── en-16798-1-2019.html
│       └── who-air-quality-2021.html
├── hardware/
│   ├── shopping-list.md               # Bill of materials with links
│   └── s8-setup-guide.md              # Galaxy S8 Termux/Udocker HA setup
├── homeassistant/
│   ├── configuration.yaml             # Main HA config (includes)
│   ├── automations.yaml               # Climate automation definitions
│   ├── scripts.yaml                   # HA scripts
│   ├── templates.yaml                 # Template sensors (PMV, dew point)
│   ├── schedules.yaml                 # Setpoint schedules
│   ├── customize.yaml                 # Entity ID overrides
│   └── integrations/
│       ├── esphome/                   # SLWF-01pro dongle configs (x4)
│       ├── xiaomi_miio.yaml           # Purifier + Humidifier config
│       ├── xiaomi_miot.yaml           # Vacuum config
│       ├── shelly.yaml                # Shelly plug config
│       ├── open_meteo.yaml            # Weather integration
│       ├── waqi.yaml                  # Air quality index
│       └── ble_proxy.yaml             # BLE proxy / ESP32 client config
└── scripts/
    ├── pmv_calculator.py              # Fanger PMV/PPD (standalone)
    ├── comfort_score.py               # Aggregate comfort metric
    ├── deploy.sh                      # Deploy config to S8
    └── simulate.py                    # Simulate automations from history
```

## MCP Servers

| Server | Purpose | When to Use |
|--------|---------|-------------|
| Context7 | Home Assistant docs | HA integration config, automation syntax, template sensor API |
| Web Search / Reader | Research | AQI standards, ESPHome device configs, SLWF-01pro setup guides |

CAD MCPs (FreeCAD, DXF viewer) are NOT relevant to this project.

## Reference Documents

Four HTML files in `docs/reference/`:

| File | Standard | Use For |
|------|----------|---------|
| `ashrae-55-2020.html` | ASHRAE 55-2020 | Thermal comfort criteria, PMV/PPD ranges |
| `iso-7730-2005.html` | ISO 7730:2005 | Detailed PMV calculation method, comfort categories |
| `en-16798-1-2019.html` | EN 16798-1:2019 | European indoor environment design criteria |
| `who-air-quality-2021.html` | WHO AQG 2021 | PM2.5, CO2, TVOC, HCHO health-based limits |

## Science References

- **Thermal comfort:** Fanger PMV/PPD model (ASHRAE 55 / ISO 7730). Target PMV in [-0.5, +0.5], corresponding to PPD < 10%.
- **Humidity:** 25-60% RH per ASHRAE 55. Dew point kept below 15 degC to prevent condensation and mold. Winter targets lower (35-40%) due to cold outdoor air and condensation risk on windows.
- **Air quality:** CO2 < 1000 ppm (EN 16798-1 category I), TVOC < 0.3 mg/m3, HCHO < 0.03 mg/m3 (WHO guideline), PM2.5 < 12 ug/m3 (WHO annual interim target).
- **Outdoor data:** Open-Meteo (free, no API key) for temperature, humidity, solar radiation forecast. WAQI (free token) for outdoor AQI and PM2.5.

## Automation Principles

1. **Local-first:** All automations run on the S8. Cloud services are read-only (weather data).
2. **Idempotent:** Re-running an automation does not change state if targets are met.
3. **Graceful degradation:** If BLE sensors go offline, fall back to AC-integrated temperature. If weather API fails, use last-known values.
4. **No oscillation:** Deadbands prevent rapid on/off cycling. Minimum runtime of 5 minutes per device toggle.
5. **Transparent:** Every automation logs its reasoning (which sensor triggered, what threshold was crossed).
