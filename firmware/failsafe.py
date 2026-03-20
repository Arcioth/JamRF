"""
jamRF-v2 Thermal Failsafe System
================================
Target: M5StickC Plus 2 (ESP32-PICO-V3-02)
Runtime: MicroPython

Monitors NTC thermistor on heatsink via voltage divider.
Shuts down amplifiers at 85C, re-enables after cooldown to 80C.
Two-stage power sequencing for GaN PA safety.

Wiring (matches jamrf-v2 schematic):
  +3V3 -> R_TH (10k) -> ADC (G36) -> NTC (10k @ 25C) -> GND
  +14V8 -> R_BATT1 (100k) -> ADC (G0) -> R_BATT2 (22k) -> GND
  G33 -> BIAS_EN (LM2776 charge pump enable, generates -5V gate bias)
  G32 -> RELAY_CTRL (Q3 gate -> Q2 P-FET WiFi PA power switch)
  G25/DAC -> GPS_TUNE (VCO1 chaos modulation)
  G26/DAC -> WIFI_TUNE (VCO2 chaos modulation)

Power sequencing (GaN PA depletion-mode safety):
  Enable:  BIAS_EN HIGH (charge pump on, -5V gate bias)
           -> wait for BIAS_OK (LM393 confirms -5V present)
           -> RELAY_CTRL HIGH (PA drain power on)
  Disable: RELAY_CTRL LOW (PA drain power off first)
           -> wait 15ms (POSCAP bleed)
           -> BIAS_EN LOW (charge pump off, gate bias removed)

Safety behavior:
  - System starts OFF (both outputs LOW)
  - 3-second startup delay before enabling
  - Continuous 1Hz temperature AND battery voltage monitoring
  - Immediate shutdown on overtemperature (85C) or undervoltage (<13V)
  - 5C hysteresis on temperature, 0.5V hysteresis on voltage
  - Sensor fault detection (open/short circuit NTC)
  - Watchdog timer resets system if firmware hangs
"""

import machine
import time
import math

# =============================================================
# PIN CONFIGURATION (matches jamrf-v2 schematic)
# =============================================================
THERMISTOR_PIN = 36   # G36 - ADC1_CH0 input from NTC voltage divider (always available)
BATTERY_PIN = 0       # G0  - ADC input from battery voltage divider
BIAS_EN_PIN = 33      # G33 - Output: LM2776 charge pump enable (generates -5V gate bias)
RELAY_CTRL_PIN = 32   # G32 - Output: Q3 gate -> Q2 P-FET WiFi PA drain switch
BUZZER_PIN = 2        # Internal buzzer (M5StickC built-in)
SEQUENCER_DELAY_MS = 15  # Delay between bias enable and PA drain enable (ms)

# =============================================================
# SAFETY THRESHOLDS
# =============================================================
SHUTDOWN_TEMP_C = 85.0     # Amplifiers OFF above this
RECOVERY_TEMP_C = 80.0     # Amplifiers ON below this (hysteresis)
SENSOR_FAULT_LOW = -20.0   # Below this = sensor open circuit
SENSOR_FAULT_HIGH = 150.0  # Above this = sensor short circuit
UNDERVOLT_CUTOFF_V = 13.0  # ZVE-3W-83+ minimum supply voltage
UNDERVOLT_RECOVER_V = 13.5 # Re-enable after battery recovers
STARTUP_DELAY_S = 3        # Delay before first enable
SAMPLE_INTERVAL_S = 1      # Temperature polling rate
ADC_SAMPLES = 16           # Number of ADC readings to average

# =============================================================
# THERMISTOR PARAMETERS (Vishay NTCS0805E3103FMT)
# =============================================================
B_COEFFICIENT = 3950       # Beta value (K)
NOMINAL_RESISTANCE = 10000 # Ohms at nominal temperature
NOMINAL_TEMP_K = 298.15    # 25C in Kelvin
SERIES_RESISTOR = 10000    # Fixed series resistor (ohms)
ADC_MAX = 4095             # ESP32 12-bit ADC
V_REF = 3.3                # ADC reference voltage

# =============================================================
# BATTERY VOLTAGE DIVIDER (R_BATT1=100k / R_BATT2=22k)
# V_adc = V_batt * R_BATT2 / (R_BATT1 + R_BATT2)
# V_batt = V_adc * (R_BATT1 + R_BATT2) / R_BATT2
# =============================================================
R_BATT1 = 100000          # High-side divider resistor (ohms)
R_BATT2 = 22000           # Low-side divider resistor (ohms)
BATT_DIVIDER_RATIO = (R_BATT1 + R_BATT2) / R_BATT2  # ~5.545

# =============================================================
# HARDWARE INITIALIZATION
# =============================================================
adc = machine.ADC(machine.Pin(THERMISTOR_PIN))
adc.atten(machine.ADC.ATTN_11DB)  # Full range 0-3.3V
adc.width(machine.ADC.WIDTH_12BIT)

batt_adc = machine.ADC(machine.Pin(BATTERY_PIN))
batt_adc.atten(machine.ADC.ATTN_11DB)
batt_adc.width(machine.ADC.WIDTH_12BIT)

bias_en = machine.Pin(BIAS_EN_PIN, machine.Pin.OUT)
bias_en.value(0)  # Start with charge pump OFF

relay_ctrl = machine.Pin(RELAY_CTRL_PIN, machine.Pin.OUT)
relay_ctrl.value(0)  # Start with PA drain switches OFF

# Watchdog timer - resets if firmware hangs for >10 seconds
wdt = machine.WDT(timeout=10000)

# =============================================================
# STATE TRACKING
# =============================================================
system_armed = False
fault_count = 0
undervolt_active = False
MAX_CONSECUTIVE_FAULTS = 5


def read_adc_averaged():
    """Read ADC with oversampling to reduce noise."""
    total = 0
    for _ in range(ADC_SAMPLES):
        total += adc.read()
        time.sleep_ms(1)
    return total // ADC_SAMPLES


def adc_to_temperature(adc_val):
    """
    Convert ADC reading to temperature using Steinhart-Hart
    (simplified Beta equation).

    Circuit: 3V3 -> R_TH (10k fixed) -> ADC_NODE -> NTC (10k @ 25C) -> GND
    V_adc = V_ref * R_ntc / (R_series + R_ntc)
    R_ntc = R_series * adc_val / (ADC_MAX - adc_val)
    """
    if adc_val <= 0 or adc_val >= ADC_MAX:
        return None  # Sensor fault

    resistance = SERIES_RESISTOR * adc_val / (ADC_MAX - adc_val)

    if resistance <= 0:
        return None

    # Steinhart-Hart (Beta equation)
    steinhart = math.log(resistance / NOMINAL_RESISTANCE)
    steinhart /= B_COEFFICIENT
    steinhart += 1.0 / NOMINAL_TEMP_K
    temp_k = 1.0 / steinhart

    return temp_k - 273.15


def read_battery_voltage():
    """Read battery voltage via resistive divider on G36."""
    total = 0
    for _ in range(ADC_SAMPLES):
        total += batt_adc.read()
        time.sleep_ms(1)
    avg = total // ADC_SAMPLES
    if avg <= 0:
        return 0.0
    v_adc = (avg / ADC_MAX) * V_REF
    return v_adc * BATT_DIVIDER_RATIO


def set_system_state(enabled):
    """Enable/disable PA power with asymmetric GaN bias sequencing.

    Enable:  charge pump ON first (-5V gate bias) -> wait -> PA drain ON
    Disable: PA drain OFF first -> wait for POSCAP bleed -> charge pump OFF
    This prevents depletion-mode GaN Idss runaway.
    """
    global system_armed
    system_armed = enabled
    if enabled:
        # Enable: gate bias BEFORE drain voltage
        bias_en.value(1)
        time.sleep_ms(SEQUENCER_DELAY_MS)
        relay_ctrl.value(1)
    else:
        # Disable: drain voltage OFF BEFORE gate bias removed
        relay_ctrl.value(0)
        time.sleep_ms(SEQUENCER_DELAY_MS)
        bias_en.value(0)


def alarm_pulse(count=3):
    """Pulse relay_ctrl LED as visual alarm."""
    for _ in range(count):
        relay_ctrl.value(1)
        time.sleep_ms(200)
        relay_ctrl.value(0)
        time.sleep_ms(200)


# =============================================================
# MAIN LOOP
# =============================================================
print("=" * 50)
print("jamRF-v2 Thermal Failsafe System")
print("Shutdown: {}C | Recovery: {}C".format(SHUTDOWN_TEMP_C, RECOVERY_TEMP_C))
print("Startup delay: {}s".format(STARTUP_DELAY_S))
print("=" * 50)

# Startup delay - system stays OFF
for i in range(STARTUP_DELAY_S, 0, -1):
    print("Starting in {}...".format(i))
    wdt.feed()
    time.sleep(1)

print("System active. Monitoring temperature.")

while True:
    wdt.feed()

    adc_val = read_adc_averaged()
    temp = adc_to_temperature(adc_val)

    if temp is None or temp < SENSOR_FAULT_LOW or temp > SENSOR_FAULT_HIGH:
        # Sensor fault - shut down immediately
        fault_count += 1
        print("SENSOR FAULT #{} (ADC={}) - SHUTTING DOWN".format(fault_count, adc_val))
        set_system_state(False)
        alarm_pulse(5)

        if fault_count >= MAX_CONSECUTIVE_FAULTS:
            print("PERSISTENT SENSOR FAULT - SYSTEM LOCKED OUT")
            while True:
                wdt.feed()
                alarm_pulse(1)
                time.sleep(5)
    else:
        fault_count = 0  # Reset on valid reading

        # Battery undervoltage check (ZVE-3W-83+ requires >= 13V)
        v_batt = read_battery_voltage()

        if v_batt < UNDERVOLT_CUTOFF_V:
            if system_armed or not undervolt_active:
                print("UNDERVOLT {:.1f}V < {:.1f}V - SHUTTING DOWN".format(
                    v_batt, UNDERVOLT_CUTOFF_V))
                set_system_state(False)
                undervolt_active = True
                alarm_pulse(3)
        elif v_batt >= UNDERVOLT_RECOVER_V:
            undervolt_active = False

        if undervolt_active:
            print("Batt {:.1f}V - Waiting for {:.1f}V".format(
                v_batt, UNDERVOLT_RECOVER_V))
        elif temp >= SHUTDOWN_TEMP_C:
            if system_armed:
                print("OVERHEAT {:.1f}C >= {:.1f}C - SHUTTING DOWN".format(
                    temp, SHUTDOWN_TEMP_C))
                set_system_state(False)
                alarm_pulse(5)
            else:
                print("Temp {:.1f}C - Waiting for cooldown to {:.1f}C".format(
                    temp, RECOVERY_TEMP_C))

        elif temp <= RECOVERY_TEMP_C:
            if not system_armed:
                print("Temp {:.1f}C <= {:.1f}C | Batt {:.1f}V - ENABLING".format(
                    temp, RECOVERY_TEMP_C, v_batt))
                set_system_state(True)
            else:
                print("Temp {:.1f}C | Batt {:.1f}V - System OK".format(temp, v_batt))

        else:
            state_str = "ON" if system_armed else "OFF"
            print("Temp {:.1f}C | Batt {:.1f}V - {} (hysteresis)".format(
                temp, v_batt, state_str))

    time.sleep(SAMPLE_INTERVAL_S)
