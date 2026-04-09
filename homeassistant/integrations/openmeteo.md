# Open-Meteo - Outdoor Weather Data

## Overview

Open-Meteo is a free weather API that provides comprehensive meteorological data
without requiring an API key. It is used as the primary outdoor weather source
for ClimatIQ's climate intelligence calculations.

**Location**: Skopje, North Macedonia (41.9973, 21.4280)

## Setup Steps

### 1. Configure Home Assistant Location

1. **Settings > General**
2. Set location:
   - Latitude: `41.9973`
   - Longitude: `21.4280`
   - Elevation: `240` (meters, Skopje average)
   - Timezone: `Europe/Skopje`
3. Save

### 2. Add Open-Meteo Integration

1. **Settings > Devices & Services > Add Integration**
2. Search for **Open-Meteo**
3. Select weather mode:
   - **Current weather + hourly forecast** (recommended for ClimatIQ)
4. Location auto-fills from HA settings
5. Submit - no API key needed

### 3. Verify Entity Creation

Check that these entities are available:

| Entity | Type | Purpose |
|--------|------|---------|
| `sensor.open_meteo_temperature` | sensor | Current outdoor temperature |
| `sensor.open_meteo_humidity` | sensor | Outdoor relative humidity (%) |
| `sensor.open_meteo_dew_point` | sensor | Calculated dew point (C) |
| `sensor.open_meteo_cloud_cover` | sensor | Cloud cover (%) - used for solar load |
| `sensor.open_meteo_wind_speed` | sensor | Wind speed (km/h) |
| `sensor.open_meteo_wind_bearing` | sensor | Wind direction (degrees) |
| `sensor.open_meteo_pressure` | sensor | Atmospheric pressure (hPa) |
| `sensor.open_meteo_precipitation` | sensor | Precipitation (mm) |
| `weather.open_meteo` | weather | Full weather entity for UI |

## ClimatIQ Usage

Open-Meteo data feeds these template sensors and automations:

### Template Sensors
- `sensor.target_humidity` - adjusts based on outdoor temp (condensation risk)
- `sensor.ventilation_advice` - open_windows / keep_closed / ac_preferred
- `sensor.sun_exposure_intensity` - cloud cover modulates solar load
- `sensor.room{n}_solar_load` - cloud cover affects solar heat gain
- `sensor.room{n}_temp_differential` - indoor vs outdoor temp difference
- `binary_sensor.free_cooling_available` - outdoor temp + humidity check

### Automations
- Climate Master Controller - determines heat/cool mode
- Blueair 411 Control - free cooling check before turning off
- Fresh Air Notification - conditions for window ventilation

## Data Refresh Rate

Open-Meteo updates every **15 minutes** in Home Assistant. This matches the
master controller's 15-minute cycle perfectly.

## Why Open-Meteo (Not Other Weather Services)

| Feature | Open-Meteo | Other (AccuWeather, etc.) |
|---------|-----------|--------------------------|
| API Key | Not needed | Required (free tier limited) |
| Free tier | Unlimited | Limited calls/day |
| Data quality | Excellent (ERA5 reanalysis) | Varies |
| HA integration | Built-in | Some need HACS |
| Cloud cover | Yes (exact %) | Sometimes binary |

## Troubleshooting

- **Missing entities**: Some sensors only appear if the hourly forecast mode
  is selected during setup. Re-configure the integration.
- **Stale data**: Open-Meteo should update every 15 min. Check HA logs for
  API errors. Rate limited only if making >10,000 calls/day.
- **Wrong location**: Verify coordinates in HA Settings > General.
- **Cloud cover missing**: Ensure hourly forecast is enabled. Cloud cover is
  an hourly parameter.
