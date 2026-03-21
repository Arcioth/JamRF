# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

jamRF is a custom PCB hardware platform for chaos-modulated RF jamming, designed for authorized RF testing and research. It uses purpose-built analog/RF hardware (VCOs, PAs, filters) — **not** software-defined radio.

> **Not related to TIIUAE's JamRF.** TIIUAE's project is an SDR-based RF testing framework. This project is independent custom hardware with no shared codebase or architecture.

Hardware designs derived from the Great Scott Gadgets HackRF project, extended with custom RF jammer designs (jamrf-v1 through v4). Licensed under CERN-OHL-P v2.

**Primary active design:** `hardware/jamrf-v2/` — KiCad 9.0, version 2.0.

## Tools & Commands

There is no build system (no Makefile, CMake, etc.). All designs are opened directly in KiCad IDE.

### KiCad CLI (validation/export)
```bash
# ERC (Electrical Rules Check)
kicad-cli sch erc hardware/jamrf-v2/jamrf-v2.kicad_sch

# DRC (Design Rules Check)
kicad-cli pcb drc hardware/jamrf-v2/jamrf-v2.kicad_pcb

# Export netlist
kicad-cli sch export netlist hardware/jamrf-v2/jamrf-v2.kicad_sch -o output.net

# Export BOM (XML)
kicad-cli sch export python-bom hardware/jamrf-v2/jamrf-v2.kicad_sch -o bom.xml

# Plot Gerbers
kicad-cli pcb export gerbers hardware/jamrf-v2/jamrf-v2.kicad_pcb -o gerbers/
```

### Python Utility Scripts
- `hardware/test/si5351-configure.py` — Si5351 clock generator configuration for hardware verification
- `jamrf_v3/update_schematics.py` — programmatic schematic modification
- `jamrf_v4/fix_v4.py`, `fix_sch.py`, `fix_bom_more.py` — component substitution and BOM repair scripts

## KiCad Version Compatibility

| Design | KiCad Format | Status |
|--------|-------------|--------|
| `hardware/jamrf-v2/` | **KiCad 9.0** (v20250114) | Active, primary target |
| `hardware/jamrf-v1/` | KiCad 7+ | Complete flat schematic |
| `jamrf_v3/` | KiCad 6 (v20211123) | Gemini-generated, incomplete |
| `jamrf_v4/` | KiCad 6 (v20211123) | Gemini-generated, WiFi-only variant |
| `hardware/hackrf-one/` | KiCad 6+ (.kicad_sch) + legacy (.sch) | Reference design |
| Legacy boards | KiCad 4/5 (.sch, .brd, .pro) | jawbreaker, jellybean, bubblegum, lemondrop, lollipop |

### KiCad 9 S-Expression Format Rules
When editing `.kicad_sch` files for jamrf-v2, these format requirements must be followed:
- Property names: `"Sheetname"` / `"Sheetfile"` (not `"Sheet name"` / `"Sheet file"`)
- Instances: `(instances (project "name" (path "/uuid" ...)))` nested format
- All symbols need: `exclude_from_sim`, `in_bom`, `on_board`, `dnp` attributes
- Global labels require: `(property "Intersheetrefs" "${INTERSHEET_REFS}")`
- `(embedded_fonts no)` required in lib_symbols
- No `;;` comments in s-expression files
- All properties must have values (no empty property syntax)

## jamrf-v2 Architecture

Hierarchical schematic with 5 sub-sheets, all using **label-based connections** (global labels for inter-sheet, local labels for intra-sheet — no direct wire connections between component pins):

```
jamrf-v2.kicad_sch (top-level)
├── baseband.kicad_sch       — ESP32 (M5StickC Plus2) controller, chaos modulation DAC
├── frontend_gps.kicad_sch   — MAX2751 VCO → 3dB pad → BFCN-1575+ BPF → TGA2215-SM GaN PA → Isolator → SMA
├── frontend_wifi.kicad_sch  — MAX2750 VCO → 3dB pad → BFCN-2440+ BPF → ZVE-3W-83+ PA → Isolator → SMA
├── power.kicad_sch          — 14.8V 4S LiPo → D24V10F5 (5V) + TPS7A4700 (5V analog) + LM2776 (-5V) + U3V70F15 (15V WiFi PA) + MOSFET switches
└── control.kicad_sch        — LM393 GaN bias sequencing, NTC thermal monitoring
```

### PCB Parameters
- **Bands**: GPS L1 (1.575 GHz), WiFi/ISM (2.4 GHz)
- **Stackup**: 4-layer Isola FR408HR — F.Cu / GND (In1.Cu) / PWR (In2.Cu) / B.Cu
- **Dielectric**: Er = 3.65, tan d = 0.0095 (stable 1-10 GHz)
- **Board**: 120x90mm, 0.062", 1oz Cu, ENIG finish
- **RF impedance**: 50 ohm controlled, 0.40mm microstrip over 0.2mm prepreg
- **Power**: 14.8V 4S LiPo

### RF Design Parameters
| Parameter | GPS L1 (1.575 GHz) | WiFi (2.4 GHz) |
|-----------|:---:|:---:|
| Lambda_0 | 19.03 cm | 12.49 cm |
| Epsilon_eff | 2.848 | 2.848 |
| Lambda_g (guided) | 11.28 cm | 7.40 cm |
| Lambda_g/4 | 28.2 mm | 18.5 mm |
| Via fence max spacing | 11.3 mm | 7.4 mm |
| Ground stitch spacing | <= 5.0 mm | <= 5.0 mm |
| Insertion loss | 0.065 dB/cm | 0.086 dB/cm |

### Net Classes
| Net Class | Trace Width | Clearance |
|-----------|------------|-----------|
| Default | 0.254mm | 0.2mm |
| RF_50ohm | 0.40mm | 0.3mm |
| Power | 1.0mm | 0.3mm |
| HighPower | 2.54mm | 0.5mm |

### Critical Component Safety Rules
- **LM2776 charge pump**: Max VIN = 5.5V. Must be powered from +5V rail, NOT directly from LiPo (+14V8)
- **TGA2215-SM GaN PA**: Depletion-mode device. Gate bias (-5V) MUST be applied before drain voltage — sequenced via LM393 comparator circuit
- **SQJ407EP P-FET switches**: High-side, controlled via 2N7002 N-FET level shifters. 100k pull-up keeps them OFF by default
- **U3V70F15 buck-boost**: Regulates switched battery voltage (+14V8_SW, 12.8-16.8V) to 15V fixed on +14V8_WIFI rail, keeping ZVE-3W-83+ within its 16V absolute max
- **Pi-attenuator values**: 292/18/292 ohm for 3dB pad, 50-ohm matched

### Library Configuration
- Custom symbol library: `jamrf-v2.kicad_sym` (18 symbols with `jamrf-v2:` prefix, including U3V70F15)
- Custom footprint library: `jamrf-v2.pretty/` (6 footprints: M5StickC_Plus2_Module, Pololu_D24V10F5, Pololu_U3V70F15, Ferrite_Isolator_DropIn, Mini-Circuits_CP1281, Wurth_36103305_Shield)
- Footprints reference KiCad standard libraries via `KICAD7_FOOTPRINT_DIR` env var
- Shared legacy library: `hardware/kicad/hackrf.lib` / `hackrf.mod`

## Failsafe Firmware (`failsafe.py`)

MicroPython running on M5StickC Plus2 (ESP32). Pin mapping:
- **G25/DAC**: GPS_TUNE (DAC1 output to MAX2751 VCO)
- **G26/DAC**: WIFI_TUNE (DAC2 output to MAX2750 VCO)
- **G36/ADC**: THERM_ADC — NTC thermistor (ADC1_CH0, always available)
- **G0/ADC**: BATT_ADC — Battery voltage (100k/22k divider)
- **G33**: BIAS_EN — LM2776 charge pump enable (generates -5V gate bias)
- **G32**: RELAY_CTRL — Q3/Q2 WiFi PA MOSFET switch

**Power sequencing (GaN safety):** Enable: BIAS_EN HIGH → 15ms → RELAY_CTRL HIGH. Disable: RELAY_CTRL LOW → 15ms → BIAS_EN LOW. Prevents depletion-mode Idss runaway.

**NTC divider topology:** +3V3 → R_TH (10k fixed) → midpoint → NTC → GND. Formula: `R_ntc = R_TH * adc / (ADC_MAX - adc)`. Voltage rises with temperature.

Thresholds: thermal shutdown 85C (recover 80C), undervoltage cutoff 13.0V (recover 13.5V). 16-sample ADC averaging, 1Hz polling, 10s watchdog, 5-fault sensor lockout.

## jamrf-v4 Differences

WiFi/ISM 2.4 GHz only (GPS L1 removed). Replaces GaN PA path with SEPIC boost-buck converter and quadrature hybrids. Simplified architecture vs v2.

## Known Issues / TODO
- 7 pre-existing wire_dangling ERC warnings in power/control sheets (KiCad ERC false positives from wire-to-pin junction detection)
- PCB layout not yet started (component placement, RF trace routing, copper zone fills)
- `hardware/gsg-kicad-lib/` directory exists but is empty
