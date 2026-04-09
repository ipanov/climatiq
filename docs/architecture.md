# System Architecture — ClimatIQ

## Physical Architecture

```
                         CLOUD SERVICES
                    (read-only, no local control)
                    ┌─────────────────────────┐
                    │                         │
                    │  ┌───────────────────┐  │
                    │  │   Open-Meteo      │  │
                    │  │  (weather/forecast)│  │
                    │  └───────────────────┘  │
                    │                         │
                    │  ┌───────────────────┐  │
                    │  │   WAQI            │  │
                    │  │  (outdoor AQI)    │  │
                    │  └───────────────────┘  │
                    │                         │
                    └─────────┬───────────────┘
                              │ REST (polling)
                              │
    ══════════════════════════╪═══════════════════════════════
                    HOME NETWORK (WiFi + BLE)
    ══════════════════════════╪═══════════════════════════════
                              │
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 │   Samsung Galaxy S8     │
                 │   ┌───────────────────┐ │
                 │   │  Termux           │ │
                 │   │  ┌──────────────┐ │ │
                 │   │  │   Udocker    │ │ │
                 │   │  │  ┌─────────┐ │ │ │
                 │   │  │  │  HA     │ │ │ │
                 │   │  │  │  Core   │ │ │ │
                 │   │  │  └────┬────┘ │ │ │
                 │   │  └───────┼──────┘ │ │
                 │   └─────────┼────────┘ │
                 │             │          │
                 └─────────────┼──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
     ┌────────┴───┐    ┌──────┴──────┐   ┌─────┴──────┐
     │   WiFi     │    │    BLE      │   │  HA Core   │
     │  Network   │    │  (built-in) │   │  Engine    │
     └─────┬──────┘    └──────┬──────┘   └─────┬──────┘
           │                  │                │
     ┌─────┴──────────┐ ┌────┴──────────┐     │
     │                │ │               │     │
  ┌──┴──┐  ┌─────┐  ┌┴─┐ ┌──┐  ┌─────┐ │     │
  │AC x4│  │Purf │  │Sm│ │Xm│  │Vac  │ │     │
  │SLWF │  │3H   │  │i │ │BL│  │X20+ │ │     │
  └──┬──┘  └──┬──┘  └┬─┘ └──┘  └──┬──┘ │     │
     │        │      │              │    │     │
     │  ┌─────┴──┐   │         ┌────┴──┐ │     │
     │  │Blueair │   │         │ Shelly│ │     │
     │  │411     │   │         │ Plug  │ │     │
     │  └────────┘   │         └───────┘ │     │
     │               │                   │     │
     └───────────────┴───────────────────┴─────┘
                      SENSOR DATA
                    & CONTROL FLOW
```

## Component Legend

```
  WiFi Devices                        BLE Devices
  ────────────                        ──────────
  AC x4     Vivax via SLWF-01pro      XiaoMei   WP6003 Air Quality Box
  Purf 3H   Xiaomi Air Purifier 3H    Xm BLE    Xiaomi Temp/Humidity
  Smartmi   Evaporative Humidifier 2
  Vac X20+  Robot Vacuum              Cloud Services
  Shelly    Smart plug for Blueair    ──────────────
  Blueair   Blue Pure 411 (via plug)  Open-Meteo  Weather + forecast
                                       WAQI        Outdoor AQI + PM2.5
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        RAW SENSOR INPUTS                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Living Room                    Children's Room                     │
│  ┌──────────────────┐          ┌──────────────────┐                │
│  │ Purifier 3H      │          │ Xiaomi BLE       │                │
│  │  -> temperature   │          │  -> temperature   │                │
│  │  -> humidity      │          │  -> humidity      │                │
│  │  -> PM2.5         │          └────────┬──────────┘                │
│  └────────┬─────────┘                    │                          │
│           │                              │                          │
│  ┌────────┴──────────┐                   │                          │
│  │ XiaoMei WP6003    │                   │                          │
│  │  -> CO2           │                   │                          │
│  │  -> TVOC          │                   │                          │
│  │  -> HCHO          │                   │                          │
│  └────────┬──────────┘                   │                          │
│           │                              │                          │
│  Room 3,4 │                              │                          │
│  ┌────────┴──────────┐                   │                          │
│  │ AC sensors only    │                  │                          │
│  │  -> temperature    │                  │                          │
│  └────────┬──────────┘                   │                          │
│           │                              │                          │
│  Outdoor  │                              │                          │
│  ┌────────┴──────────┐                   │                          │
│  │ Open-Meteo        │                   │                          │
│  │  -> temperature   │                   │                          │
│  │  -> humidity      │                   │                          │
│  │  -> solar_rad     │                   │                          │
│  │  -> forecast_24h  │                   │                          │
│  └────────┬──────────┘                   │                          │
│           │                              │                          │
│  ┌────────┴──────────┐                   │                          │
│  │ WAQI              │                   │                          │
│  │  -> AQI           │                   │                          │
│  │  -> PM2.5         │                   │                          │
│  └────────┬──────────┘                   │                          │
│           │                              │                          │
├───────────┴──────────────────────────────┴──────────────────────────┤
│                   TEMPLATE SENSOR LAYER                            │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  For each room with sufficient data:                         │  │
│  │                                                               │  │
│  │    dew_point = f(temperature, humidity)                       │  │
│  │    pmv       = f(t_air, t_radiant, v_air, RH, clothing, met) │  │
│  │    ppd       = f(pmv)                                         │  │
│  │    comfort   = weighted(pmv, humidity, co2, pm25)             │  │
│  │                                                               │  │
│  │  Entity outputs:                                              │  │
│  │    sensor.room{n}_dew_point                                   │  │
│  │    sensor.room{n}_pmv                                         │  │
│  │    sensor.room{n}_ppd                                         │  │
│  │    sensor.room{n}_comfort_score                               │  │
│  └──────────────────────────┬────────────────────────────────────┘  │
│                              │                                      │
├──────────────────────────────┴──────────────────────────────────────┤
│                    CLIMATE INTELLIGENCE ENGINE                      │
│                                                                     │
│  Priority cascade: Safety > Health > Comfort > Energy               │
│                                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐     │
│  │  Safety     │  │  Health      │  │  Comfort               │     │
│  │  Monitor    │  │  Guard       │  │  Optimizer             │     │
│  │             │  │              │  │                        │     │
│  │ frost watch │  │ CO2 < 1000   │  │ PMV in [-0.5, +0.5]   │     │
│  │ overheat    │  │ PM2.5 < 12   │  │ dew point < 15         │     │
│  │ CO2 > 2000  │  │ TVOC < 0.3   │  │ setpoint scheduling    │     │
│  └──────┬──────┘  │ HCHO < 0.03  │  │ sun pre-cool/heat      │     │
│         │         └──────┬───────┘  │ forecast adjustment    │     │
│         │                │          └───────────┬────────────┘     │
│         │                │                      │                   │
│         │    ┌───────────┴──────────────────────┘                   │
│         │    │                                                      │
│  ┌──────┴────┴──────────────────────────────────────────────────┐  │
│  │                    CONTROL OUTPUTS                            │  │
│  │                                                              │  │
│  │  climate.room1_ac ── temperature + mode + fan speed          │  │
│  │  climate.room2_ac ── temperature + mode + fan speed          │  │
│  │  climate.room3_ac ── temperature + mode + fan speed          │  │
│  │  climate.room4_ac ── temperature + mode + fan speed          │  │
│  │  purifier.xiaomi_3h ── mode (auto/silent/favorite)          │  │
│  │  switch.shelly_blueair ── on/off                             │  │
│  │  humidifier.smartmi ── target humidity + mode                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Network Topology

```
                    ┌──────────────┐
                    │   Internet   │
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
                    │  Home Router │
                    │  2.4 GHz     │
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────┴──────┐  ┌─────┴──────┐   ┌─────┴──────┐
    │ Galaxy S8  │  │ WiFi IoT   │   │ ESP32      │
    │ (HA Core)  │  │ Devices    │   │ (optional) │
    │            │  │            │   │            │
    │ BLE proxy  │  │ - AC x4   │   │ BLE bridge │
    │            │  │ - Purf 3H │   │ for XiaoMei│
    └─────┬──────┘  │ - Smartmi │   └─────┬──────┘
          │         │ - Vac X20+│         │
          │         │ - Shelly  │         │
          │         └───────────┘         │
          │                               │
    ┌─────┴───────────────────────────────┴─────┐
    │              BLE Network                   │
    │                                            │
    │  - XiaoMei WP6003 (living room)            │
    │  - Xiaomi BLE sensor (children's room)     │
    └────────────────────────────────────────────┘
```

## Automation Trigger Flow

```
    Sensor state change
          │
          v
    ┌─────────────┐     No     ┌──────────────┐
    │ Threshold   │──────────->│ No action    │
    │ exceeded?   │            │ (within      │
    └──────┬──────┘            │  deadband)   │
           │ Yes               └──────────────┘
           v
    ┌─────────────┐     No     ┌──────────────┐
    │ Safety      │──────────->│ Next check   │
    │ condition?  │            │              │
    └──────┬──────┘            └──────────────┘
           │ Yes                     │
           v                         v
    ┌─────────────┐           ┌──────────────┐
    │ IMMEDIATE   │     No    │ Health       │
    │ action      │───────────│ condition?   │
    │ (no delay)  │           └──────┬───────┘
    └─────────────┘                  │ Yes
                               ┌─────┴───────┐
                               │ HEALTH      │
                               │ action      │
                               │ (30s delay) │
                               └──────┬──────┘
                                      │ No
                                ┌─────┴───────┐
                           No   │ Comfort     │
                        ────────── condition? │
                               │ └──────┬──────┘
                               │ Yes    │ No
                               v        v
                        ┌────────────┐ ┌──────────────┐
                        │ COMFORT    │ │ Energy       │
                        │ action     │ │ optimization │
                        │ (5m delay) │ │ (schedule)   │
                        └────────────┘ └──────────────┘
```
