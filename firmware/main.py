"""
jamRF-v2 Operational Firmware
=============================
Target: M5StickC Plus 2 (ESP32-PICO-V3-02)
Runtime: MicroPython

Full operational firmware with chaos modulation engine, safety monitoring,
GaN bias sequencing, display UI, and button-driven mode control.

Pin Mapping (matches jamrf-v2 schematic):
  G25/DAC1  GPS_TUNE    — Chaos modulation output to MAX2751 VCO
  G26/DAC2  WIFI_TUNE   — Chaos modulation output to MAX2750 VCO
  G36/ADC   THERM_ADC   — NTC thermistor voltage divider (ADC1_CH0)
  G0/ADC    BATT_ADC    — Battery voltage divider (100k/22k)
  G35/ADC   BIAS_OK     — LM393 comparator output (gate bias confirmation)
  G33       BIAS_EN     — LM2776 charge pump enable (-5V gate bias)
  G32       RELAY_CTRL  — Q3/Q2 WiFi PA MOSFET switch
  G37       BTN_A       — Mode cycle button
  G39       BTN_B       — Parameter adjust button
  G2        BUZZER      — Internal buzzer

Modes (Button A cycles):
  OFF  -> GPS -> WIFI -> DUAL -> OFF

Safety (always active, overrides all modes):
  - Thermal shutdown 85C / recover 80C
  - Battery undervoltage cutoff 13.0V / recover 13.5V
  - GaN bias sequencing: -5V gate bias before drain voltage
  - BIAS_OK readback: LM393 confirms bias present before PA enable
  - Sensor fault lockout after 5 consecutive bad readings
  - 10s watchdog timer
"""

import machine
import time
import math
import struct

# =============================================================================
# PIN CONFIGURATION
# =============================================================================
PIN_GPS_TUNE = 25      # DAC1 output to MAX2751 VCO
PIN_WIFI_TUNE = 26     # DAC2 output to MAX2750 VCO
PIN_THERM_ADC = 36     # NTC thermistor ADC input
PIN_BATT_ADC = 0       # Battery voltage divider ADC input
PIN_BIAS_OK = 35       # LM393 comparator output (input only)
PIN_BIAS_EN = 33       # LM2776 charge pump enable
PIN_RELAY_CTRL = 32    # WiFi PA MOSFET switch
PIN_BTN_A = 37         # Mode button
PIN_BTN_B = 39         # Parameter button
PIN_BUZZER = 2         # Internal buzzer

# =============================================================================
# OPERATING MODES
# =============================================================================
MODE_OFF = 0
MODE_GPS = 1
MODE_WIFI = 2
MODE_DUAL = 3
MODE_NAMES = ["OFF", "GPS", "WIFI", "DUAL"]

# =============================================================================
# SAFETY THRESHOLDS
# =============================================================================
SHUTDOWN_TEMP_C = 85.0
RECOVERY_TEMP_C = 80.0
SENSOR_FAULT_LOW = -20.0
SENSOR_FAULT_HIGH = 150.0
UNDERVOLT_CUTOFF_V = 13.0
UNDERVOLT_RECOVER_V = 13.5
STARTUP_DELAY_S = 3
SAMPLE_INTERVAL_MS = 100    # Safety check rate (10 Hz)
CHAOS_INTERVAL_US = 50      # Chaos update rate (~20 kHz)
ADC_SAMPLES = 16
SEQUENCER_DELAY_MS = 15
MAX_CONSECUTIVE_FAULTS = 5

# =============================================================================
# THERMISTOR PARAMETERS (Vishay NTCS0805E3103FMT)
# =============================================================================
B_COEFFICIENT = 3950
NOMINAL_RESISTANCE = 10000
NOMINAL_TEMP_K = 298.15
SERIES_RESISTOR = 10000
ADC_MAX = 4095
V_REF = 3.3

# =============================================================================
# BATTERY VOLTAGE DIVIDER (R_BATT1=100k / R_BATT2=22k)
# =============================================================================
R_BATT1 = 100000
R_BATT2 = 22000
BATT_DIVIDER_RATIO = (R_BATT1 + R_BATT2) / R_BATT2

# =============================================================================
# VCO TUNING PARAMETERS
#
# MAX2751 (GPS L1, 1.575 GHz): ~200 MHz/V, TUNE 0.4-2.4V
# MAX2750 (WiFi 2.4 GHz):      ~250 MHz/V, TUNE 0.4-2.4V
# ESP32 DAC: 8-bit (0-255), 0-3.3V, 1 step = 12.94 mV
# =============================================================================
GPS_DAC_CENTER = 100    # ~1.29V -> ~1.575 GHz (calibrate on hardware)
GPS_DAC_SWING = 12      # +/-155 mV -> +/-31 MHz spread
WIFI_DAC_CENTER = 116   # ~1.50V -> ~2.4 GHz (calibrate on hardware)
WIFI_DAC_SWING = 16     # +/-207 mV -> +/-52 MHz spread

# =============================================================================
# CHAOS ENGINE PARAMETERS
# =============================================================================
CHAOS_R = 3.9999        # Logistic map parameter (full chaos)
LORENZ_SIGMA = 10.0     # Lorenz attractor parameters
LORENZ_RHO = 28.0
LORENZ_BETA = 8.0 / 3.0
LORENZ_DT = 0.005

# =============================================================================
# DISPLAY — ST7789V2 (M5StickC Plus2: 135x240, SPI)
# =============================================================================
DISP_WIDTH = 135
DISP_HEIGHT = 240
DISP_SCK = 13
DISP_MOSI = 15
DISP_DC = 14
DISP_CS = 5
DISP_RST = 12
DISP_BL = 27

# Colors (RGB565)
BLACK = 0x0000
WHITE = 0xFFFF
RED = 0xF800
GREEN = 0x07E0
BLUE = 0x001F
ORANGE = 0xFD20
YELLOW = 0xFFE0
CYAN = 0x07FF
DARK_BG = 0x1926      # Dark navy matching logo


# =============================================================================
# MINIMAL ST7789 DISPLAY DRIVER
# =============================================================================
class ST7789:
    def __init__(self):
        self.spi = machine.SPI(1, baudrate=40000000, polarity=1, phase=0,
                               sck=machine.Pin(DISP_SCK),
                               mosi=machine.Pin(DISP_MOSI))
        self.dc = machine.Pin(DISP_DC, machine.Pin.OUT)
        self.cs = machine.Pin(DISP_CS, machine.Pin.OUT)
        self.rst = machine.Pin(DISP_RST, machine.Pin.OUT)
        self.bl = machine.Pin(DISP_BL, machine.Pin.OUT)
        self._init_display()

    def _cmd(self, cmd, data=None):
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytes([cmd]))
        if data:
            self.dc.value(1)
            self.spi.write(data)
        self.cs.value(1)

    def _init_display(self):
        self.rst.value(0)
        time.sleep_ms(50)
        self.rst.value(1)
        time.sleep_ms(150)
        self._cmd(0x01)         # SWRESET
        time.sleep_ms(150)
        self._cmd(0x11)         # SLPOUT
        time.sleep_ms(50)
        self._cmd(0x3A, b'\x55')  # COLMOD: 16-bit color
        self._cmd(0x36, b'\x00')  # MADCTL: normal orientation
        self._cmd(0x21)         # INVON (needed for M5StickC)
        self._cmd(0x13)         # NORON
        time.sleep_ms(10)
        self._cmd(0x29)         # DISPON
        self.bl.value(1)

    def _set_window(self, x0, y0, x1, y1):
        # Column offset for 135-wide display centered in 240-wide controller
        xoff = 52
        yoff = 40
        self._cmd(0x2A, struct.pack('>HH', x0 + xoff, x1 + xoff))
        self._cmd(0x2B, struct.pack('>HH', y0 + yoff, y1 + yoff))
        self._cmd(0x2C)

    def fill(self, color):
        self._set_window(0, 0, DISP_WIDTH - 1, DISP_HEIGHT - 1)
        buf = struct.pack('>H', color) * 135
        self.cs.value(0)
        self.dc.value(1)
        for _ in range(240):
            self.spi.write(buf)
        self.cs.value(1)

    def fill_rect(self, x, y, w, h, color):
        self._set_window(x, y, x + w - 1, y + h - 1)
        buf = struct.pack('>H', color) * w
        self.cs.value(0)
        self.dc.value(1)
        for _ in range(h):
            self.spi.write(buf)
        self.cs.value(1)

    def text(self, s, x, y, color=WHITE, scale=1):
        for i, ch in enumerate(s):
            self._draw_char(ch, x + i * 6 * scale, y, color, scale)

    def _draw_char(self, ch, x, y, color, scale):
        idx = ord(ch)
        if idx < 32 or idx > 126:
            idx = 32
        idx -= 32
        for col in range(5):
            line = _FONT[idx * 5 + col]
            for row in range(8):
                if line & (1 << row):
                    if scale == 1:
                        self._pixel(x + col, y + row, color)
                    else:
                        self.fill_rect(x + col * scale, y + row * scale,
                                       scale, scale, color)

    def _pixel(self, x, y, color):
        if 0 <= x < DISP_WIDTH and 0 <= y < DISP_HEIGHT:
            self._set_window(x, y, x, y)
            self.cs.value(0)
            self.dc.value(1)
            self.spi.write(struct.pack('>H', color))
            self.cs.value(1)


# 5x8 font (ASCII 32-126, 5 bytes per character)
_FONT = bytes([
    0x00,0x00,0x00,0x00,0x00, # space
    0x00,0x00,0x5F,0x00,0x00, # !
    0x00,0x07,0x00,0x07,0x00, # "
    0x14,0x7F,0x14,0x7F,0x14, # #
    0x24,0x2A,0x7F,0x2A,0x12, # $
    0x23,0x13,0x08,0x64,0x62, # %
    0x36,0x49,0x56,0x20,0x50, # &
    0x00,0x08,0x07,0x03,0x00, # '
    0x00,0x1C,0x22,0x41,0x00, # (
    0x00,0x41,0x22,0x1C,0x00, # )
    0x2A,0x1C,0x7F,0x1C,0x2A, # *
    0x08,0x08,0x3E,0x08,0x08, # +
    0x00,0x80,0x70,0x30,0x00, # ,
    0x08,0x08,0x08,0x08,0x08, # -
    0x00,0x00,0x60,0x60,0x00, # .
    0x20,0x10,0x08,0x04,0x02, # /
    0x3E,0x51,0x49,0x45,0x3E, # 0
    0x00,0x42,0x7F,0x40,0x00, # 1
    0x72,0x49,0x49,0x49,0x46, # 2
    0x21,0x41,0x49,0x4D,0x33, # 3
    0x18,0x14,0x12,0x7F,0x10, # 4
    0x27,0x45,0x45,0x45,0x39, # 5
    0x3C,0x4A,0x49,0x49,0x31, # 6
    0x41,0x21,0x11,0x09,0x07, # 7
    0x36,0x49,0x49,0x49,0x36, # 8
    0x46,0x49,0x49,0x29,0x1E, # 9
    0x00,0x00,0x14,0x00,0x00, # :
    0x00,0x40,0x34,0x00,0x00, # ;
    0x00,0x08,0x14,0x22,0x41, # <
    0x14,0x14,0x14,0x14,0x14, # =
    0x00,0x41,0x22,0x14,0x08, # >
    0x02,0x01,0x59,0x09,0x06, # ?
    0x3E,0x41,0x5D,0x59,0x4E, # @
    0x7C,0x12,0x11,0x12,0x7C, # A
    0x7F,0x49,0x49,0x49,0x36, # B
    0x3E,0x41,0x41,0x41,0x22, # C
    0x7F,0x41,0x41,0x41,0x3E, # D
    0x7F,0x49,0x49,0x49,0x41, # E
    0x7F,0x09,0x09,0x09,0x01, # F
    0x3E,0x41,0x41,0x51,0x73, # G
    0x7F,0x08,0x08,0x08,0x7F, # H
    0x00,0x41,0x7F,0x41,0x00, # I
    0x20,0x40,0x41,0x3F,0x01, # J
    0x7F,0x08,0x14,0x22,0x41, # K
    0x7F,0x40,0x40,0x40,0x40, # L
    0x7F,0x02,0x1C,0x02,0x7F, # M
    0x7F,0x04,0x08,0x10,0x7F, # N
    0x3E,0x41,0x41,0x41,0x3E, # O
    0x7F,0x09,0x09,0x09,0x06, # P
    0x3E,0x41,0x51,0x21,0x5E, # Q
    0x7F,0x09,0x19,0x29,0x46, # R
    0x26,0x49,0x49,0x49,0x32, # S
    0x03,0x01,0x7F,0x01,0x03, # T
    0x3F,0x40,0x40,0x40,0x3F, # U
    0x1F,0x20,0x40,0x20,0x1F, # V
    0x3F,0x40,0x38,0x40,0x3F, # W
    0x63,0x14,0x08,0x14,0x63, # X
    0x03,0x04,0x78,0x04,0x03, # Y
    0x61,0x59,0x49,0x4D,0x43, # Z
    0x00,0x7F,0x41,0x41,0x41, # [
    0x02,0x04,0x08,0x10,0x20, # backslash
    0x00,0x41,0x41,0x41,0x7F, # ]
    0x04,0x02,0x01,0x02,0x04, # ^
    0x40,0x40,0x40,0x40,0x40, # _
    0x00,0x03,0x07,0x08,0x00, # `
    0x20,0x54,0x54,0x78,0x40, # a
    0x7F,0x28,0x44,0x44,0x38, # b
    0x38,0x44,0x44,0x44,0x28, # c
    0x38,0x44,0x44,0x28,0x7F, # d
    0x38,0x54,0x54,0x54,0x18, # e
    0x00,0x08,0x7E,0x09,0x02, # f
    0x18,0xA4,0xA4,0x9C,0x78, # g
    0x7F,0x08,0x04,0x04,0x78, # h
    0x00,0x44,0x7D,0x40,0x00, # i
    0x20,0x40,0x40,0x3D,0x00, # j
    0x7F,0x10,0x28,0x44,0x00, # k
    0x00,0x41,0x7F,0x40,0x00, # l
    0x7C,0x04,0x78,0x04,0x78, # m
    0x7C,0x08,0x04,0x04,0x78, # n
    0x38,0x44,0x44,0x44,0x38, # o
    0xFC,0x18,0x24,0x24,0x18, # p
    0x18,0x24,0x24,0x18,0xFC, # q
    0x7C,0x08,0x04,0x04,0x08, # r
    0x48,0x54,0x54,0x54,0x24, # s
    0x04,0x04,0x3F,0x44,0x24, # t
    0x3C,0x40,0x40,0x20,0x7C, # u
    0x1C,0x20,0x40,0x20,0x1C, # v
    0x3C,0x40,0x30,0x40,0x3C, # w
    0x44,0x28,0x10,0x28,0x44, # x
    0x4C,0x90,0x90,0x90,0x7C, # y
    0x44,0x64,0x54,0x4C,0x44, # z
    0x00,0x08,0x36,0x41,0x00, # {
    0x00,0x00,0x77,0x00,0x00, # |
    0x00,0x41,0x36,0x08,0x00, # }
    0x02,0x01,0x02,0x04,0x02, # ~
])


# =============================================================================
# CHAOS MODULATION ENGINE
# =============================================================================
class ChaosEngine:
    """Generates chaotic signals via logistic map for VCO modulation."""

    def __init__(self):
        self.x_gps = 0.1 + (time.ticks_us() % 800) / 1000.0   # Random seed
        self.x_wifi = 0.4 + (time.ticks_us() % 500) / 1000.0
        # Lorenz state
        self.lx = 1.0
        self.ly = 1.0
        self.lz = 1.0
        self.algorithm = 0  # 0=logistic, 1=lorenz

    def step_logistic(self):
        """Advance logistic map for both channels."""
        self.x_gps = CHAOS_R * self.x_gps * (1.0 - self.x_gps)
        self.x_wifi = CHAOS_R * self.x_wifi * (1.0 - self.x_wifi)
        # Prevent convergence to fixed points
        if self.x_gps < 0.01 or self.x_gps > 0.99:
            self.x_gps = 0.3 + (time.ticks_us() % 400) / 1000.0
        if self.x_wifi < 0.01 or self.x_wifi > 0.99:
            self.x_wifi = 0.6 + (time.ticks_us() % 300) / 1000.0

    def step_lorenz(self):
        """Advance Lorenz attractor, map x->GPS, y->WiFi."""
        dx = LORENZ_SIGMA * (self.ly - self.lx) * LORENZ_DT
        dy = (self.lx * (LORENZ_RHO - self.lz) - self.ly) * LORENZ_DT
        dz = (self.lx * self.ly - LORENZ_BETA * self.lz) * LORENZ_DT
        self.lx += dx
        self.ly += dy
        self.lz += dz
        # Normalize Lorenz output to 0-1 range (typical range: x=-20..20)
        self.x_gps = max(0.0, min(1.0, (self.lx + 25.0) / 50.0))
        self.x_wifi = max(0.0, min(1.0, (self.ly + 30.0) / 60.0))

    def step(self):
        """Advance one step using selected algorithm."""
        if self.algorithm == 0:
            self.step_logistic()
        else:
            self.step_lorenz()

    def gps_dac_value(self):
        """Get DAC value for GPS VCO TUNE pin."""
        val = int(GPS_DAC_CENTER + (self.x_gps - 0.5) * 2.0 * GPS_DAC_SWING)
        return max(0, min(255, val))

    def wifi_dac_value(self):
        """Get DAC value for WiFi VCO TUNE pin."""
        val = int(WIFI_DAC_CENTER + (self.x_wifi - 0.5) * 2.0 * WIFI_DAC_SWING)
        return max(0, min(255, val))

    def toggle_algorithm(self):
        self.algorithm = 1 - self.algorithm
        return "LORENZ" if self.algorithm else "LOGISTIC"


# =============================================================================
# HARDWARE SETUP
# =============================================================================
# DAC outputs for VCO tuning
dac_gps = machine.DAC(machine.Pin(PIN_GPS_TUNE))
dac_wifi = machine.DAC(machine.Pin(PIN_WIFI_TUNE))
dac_gps.write(0)
dac_wifi.write(0)

# ADC inputs
adc_therm = machine.ADC(machine.Pin(PIN_THERM_ADC))
adc_therm.atten(machine.ADC.ATTN_11DB)
adc_therm.width(machine.ADC.WIDTH_12BIT)

adc_batt = machine.ADC(machine.Pin(PIN_BATT_ADC))
adc_batt.atten(machine.ADC.ATTN_11DB)
adc_batt.width(machine.ADC.WIDTH_12BIT)

# Digital I/O
bias_ok_pin = machine.Pin(PIN_BIAS_OK, machine.Pin.IN)
bias_en = machine.Pin(PIN_BIAS_EN, machine.Pin.OUT, value=0)
relay_ctrl = machine.Pin(PIN_RELAY_CTRL, machine.Pin.OUT, value=0)
btn_a = machine.Pin(PIN_BTN_A, machine.Pin.IN, machine.Pin.PULL_UP)
btn_b = machine.Pin(PIN_BTN_B, machine.Pin.IN, machine.Pin.PULL_UP)

try:
    buzzer = machine.PWM(machine.Pin(PIN_BUZZER), freq=2000, duty=0)
except Exception:
    buzzer = None

# Watchdog
wdt = machine.WDT(timeout=10000)

# Chaos engine
chaos = ChaosEngine()


# =============================================================================
# SENSOR FUNCTIONS
# =============================================================================
def read_temperature():
    total = 0
    for _ in range(ADC_SAMPLES):
        total += adc_therm.read()
        time.sleep_us(100)
    avg = total // ADC_SAMPLES
    if avg <= 0 or avg >= ADC_MAX:
        return None
    resistance = SERIES_RESISTOR * avg / (ADC_MAX - avg)
    if resistance <= 0:
        return None
    steinhart = math.log(resistance / NOMINAL_RESISTANCE) / B_COEFFICIENT
    steinhart += 1.0 / NOMINAL_TEMP_K
    return (1.0 / steinhart) - 273.15


def read_battery_voltage():
    total = 0
    for _ in range(ADC_SAMPLES):
        total += adc_batt.read()
        time.sleep_us(100)
    avg = total // ADC_SAMPLES
    if avg <= 0:
        return 0.0
    return (avg / ADC_MAX) * V_REF * BATT_DIVIDER_RATIO


def read_bias_ok():
    return bias_ok_pin.value() == 1


# =============================================================================
# POWER SEQUENCING
# =============================================================================
def enable_pa():
    """Enable PA with GaN-safe bias sequencing.
    Gate bias (-5V) MUST be present before drain voltage.
    """
    bias_en.value(1)
    time.sleep_ms(SEQUENCER_DELAY_MS)
    # Verify BIAS_OK from LM393 comparator
    if not read_bias_ok():
        # Wait additional time for charge pump to stabilize
        time.sleep_ms(50)
        if not read_bias_ok():
            print("!! BIAS_OK not confirmed — aborting PA enable")
            bias_en.value(0)
            return False
    relay_ctrl.value(1)
    return True


def disable_pa():
    """Disable PA: drain OFF first, then gate bias removed."""
    relay_ctrl.value(0)
    time.sleep_ms(SEQUENCER_DELAY_MS)
    bias_en.value(0)


def beep(freq=2000, duration_ms=100):
    if buzzer:
        buzzer.freq(freq)
        buzzer.duty(512)
        time.sleep_ms(duration_ms)
        buzzer.duty(0)


# =============================================================================
# DISPLAY MANAGER
# =============================================================================
class Display:
    def __init__(self):
        self.lcd = None
        try:
            self.lcd = ST7789()
            self.lcd.fill(DARK_BG)
        except Exception as e:
            print("Display init failed: {}".format(e))
        self._last_mode = -1
        self._last_temp = -999
        self._last_batt = -999
        self._last_status = ""

    def splash(self):
        if not self.lcd:
            return
        self.lcd.fill(DARK_BG)
        self.lcd.text("jamRF", 30, 20, ORANGE, 3)
        self.lcd.text("v2.0", 42, 50, WHITE, 2)
        self.lcd.text("Chaos Modulated", 6, 90, CYAN, 1)
        self.lcd.text("RF Platform", 21, 105, CYAN, 1)
        self.lcd.text("A:Mode  B:Algo", 9, 200, WHITE, 1)
        self.lcd.text("Initializing...", 9, 220, YELLOW, 1)

    def update(self, mode, temp, batt, armed, algo, fault_msg=None):
        if not self.lcd:
            return
        # Only redraw changed sections
        if mode != self._last_mode:
            self.lcd.fill_rect(0, 0, 135, 30, DARK_BG)
            mode_colors = [WHITE, GREEN, BLUE, ORANGE]
            self.lcd.text("MODE:", 5, 5, WHITE, 2)
            self.lcd.text(MODE_NAMES[mode], 70, 5, mode_colors[mode], 2)
            self._last_mode = mode

        # Temperature bar
        t_int = int(temp) if temp else -999
        if t_int != self._last_temp:
            self.lcd.fill_rect(0, 35, 135, 45, DARK_BG)
            t_str = "{:.1f}C".format(temp) if temp else "FAULT"
            t_color = RED if (temp and temp >= SHUTDOWN_TEMP_C) else \
                      YELLOW if (temp and temp >= RECOVERY_TEMP_C) else GREEN
            self.lcd.text("TEMP", 5, 38, WHITE, 1)
            self.lcd.text(t_str, 40, 38, t_color, 2)
            # Progress bar
            if temp:
                bar_w = max(0, min(125, int((temp / 100.0) * 125)))
                self.lcd.fill_rect(5, 60, 125, 8, BLACK)
                self.lcd.fill_rect(5, 60, bar_w, 8, t_color)
            self._last_temp = t_int

        # Battery
        b_int = int(batt * 10) if batt else -999
        if b_int != self._last_batt:
            self.lcd.fill_rect(0, 75, 135, 30, DARK_BG)
            b_str = "{:.1f}V".format(batt) if batt else "?"
            b_color = RED if batt < UNDERVOLT_CUTOFF_V else \
                      YELLOW if batt < UNDERVOLT_RECOVER_V else GREEN
            self.lcd.text("BATT", 5, 78, WHITE, 1)
            self.lcd.text(b_str, 40, 78, b_color, 2)
            # Percentage bar (12.0V=0%, 16.8V=100%)
            pct = max(0, min(100, int((batt - 12.0) / 4.8 * 100)))
            self.lcd.fill_rect(5, 98, 125, 8, BLACK)
            self.lcd.fill_rect(5, 98, int(pct * 1.25), 8, b_color)
            self._last_batt = b_int

        # Status area
        status = "ARMED" if armed else "SAFE"
        if fault_msg:
            status = fault_msg
        if status != self._last_status:
            self.lcd.fill_rect(0, 115, 135, 50, DARK_BG)
            s_color = GREEN if armed else RED if fault_msg else WHITE
            self.lcd.text(status, 5, 120, s_color, 2)
            algo_name = "LORENZ" if algo else "LOGISTIC"
            self.lcd.text("Algo:" + algo_name, 5, 145, CYAN, 1)
            self._last_status = status

        # Footer
        self.lcd.fill_rect(0, 220, 135, 20, DARK_BG)
        self.lcd.text("A:Mode  B:Algo", 9, 225, WHITE, 1)


# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main():
    print("=" * 50)
    print("jamRF-v2 Operational Firmware")
    print("Modes: OFF / GPS / WIFI / DUAL")
    print("Safety: {}C shutdown, {}V cutoff".format(
        SHUTDOWN_TEMP_C, UNDERVOLT_CUTOFF_V))
    print("=" * 50)

    display = Display()
    display.splash()

    mode = MODE_OFF
    armed = False
    fault_count = 0
    undervolt_active = False
    btn_a_last = 1
    btn_b_last = 1
    last_safety_ms = 0
    last_display_ms = 0

    # Startup delay
    for i in range(STARTUP_DELAY_S, 0, -1):
        print("Starting in {}...".format(i))
        wdt.feed()
        time.sleep(1)

    print("System active.")

    # Chaos modulation timer — drives DAC updates at high rate
    chaos_active = False

    def chaos_tick(_):
        if not chaos_active:
            return
        chaos.step()
        if mode in (MODE_GPS, MODE_DUAL):
            dac_gps.write(chaos.gps_dac_value())
        if mode in (MODE_WIFI, MODE_DUAL):
            dac_wifi.write(chaos.wifi_dac_value())

    chaos_timer = machine.Timer(0)

    while True:
        wdt.feed()
        now = time.ticks_ms()

        # ---- BUTTON HANDLING ----
        btn_a_now = btn_a.value()
        btn_b_now = btn_b.value()

        if btn_a_last == 1 and btn_a_now == 0:  # Button A pressed
            # Cycle mode
            if armed:
                # Shut down first
                disable_pa()
                chaos_active = False
                chaos_timer.deinit()
                dac_gps.write(0)
                dac_wifi.write(0)
                armed = False

            mode = (mode + 1) % 4
            print("Mode: {}".format(MODE_NAMES[mode]))
            beep(1500 + mode * 300, 80)

            if mode != MODE_OFF:
                # Arm the system
                print("Enabling PA...")
                success = enable_pa()
                if success:
                    armed = True
                    chaos_active = True
                    chaos_timer.init(period=1,
                                     mode=machine.Timer.PERIODIC,
                                     callback=chaos_tick)
                    print("PA armed — {} mode, chaos running".format(
                        MODE_NAMES[mode]))
                    beep(2500, 150)
                else:
                    mode = MODE_OFF
                    print("PA enable failed — returning to OFF")
                    beep(500, 500)

        if btn_b_last == 1 and btn_b_now == 0:  # Button B pressed
            algo = chaos.toggle_algorithm()
            print("Chaos algorithm: {}".format(algo))
            beep(1800, 80)

        btn_a_last = btn_a_now
        btn_b_last = btn_b_now

        # ---- SAFETY MONITORING (10 Hz) ----
        if time.ticks_diff(now, last_safety_ms) >= SAMPLE_INTERVAL_MS:
            last_safety_ms = now
            temp = read_temperature()
            v_batt = read_battery_voltage()
            fault_msg = None

            # Sensor fault check
            if temp is None or temp < SENSOR_FAULT_LOW or temp > SENSOR_FAULT_HIGH:
                fault_count += 1
                fault_msg = "SNSR FAULT"
                print("SENSOR FAULT #{} — shutting down".format(fault_count))
                if armed:
                    disable_pa()
                    chaos_active = False
                    chaos_timer.deinit()
                    dac_gps.write(0)
                    dac_wifi.write(0)
                    armed = False
                    mode = MODE_OFF
                beep(500, 300)

                if fault_count >= MAX_CONSECUTIVE_FAULTS:
                    print("PERSISTENT SENSOR FAULT — LOCKED OUT")
                    display.update(mode, 0, v_batt, False, chaos.algorithm,
                                   "LOCKOUT")
                    while True:
                        wdt.feed()
                        beep(400, 200)
                        time.sleep(5)
            else:
                fault_count = 0

                # Undervoltage check
                if v_batt < UNDERVOLT_CUTOFF_V:
                    if armed or not undervolt_active:
                        fault_msg = "LOW BATT"
                        print("UNDERVOLT {:.1f}V — shutting down".format(v_batt))
                        if armed:
                            disable_pa()
                            chaos_active = False
                            chaos_timer.deinit()
                            dac_gps.write(0)
                            dac_wifi.write(0)
                            armed = False
                            mode = MODE_OFF
                        undervolt_active = True
                        beep(600, 300)
                elif v_batt >= UNDERVOLT_RECOVER_V:
                    undervolt_active = False

                # Overtemperature check
                if temp >= SHUTDOWN_TEMP_C and armed:
                    fault_msg = "OVERHEAT"
                    print("OVERHEAT {:.1f}C — shutting down".format(temp))
                    disable_pa()
                    chaos_active = False
                    chaos_timer.deinit()
                    dac_gps.write(0)
                    dac_wifi.write(0)
                    armed = False
                    mode = MODE_OFF
                    beep(400, 500)

                # Auto-recovery (only if mode was set and condition cleared)
                if undervolt_active:
                    fault_msg = "LOW BATT"

            # Serial status (1 Hz)
            if temp:
                state = "ON" if armed else "OFF"
                print("T={:.1f}C V={:.1f}V Mode={} PA={} Bias={}".format(
                    temp, v_batt, MODE_NAMES[mode], state,
                    "OK" if read_bias_ok() else "NO"))

            # Display update (throttled)
            if time.ticks_diff(now, last_display_ms) >= 500:
                last_display_ms = now
                display.update(mode, temp if temp else 0, v_batt,
                               armed, chaos.algorithm, fault_msg)

        time.sleep_ms(10)


# =============================================================================
# ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Emergency shutdown on unhandled exception
        print("FATAL: {}".format(e))
        machine.Pin(PIN_RELAY_CTRL, machine.Pin.OUT).value(0)
        time.sleep_ms(SEQUENCER_DELAY_MS)
        machine.Pin(PIN_BIAS_EN, machine.Pin.OUT).value(0)
        machine.DAC(machine.Pin(PIN_GPS_TUNE)).write(0)
        machine.DAC(machine.Pin(PIN_WIFI_TUNE)).write(0)
        raise
