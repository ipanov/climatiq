# Vivax AC + SLWF-01pro Compatibility Research

## Key Finding: Vivax ACs Use Midea Internals

Vivax air conditioners are OEM rebrands of Midea (美的) units. This means they
share the same internal electronics, including the diagnostic USB port on the
indoor unit PCB that the SLWF-01pro module plugs into.

---

## SLWF-01pro Overview

The **SLWF-01pro** (also sold as "Midea USB WiFi Module") is a purpose-built
ESPHome module that connects to Midea-platform air conditioners via the USB
header on the indoor unit circuit board.

### Compatible Brands

All Midea OEM brands are compatible:

- **Vivax** (confirmed)
- **Midea** (native)
- **Comfee**
- **Electrolux** (Midea OEM models)
- **Qlima**
- **Inventor**
- **Kaisai**
- **Mitsubishi Electric** (some models — verify)
- **Hyundai** (Midea OEM models)
- **Beko** (Midea OEM models)
- **TCL**

### Key Specs

| Parameter | Value |
|-----------|-------|
| MCU | ESP8266 (ESP-12F) |
| Firmware | ESPHome (pre-flashed) |
| Connection | USB-A header on AC PCB |
| Power | Drawn from AC PCB USB port |
| WiFi | 2.4 GHz 802.11 b/g/n |
| Protocol | Midea electrical protocol via UART |
| Control | On/Off, temperature, mode, fan speed, swing |
| Sensors | Ambient temperature (from AC), compressor status |

---

## Setup Procedure

### Step 1: Open Indoor Unit Cover

1. Power off the AC at the breaker (safety first)
2. Remove the front cover/plastic fascia of the indoor unit
3. Locate the PCB (usually behind the display panel)
4. Look for a USB-A header on the PCB

### Step 2: Identify the USB Port

The USB port on the PCB looks like a standard USB-A female connector. It may
be labeled "USB" or "WIFI" or have no label at all. On some boards it is a
4-pin header that requires the included adapter cable.

**Important:** This USB port is NOT for firmware updates on the AC. It is a
serial communication port that the original WiFi module (if any) would use.
The SLWF-01pro replaces or supplements the factory WiFi module.

### Step 3: Install SLWF-01pro

1. Insert the SLWF-01pro into the USB port
2. Power the AC back on
3. The module creates a WiFi hotspot named `SLWF-01pro_xxxxx`
4. Connect to the hotspot from your phone
5. A captive portal opens — enter your home WiFi credentials
6. The module connects to your WiFi and appears in Home Assistant

### Step 4: Home Assistant Integration

1. In HA, go to Settings > Devices & Services
2. ESPHome integration auto-discovers the module
3. Click "Configure" on the discovered device
4. The AC appears as a climate entity with full control:
   - On/Off
   - Mode (Cool, Heat, Auto, Dry, Fan)
   - Target temperature
   - Fan speed
   - Swing control
5. Sensor entities are also created:
   - Ambient temperature
   - Compressor power (derived)

---

## Vivax Design Air Plus Specifics

For the Vivax Design Air Plus model (and similar Vivax inverter split units):

- The indoor unit PCB is typically located behind the front panel/display
- The USB header is usually a 4-pin JST-style connector, not a full USB-A port
- The SLWF-01pro kit should include an adapter cable for this connector type
- If no USB/UART header is visible, check under adhesive covers or behind
  cable bundles — it is sometimes partially hidden

### Verification Checklist

Before ordering SLWF-01pro modules, verify on each AC unit:

- [ ] Indoor unit front cover can be removed without special tools
- [ ] PCB is accessible (usually right behind the cover)
- [ ] USB or 4-pin header is present on the PCB
- [ ] Header pinout matches SLWF-01pro (5V, GND, TX, RX)
- [ ] No existing WiFi module occupies the header (if one does, replace it)

### If No USB Header Found

Some newer Midea boards use an I2C or SPI header instead of USB. In this case:
- Check if the existing WiFi module (if any) can be unplugged and replaced
- Look for an "OPPO" or "Midea Smart" branded WiFi card — this is the factory
  module that the SLWF-01pro replaces
- Contact the SLWF-01pro seller with a photo of your PCB — they can identify
  the correct connection point

---

## ESPHome Configuration

The SLWF-01pro comes pre-flashed, but if you need to reflash or customize:

```yaml
# ESPHome config for SLWF-01pro (Midea AC)
substitutions:
  name: vivax-ac-bedroom
  friendly_name: "Vivax AC Bedroom"

esphome:
  name: ${name}
  friendly_name: ${friendly_name}

esp8266:
  board: esp12e

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  ap:
    ssid: "${name} Fallback"
    password: !secret fallback_password

captive_portal:

logger:

api:
  encryption:
    key: !secret api_key

ota:
  - platform: esphome
    password: !secret ota_password

uart:
  tx_pin: GPIO1
  rx_pin: GPIO3
  baud_rate: 9600

climate:
  - platform: midea
    name: "${friendly_name}"
    visual:
      min_temperature: 16
      max_temperature: 30
      temperature_step: 1.0
    supports:
      mode: [COOL, HEAT, AUTO, DRY, FAN_ONLY]
      fan_mode: [AUTO, LOW, MEDIUM, HIGH]
      swing_mode: [OFF, VERTICAL]
    outdoor_temperature:
      name: "${friendly_name} Outdoor Temperature"
    power_usage:
      name: "${friendly_name} Power Usage"
```

---

## References

- SLWF-01pro product page and documentation: search AliExpress for "SLWF-01pro"
- ESPHome Midea climate component: https://esphome.io/components/climate/midea.html
- Midea AC protocol reverse engineering: https://github.com/mac-zhou/midea-msmart
- Vivax AC Midea OEM confirmation: multiple community reports on HA forums

## Open Questions

1. Does the specific Vivax Design Air Plus model have a USB header or 4-pin JST?
2. Are all 4 Vivax units the same model? (Different models may have different PCBs)
3. Is there an existing WiFi module in any of the units that needs replacing?
4. Maximum cable length from PCB to mounting point? (Module should be mounted
   inside the indoor unit housing for best WiFi reception)
