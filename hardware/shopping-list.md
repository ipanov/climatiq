# ClimatIQ Hardware Shopping List

## Overview

Smart home climate control hardware for a Home Assistant setup running on a
Galaxy S8 hub. All prices are estimates as of April 2026.

---

## Priority 1 — Vivax AC Integration (Order First)

| # | Item | Est. Price | Source | Notes |
|---|------|-----------|--------|-------|
| 4 | **SLWF-01pro** ESPHome Wi-Fi module | $10-12 each ($40-48 total) | AliExpress | For 4 Vivax AC units |

- **Total for AC modules:** ~$40-48
- **Shipping to Macedonia:** 15-30 days (AliExpress standard), 7-15 days (AliExpress Premium Shipping if available, +$2-3 per item)
- **Search terms:** "SLWF-01pro", "Midea USB ESPHome", "SLWF01pro WiFi module"
- **Verified sellers:** Look for stores with 95%+ rating and 500+ orders. Common store names include "Smart Life Store" and "Midea WiFi Module Store"

### Why SLWF-01pro

- Plugs directly into the USB port on the AC indoor unit PCB
- ESPHome firmware pre-flashed — no flashing required
- Home Assistant auto-discovery via ESPHome integration
- Works with Midea-platform ACs (Vivax uses Midea internals)
- No soldering, no cutting wires, fully reversible

---

## Priority 2 — Smart Plugs (Order with AC Modules)

| # | Item | Est. Price | Source | Notes |
|---|------|-----------|--------|-------|
| 1 | **Shelly Plug S** | ~$15 | Amazon DE / domadoo.fr / Shelly Official | For S8 charger cycling (battery protection automation) |
| 1 | **Shelly Plug S** | ~$15 | Amazon DE / domadoo.fr / Shelly Official | For Blueair 411 smart control (on/off + power monitoring) |

- **Total for smart plugs:** ~$30
- **Shipping to Macedonia:** 5-10 days (EU vendors), 3-5 days (Amazon DE with forwarding)
- **Why Shelly Plug S:** Native ESPHome/Tasmota support, power monitoring, compact size, reliable WiFi
- **Alternative:** Shelly Plug Plus S (newer, Bluetooth) — same price range, also works

---

## Priority 3 — BLE Proxy (Conditional Purchase)

| # | Item | Est. Price | Source | Notes |
|---|------|-----------|--------|-------|
| 1 | **ESP32 dev board** | ~$5 | AliExpress / locally | Only if S8 BLE proxy doesn't reach XiaoMei robot |

- **Total (conditional):** ~$5
- **When to buy:** After testing S8 BLE range. If the S8 can maintain BLE connection to XiaoMei from its charging spot, skip this.
- **Board options:** ESP32-WROOM-32 dev kit, ESP32-S3, or M5Stack Atom Lite
- **Firmware:** ESPHome BLE proxy (trivial to flash)

---

## Budget Summary

| Category | Low Estimate | High Estimate |
|----------|-------------|---------------|
| SLWF-01pro x4 | $40 | $48 |
| Shelly Plug S x2 | $30 | $30 |
| ESP32 (conditional) | $0 | $5 |
| **Total** | **$70** | **$83** |

### Shipping Estimates to Macedonia

| Source | Typical Time | Notes |
|--------|-------------|-------|
| AliExpress (standard) | 15-30 days | Often arrives in 20 days |
| AliExpress (premium) | 7-15 days | Slightly more expensive |
| Amazon DE | 5-10 days | With mail forwarding service |
| domadoo.fr | 7-14 days | EU-based smart home shop |
| Shelly Official | 5-10 days | Direct from EU warehouse |

### Recommended Order of Purchase

1. **SLWF-01pro modules** (AliExpress) — order immediately, longest shipping time
2. **Shelly Plug S** (EU vendor) — order at the same time, arrives faster
3. **ESP32 board** — only after testing S8 BLE range, skip if not needed

### Total Time to Full Deployment

- **Day 0:** Order everything
- **Day 5-10:** Shelly plugs arrive (EU shipping)
- **Day 7-10:** Begin S8 HA setup with Shelly plugs
- **Day 15-30:** SLWF-01pro modules arrive
- **Day 16-31:** Full system operational
