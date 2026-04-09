# Galaxy S8 Home Assistant Hub Setup Guide

Complete step-by-step guide for turning a Samsung Galaxy S8 into a Home
Assistant hub using Termux and Udocker.

---

## Prerequisites

- Samsung Galaxy S8 (SM-G950F or SM-G950U) with:
  - Android 9 (last official update) or LineageOS
  - At least 32 GB storage
  - Functional WiFi
  - Charged battery (will be kept at 40-80% via automation)
- MicroSD card (optional, for data persistence)
- Shelly Plug S smart plug (for battery cycling automation)
- Access to home WiFi network

---

## Step 1: Factory Reset (Recommended)

A clean slate avoids conflicts with old apps and settings.

1. Back up any data you want to keep
2. Settings > General Management > Reset > Factory data reset
3. After reset, skip all Google account setup (not needed)
4. Disable all Samsung bloatware that can't be uninstalled
5. Enable Developer Options (tap Build Number 7 times)
6. In Developer Options: enable USB debugging (optional, for ADB)

---

## Step 2: Install Termux from F-Droid

**CRITICAL:** Do NOT install Termux from Google Play Store. The Play Store
version is severely outdated and broken.

1. Open browser, go to https://f-droid.org
2. Download and install the F-Droid APK
3. Open F-Droid, search for "Termux"
4. Install Termux
5. Open Termux, run initial setup:
   ```bash
   pkg update && pkg upgrade -y
   ```

---

## Step 3: Install Termux-Udocker

Udocker is a lightweight container runtime that works without root on Android.

```bash
# Install dependencies
pkg install wget curl git -y

# Install proot for chroot emulation
pkg install proot -y

# Install udocker
pip install udocker

# Verify installation
udocker --version
```

If `pip` is not available:
```bash
pkg install python -y
pip install udocker
```

---

## Step 4: Pull and Run Home Assistant Container

```bash
# Pull the HA container image
udocker pull homeassistant/home-assistant:stable

# Create a container
udocker create --name=homeassistant homeassistant/home-assistant:stable

# Set up the container (this takes a few minutes)
udocker setup homeassistant

# Run the container
udocker run \
  --publish=8123:8123 \
  --volume=/data/homeassistant:/config \
  --env=TZ=Europe/Skopje \
  homeassistant
```

### Data Persistence

The `--volume` flag maps `/data/homeassistant` on the Termux filesystem to
`/config` inside the container. This survives container restarts.

To find the actual path:
```bash
# Termux home directory
echo $HOME
# Usually: /data/data/com.termux/files/home

# Create HA config directory
mkdir -p $HOME/homeassistant
```

### Access Home Assistant

1. On the S8: open browser, go to `http://localhost:8123`
2. On any device on the same WiFi: go to `http://<S8-IP>:8123`
3. Find S8 IP: `ifconfig wlan0` or Settings > WiFi > Advanced

---

## Step 5: Critical Android Settings

These settings prevent Android from killing Termux and the HA container.

### Battery Optimization (MOST IMPORTANT)

1. Settings > Apps > Termux > Battery > **Unrestricted**
2. Settings > Apps > F-Droid > Battery > **Unrestricted**
3. Repeat for: Termux:Boot, HA Companion App

### Wake Lock (Prevent Sleep)

In Termux:
```bash
# Acquire wake lock (keeps CPU alive)
termux-wake-lock

# Verify it's held
termux-wake-lock  # running it again shows status
```

To make wake lock permanent, add to `~/.bashrc`:
```bash
echo 'termux-wake-lock' >> ~/.bashrc
```

### WiFi Settings

1. Settings > Connections > WiFi > Advanced
2. **Turn off** "WiFi Power Save Mode" (if available)
3. **Turn off** "Turn on WiFi automatically"
4. Set WiFi to **Always on** during sleep: Settings > Connections > WiFi >
   Advanced > Keep WiFi on during sleep > **Always**

### Display Settings

1. Set screen timeout to 30 seconds (saves battery, Termux runs without screen)
2. Brightness to minimum
3. Turn off "Always On Display"

### Do Not Disturb

1. Enable DND mode (the S8 is now a headless server, no notifications needed)
2. Settings > Sounds and vibration > Do not disturb > **Turn on now**

---

## Step 6: Install BLE Proxy

The S8's built-in Bluetooth can act as a BLE proxy for Home Assistant,
enabling communication with BLE devices like the XiaoMei robot vacuum.

### Option A: ESPHome BLE Proxy (via Termux)

If running ESPHome inside the HA container:
1. Flash an ESP32 with ESPHome BLE proxy firmware
2. Or configure HA's built-in Bluetooth integration

### Option B: HA Bluetooth Integration (Native)

Home Assistant 2024+ has native BLE support:
1. Settings > Devices & Services > Bluetooth
2. The S8's Bluetooth adapter is automatically available to the container
3. BLE devices in range are discovered automatically

### Option C: Dedicated BLE Proxy App

If the container can't access Bluetooth directly:
1. Install "Bluetooth BLE Proxy" from F-Droid
2. Configure it to forward BLE data to HA via MQTT
3. This requires an MQTT broker (Mosquitto add-on or external)

### Testing BLE Range

After setup, test if the S8's Bluetooth can reach the XiaoMei vacuum:
1. Place the S8 in its permanent location
2. Try to discover the XiaoMei via HA Bluetooth integration
3. If discovery fails, you may need an ESP32 BLE proxy (see shopping list)

---

## Step 7: Install HA Companion App

The Companion App provides sensor data (battery level, WiFi status, etc.)
to Home Assistant and enables notifications.

1. Download "Home Assistant Companion" from F-Droid (preferred) or Play Store
2. Open the app, enter `http://localhost:8123` as the HA URL
3. Log in with your HA account
4. Enable all sensors in app settings:
   - Battery level
   - Battery charging state
   - WiFi connection status
   - Device location (optional)
   - Bluetooth state

### Key Sensors for Automation

- `sensor.s8_battery_level` — for battery cycling automation
- `binary_sensor.s8_charger` — detects when Shelly plug is on/off
- `sensor.s8_wifi_signal` — connection quality monitoring

---

## Step 8: Battery Cycling Setup

The Galaxy S8 battery will degrade quickly if kept at 100% charge 24/7.
The battery cycling automation keeps it between 40-80% using a Shelly Plug S.

### Hardware Setup

1. Plug S8 charger into Shelly Plug S
2. Plug Shelly Plug S into wall outlet
3. Configure Shelly Plug S in HA (auto-discovered on WiFi)

### HA Automation: Battery Cycling

```yaml
automation:
  - id: s8_battery_charge_cycle
    alias: "S8 Battery Charge Cycle"
    description: "Keep S8 battery between 40-80%"
    triggers:
      - trigger: numeric_state
        entity_id: sensor.s8_battery_level
        below: 40
        id: charge_start
      - trigger: numeric_state
        entity_id: sensor.s8_battery_level
        above: 80
        id: charge_stop
    actions:
      - choose:
          - conditions:
              - condition: trigger
                id: charge_start
            sequence:
              - action: switch.turn_on
                target:
                  entity_id: switch.shelly_plug_s_s8_charger
              - service: persistent_notification.create
                data:
                  message: "S8 battery at {{ states('sensor.s8_battery_level') }}% — charging started"
                  title: "S8 Battery"
          - conditions:
              - condition: trigger
                id: charge_stop
            sequence:
              - action: switch.turn_off
                target:
                  entity_id: switch.shelly_plug_s_s8_charger
              - service: persistent_notification.create
                data:
                  message: "S8 battery at {{ states('sensor.s8_battery_level') }}% — charging stopped"
                  title: "S8 Battery"
```

### Add Hysteresis (Prevent Rapid Cycling)

```yaml
  - id: s8_battery_charge_hysteresis
    alias: "S8 Battery Charge Safety"
    description: "Minimum 30 minutes between charge state changes"
    triggers:
      - trigger: state
        entity_id: switch.shelly_plug_s_s8_charger
    conditions:
      - condition: template
        value_template: >
          {{ (as_timestamp(now()) - as_timestamp(state_attr('automation.s8_battery_charge_hysteresis', 'last_triggered') | default(0))) < 1800 }}
    actions:
      - action: switch.turn_off
        target:
          entity_id: switch.shelly_plug_s_s8_charger
```

---

## Step 9: Termux:Boot for Auto-Start

Termux:Boot ensures HA starts automatically when the S8 boots.

1. Install **Termux:Boot** from F-Droid
2. Launch Termux:Boot once (grants boot permission)
3. Create the boot script:

```bash
mkdir -p ~/.termux/boot/
cat > ~/.termux/boot/homeassistant-start.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock

# Wait for WiFi to connect
sleep 30

# Start HA container
udocker run \
  --publish=8123:8123 \
  --volume=$HOME/homeassistant:/config \
  --env=TZ=Europe/Skopje \
  --detach \
  homeassistant
EOF
chmod +x ~/.termux/boot/homeassistant-start.sh
```

### Test Auto-Start

1. Reboot the S8
2. Wait 1-2 minutes
3. Check if HA is accessible at `http://<S8-IP>:8123`

---

## Step 10: Troubleshooting

### Container Won't Start

```bash
# Check if udocker is working
udocker ps -a

# View container logs
udocker inspect homeassistant

# Remove and recreate
udocker rm homeassistant
udocker create --name=homeassistant homeassistant/home-assistant:stable
udocker setup homeassistant
```

### Termux Keeps Getting Killed

1. Verify battery optimization is disabled (Step 5)
2. Verify wake lock is active: run `termux-wake-lock` in Termux
3. On Samsung specifically: Settings > Device Care > Battery > App Power
   Management > Disable "Put unused apps to sleep"
4. Add Termux to "Apps that won't be put to sleep" list

### WiFi Disconnects

1. Settings > Connections > WiFi > Advanced > Keep WiFi on during sleep > Always
2. Disable "WiFi Power Save" in Developer Options (if available)
3. Set static IP on the router for the S8's MAC address

### Bluetooth Not Available in Container

Udocker containers may not have access to the host Bluetooth adapter. Options:
1. Use HA's integrated Bluetooth (newer versions may support it)
2. Run an external BLE proxy app (see Step 6)
3. Use a separate ESP32 as BLE proxy (most reliable)

### HA is Slow or Unresponsive

- S8 has 4 GB RAM — HA container uses ~500 MB
- If sluggish, reduce number of active integrations
- Disable unused HA components (media player, etc.)
- Consider moving to Raspberry Pi 5 if performance is insufficient

### Can't Access HA from Other Devices

1. Check S8 IP: `ifconfig wlan0` in Termux
2. Verify both devices on same WiFi network
3. Check if Android Firewall is blocking: Settings > Connections > More >
   Private DNS > Off (or set to a valid DNS)
4. Try accessing by IP instead of hostname

---

## Escape Hatch: If S8 Proves Unreliable

If the S8 approach has persistent issues (crashes, Bluetooth problems,
WiFi drops), migrate to a Raspberry Pi 5:

| Option | Cost | Pros | Cons |
|--------|------|------|------|
| **Raspberry Pi 5 (4 GB)** | ~$60 + $15 PSU + $10 case = ~$85 | Reliable, native Linux, GPIO, BT | Need to buy and wait for delivery |
| **Raspberry Pi 5 (8 GB)** | ~$80 + $15 PSU + $10 case = ~$105 | Future-proof | Overkill for HA only |
| **Used mini PC** | ~$50-80 | x86, powerful, SSD | Larger, no GPIO, higher power |

Migration path: export HA backup from S8, install HA OS on Pi, restore backup.
Zero configuration loss.

---

## Summary Checklist

- [ ] Factory reset S8
- [ ] Install F-Droid
- [ ] Install Termux from F-Droid
- [ ] Install Termux:Boot from F-Droid
- [ ] Install udocker in Termux
- [ ] Pull and run HA container
- [ ] Configure Android settings (battery, wake lock, WiFi)
- [ ] Access HA web interface
- [ ] Install HA Companion App
- [ ] Set up Shelly Plug S for battery cycling
- [ ] Create battery cycling automation
- [ ] Create boot script for auto-start
- [ ] Test BLE proxy functionality
- [ ] Verify auto-start after reboot
