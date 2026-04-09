# WAQI - World Air Quality Index

## Overview

The WAQI (World Air Quality Index) integration provides outdoor air quality data
from monitoring stations worldwide. For Skopje, it reports real-time AQI values
that drive ClimatIQ's ventilation and air purification decisions.

**Station**: Skopje - Centar (or nearest available monitoring station)

## Setup Steps

### 1. Get a Free API Token

1. Visit https://aqicn.org/data-platform/token/
2. Fill in the form:
   - Name: Your name
   - Email: Your email
   - Purpose: "Home automation climate control"
3. Submit - token is emailed immediately
4. Token is a short alphanumeric string (not hex like Xiaomi tokens)

### 2. Find Your Station

Browse available stations at https://aqicn.org/city/macedonia/skopje/

Known Skopje stations:
- **Skopje - Centar** (GTC area)
- **Skopje - Karpos**
- **Skopje - Lisice**
- **Skopje - Miladinovci** (airport area)

Note the station ID (e.g., `@4829` for Skopje Centar).

### 3. Add Integration to Home Assistant

1. **Settings > Devices & Services > Add Integration**
2. Search for **World Air Quality Index (WAQI)**
3. Enter your **API token**
4. Enter the **station name** or **station ID**:
   - Station name: `skopje` (will find nearest)
   - Or exact: `@4829` (for specific station)
5. Submit

### 4. Verify Entity Creation

| Entity | Type | Purpose |
|--------|------|---------|
| `sensor.waqi` | sensor | Current AQI value (0-500 scale) |
| Attributes | - | PM2.5, PM10, O3, NO2, SO2, CO, timestamp |

## AQI Scale (US EPA Standard)

| AQI Range | Category | Color | Action |
|-----------|----------|-------|--------|
| 0-50 | Good | Green | No restriction |
| 51-100 | Moderate | Yellow | Unusually sensitive consider limiting |
| 101-150 | Unhealthy (Sensitive) | Orange | Sensitive groups reduce exertion |
| 151-200 | Unhealthy | Red | Everyone reduce outdoor exposure |
| 201-300 | Very Unhealthy | Purple | Avoid outdoor activity |
| 301+ | Hazardous | Maroon | Emergency conditions |

## ClimatIQ Usage

The AQI sensor drives:

### Template Sensors
- `sensor.air_quality_action` - maps AQI to action level
- `sensor.ventilation_advice` - closes windows when AQI > 100

### Automations
- **Blueair 411 Control** - ON when AQI > 100, OFF when < 50 + free cooling
- **AQI Warning Notification** - alert at AQI > 100
- **Ventilation Advice** - blocks window ventilation during poor AQI

## Skopje Air Quality Notes

Skopje frequently experiences poor winter air quality due to:
- Residential wood/coal heating
- Temperature inversions trapping pollutants
- Vehicle emissions in the valley

AQI can exceed 200 during winter inversions. ClimatIQ will:
1. Keep all windows closed (ventilation_advice = ac_preferred)
2. Run all air purifiers at maximum
3. Send warning notifications

## Data Refresh Rate

WAQI updates every **15-30 minutes** depending on the station.

## Troubleshooting

- **Station not found**: Try using the station ID with `@` prefix instead of name.
- **Stale data**: WAQI stations occasionally go offline. Check https://aqicn.org
  for station status.
- **Wrong station**: If multiple stations exist, use the station ID for precise
  selection.
- **Token rejected**: Ensure you are using the WAQI token (not a Xiaomi token).
  Re-request from aqicn.org if needed.
- **Attribute access**: PM2.5 sub-values are in the entity attributes:
  `{{ state_attr('sensor.waqi', 'pm2_5') }}`
