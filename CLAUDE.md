# ClimatIQ — Smart Home Climate Intelligence Framework

> Generic, extensible climate control framework for any home.
> ASHRAE 55 / ISO 7730 compliant. Python. Home Assistant integration.
> Reference deployment: 4-room apartment, Skopje, Macedonia.

## Project Overview

ClimatIQ is a **generic open-source framework** for intelligent home climate control.
It provides domain models, comfort algorithms, control strategies, and provider interfaces
that work with any home layout, any devices, and any location. It is NOT hardcoded to a
specific apartment — the Skopje deployment is a reference implementation.

**Architecture:** SOLID, DDD, OOP with Pydantic models and abstract provider interfaces.
**Science:** Fanger PMV/PPD (via `pythermalcomfort`), Magnus dew point, ASHRAE 55 thresholds.
**Philosophy:** Safety > Health > Comfort > Energy, enforced via PriorityCascade.

## Tech Stack

- **Language:** Python 3.10+
- **Validation:** Pydantic v2
- **Comfort:** pythermalcomfort (ASHRAE 55 / ISO 7730 PMV/PPD)
- **Testing:** pytest, pytest-cov
- **Linting:** ruff, mypy (strict)
- **CI/CD:** GitHub Actions (lint + test + YAML validate on every PR)
- **Pre-commit:** ruff, mypy, pytest fast suite

## File Structure

```
climatiq/
├── CLAUDE.md                          # This file
├── README.md                          # Project overview with badges
├── LICENSE                            # MIT
├── pyproject.toml                     # Python project config
├── .pre-commit-config.yaml            # Pre-commit hooks
├── .github/workflows/
│   ├── ci.yml                         # Lint + test + YAML validate
│   └── doc-freshness.yml              # Weekly doc structure check
├── src/climatiq/                      # Main package
│   ├── __init__.py
│   ├── config.py                      # Pydantic config loader
│   ├── models/                        # Domain models (Pydantic)
│   │   ├── home.py                    # Home, Zone, WindowOrientation
│   │   ├── sensors.py                 # SensorReading, SensorType
│   │   ├── devices.py                 # Device, DeviceType, DeviceCapability
│   │   ├── comfort.py                 # ComfortTarget, PMVResult, ComfortResult
│   │   ├── environment.py             # OutdoorConditions, AirQualityReading
│   │   └── schedule.py                # Season, TimePeriod, ScheduleEntry
│   ├── providers/                     # Abstract interfaces
│   │   └── base.py                    # SensorProvider, DeviceController, etc.
│   ├── comfort/                       # Comfort algorithms
│   │   ├── pmv.py                     # PMV/PPD via pythermalcomfort
│   │   ├── dew_point.py               # Magnus formula
│   │   ├── score.py                   # Aggregate comfort score (0-100)
│   │   └── thresholds.py              # Safety/health/comfort thresholds
│   └── controllers/                   # Control strategies
│       ├── engine.py                  # Main ControlEngine orchestrator
│       ├── deadband.py                # Hysteresis controller
│       ├── schedule.py                # Time-of-day setpoint controller
│       ├── priority.py                # Safety > Health > Comfort > Energy
│       └── feedforward.py             # Predictive (solar, weather)
├── tests/                             # Test suite
│   ├── conftest.py
│   ├── test_models/                   # Model validation tests
│   ├── test_comfort/                  # PMV, dew point, score tests
│   └── test_controllers/             # Deadband, schedule, priority tests
├── config/
│   └── example-home.yaml             # Example home configuration
├── docs/
│   ├── architecture.md               # Architecture with Mermaid diagrams
│   ├── device-inventory.md           # Reference deployment devices
│   └── reference/                    # Standard references
├── homeassistant/                     # Reference HA config (Skopje deployment)
│   ├── configuration.yaml
│   ├── automations.yaml
│   ├── templates.yaml
│   ├── inputs.yaml
│   └── integrations/
└── hardware/                          # Reference deployment hardware docs
    ├── shopping-list.md
    ├── s8-setup-guide.md
    └── vivax-ac-research.md
```

## Key Abstractions

| Interface | Purpose | Implementations |
|-----------|---------|-----------------|
| `SensorProvider` | Read sensor data | Home Assistant, MQTT, REST |
| `DeviceController` | Control devices | Home Assistant, ESPHome |
| `WeatherProvider` | Outdoor weather | Open-Meteo |
| `AirQualityProvider` | Outdoor AQI | WAQI |
| `ComfortModel` | Calculate comfort | PMV/PPD (pythermalcomfort) |
| `ControlStrategy` | Decide actions | PriorityCascade, Deadband |

## Control Laws

### 1. Deadband (Hysteresis)
Prevents short-cycling. Configurable per parameter.
- Temperature: +/-1.5 degC (default)
- Humidity: +/-5% RH (default)
- CO2: +/-100 ppm (default)

### 2. Setpoint Scheduling
Time-of-day + season targets based on ASHRAE 55. Fully configurable via ScheduleEntry.

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

## MCP Servers

| Server | Purpose | When to Use |
|--------|---------|-------------|
| Context7 | Library docs | pythermalcomfort, pydantic, HA integration APIs |
| Web Search / Reader | Research | AQI standards, ESPHome device configs, SLWF-01pro guides |

## Documentation Rules

### Soft Enforcement
- Always update docs when changing code
- README must reflect current project state
- API contracts in code (docstrings + type hints)

### Hard Enforcement
- Pre-commit: ruff lint/format, mypy, pytest fast suite
- GitHub Actions CI: full test suite, coverage, YAML validation
- GitHub Actions weekly: verify file structure matches this CLAUDE.md

## Reference Documents

| File | Standard | Use For |
|------|----------|---------|
| `docs/reference/ashrae-55-2020.html` | ASHRAE 55-2020 | Thermal comfort criteria |
| `docs/reference/iso-7730-2005.html` | ISO 7730:2005 | PMV calculation method |
| `docs/reference/en-16798-1-2019.html` | EN 16798-1:2019 | European indoor criteria |
| `docs/reference/who-air-quality-2021.html` | WHO AQG 2021 | PM2.5, CO2, TVOC limits |

## Automation Principles

1. **Local-first:** All control runs locally. Cloud services are read-only (weather data).
2. **Idempotent:** Re-evaluating does not change state if targets are met.
3. **Graceful degradation:** If sensors go offline, fall back to available data.
4. **No oscillation:** Deadbands + minimum runtime prevent rapid cycling.
5. **Transparent:** Every decision is traceable to a specific sensor + threshold.
