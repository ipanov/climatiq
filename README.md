# ClimatIQ

**Smart Home Climate Intelligence for a 4-Room Apartment**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![HA Core](https://img.shields.io/badge/Home%20Assistant-Core-blue.svg)](https://www.home-assistant.io/)
[![Platform](https://img.shields.io/badge/Platform-Galaxy%20S8-green.svg)]()

ClimatIQ is an autonomous climate control system running on Home Assistant Core
deployed to a Samsung Galaxy S8 via Termux and Udocker. It coordinates
multi-split AC units, air purifiers, a humidifier, and environmental sensors
to maintain thermal comfort (Fanger PMV/PPD, ASHRAE 55) and healthy indoor air
quality across four rooms -- all local, no cloud control dependency.

## Features

- **PMV/PPD thermal comfort** -- Fanger model (ASHRAE 55 / ISO 7730) computed
  from real sensor data, target PMV within +/-0.5
- **Multi-zone AC control** -- 4 Vivax indoor units via ESPHome SLWF-01pro
  dongles, coordinated heating/cooling
- **Air quality monitoring** -- CO2, TVOC, HCHO, PM2.5 with WHO/EU-compliant
  thresholds and automatic purifier activation
- **Humidity management** -- Evaporative humidification + dew point protection,
  season-adjusted targets
- **Predictive scheduling** -- Open-Meteo weather forecast and solar geometry
  feedforward for pre-heating/cooling
- **Priority cascade** -- Safety > Health > Comfort > Energy, enforced in every
  automation
- **Deadband protection** -- +/-1.5C, +/-5% RH, +/-100 ppm CO2 hysteresis
  prevents short-cycling
- **Budget-friendly** -- Total hardware investment of ~$70-88 (SLWF-01pro
  dongles, sensors, smart plug)

## Hardware Requirements

- Samsung Galaxy S8 (or any always-on Android with Termux support)
- Vivax multi-split AC with 4 indoor units
- Xiaomi Air Purifier 3H
- Smartmi Evaporative Humidifier 2
- Blueair Blue Pure 411
- XiaoMei WP6003 Air Quality Box
- Xiaomi BLE Temperature/Humidity Sensor
- SLWF-01pro ESPHome dongles (x4, ~$32-40)
- Shelly Plug S (~$12-15)

See [docs/device-inventory.md](docs/device-inventory.md) for the full
canonical device list.

## Quick Start

1. **Set up the hub** -- Follow [hardware/s8-setup-guide.md](hardware/s8-setup-guide.md)
   to install Termux, Udocker, and HA Core on the Galaxy S8.

2. **Procure hardware** -- See [hardware/shopping-list.md](hardware/shopping-list.md)
   for the bill of materials with purchasing links.

3. **Flash ESPHome** -- Program the SLWF-01pro dongles with the ESPHome
   configs in `homeassistant/integrations/esphome/`.

4. **Configure HA** -- Copy `homeassistant/` configs to your HA config
   directory and restart.

5. **Add BLE devices** -- Pair the XiaoMei WP6003 and Xiaomi BLE sensor
   through the HA BLE proxy integration.

## Documentation

- [Device Inventory](docs/device-inventory.md) -- Canonical hardware list
- [System Architecture](docs/architecture.md) -- Data flow and network diagrams
- [Reference Standards](docs/reference/) -- ASHRAE 55, ISO 7730, EN 16798-1, WHO AQG

## License

This project is licensed under the MIT License -- see the [LICENSE](LICENSE)
file for details.
