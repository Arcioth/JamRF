# JamRF v2

Dual-band chaos-modulated RF transmitter targeting GPS L1 (1.575 GHz) and WiFi/ISM (2.4 GHz). Open hardware design built with KiCad 9.0.

> **Legal Notice:** This design is published for educational and research purposes only. Intentional RF interference is illegal in most jurisdictions. The user is solely responsible for ensuring compliance with all applicable local, national, and international regulations. The author assumes no liability for misuse.

## Architecture

JamRF v2 uses a hierarchical schematic design inspired by the [HackRF One](https://github.com/greatscottgadgets/hackrf) baseband/frontend separation pattern.

```
                         +--[ Frontend GPS ]---> SMA (1.575 GHz Yagi)
                         |   MAX2751 VCO -> Pi-Atten -> BPF -> TGA2215-SM GaN PA -> Isolator
                         |
[ Baseband ] --- DAC --->+
  M5StickC Plus2         |
  (ESP32-PICO-V3-02)     +--[ Frontend WiFi ]--> SMA (2.4 GHz Yagi)
       |                     MAX2750 VCO -> Pi-Atten -> BPF -> ZVE-3W-83+ PA -> Isolator
       |
  [ Control ]            [ Power ]
  LM393 comparator       4S LiPo (14.8V)
  NTC thermal monitor    D24V10F5 buck (5V)
  GaN bias sequencing    TPS7A4700 LDO (5V analog)
                         LM2776 charge pump (-5V)
                         P-FET switched PA rails
```

### Signal Generation

Both RF chains use chaos-modulated VCOs. The ESP32's DAC outputs (G25, G26) drive the TUNE pins of the MAX2751 and MAX2750 VCOs, sweeping them across their respective bands. The chaotic modulation signal spreads spectral energy across the target bandwidth.

### Power System

- **Input:** 14.8V 4S LiPo (XT60 connector, min 80C discharge)
- **5V digital rail:** Pololu D24V10F5 fixed buck converter
- **5V analog rail:** TPS7A4700 ultra-low-noise LDO (ANY-OUT: 1.4+3.2+0.4V) for VCO supply
- **-5V bias rail:** LM2776 inverting charge pump for GaN PA gate bias
- **PA power:** P-FET high-side switches (SQJ407EP) with 2N7002 level shifters
- **Inrush protection:** RC snubber (10R + 1uF) across WiFi PA switch, 33uF hot-plug damping cap

### GaN PA Safety

The TGA2215-SM is a depletion-mode GaN device requiring -5V gate bias *before* drain voltage to prevent destructive Idss runaway:

1. **Enable:** BIAS_EN HIGH -> LM2776 generates -5V -> LM393 comparator confirms bias present (BIAS_OK HIGH) -> Q1 turns on drain power
2. **Disable:** Drain power OFF first -> 15ms POSCAP bleed delay -> charge pump OFF

### Thermal Failsafe

The ESP32 runs `failsafe.py` (MicroPython), continuously monitoring:
- **Temperature:** NTC thermistor on heatsink, shutdown at 85C, recovery at 80C
- **Battery voltage:** Resistive divider (100k/22k), cutoff at 13.0V, recovery at 13.5V
- **Sensor health:** 5 consecutive fault readings trigger permanent lockout
- **Watchdog:** 10-second hardware WDT resets system if firmware hangs

## PCB Specifications

| Parameter | Value |
|-----------|-------|
| Layers | 4 (F.Cu / GND / PWR / B.Cu) |
| Material | FR4, 0.062", 1oz Cu |
| Impedance | 50-ohm controlled (0.3mm RF traces) |
| Finish | ENIG |
| Board size | 120 x 90 mm |

### Net Classes

| Class | Trace | Clearance | Usage |
|-------|-------|-----------|-------|
| Default | 0.254mm | 0.2mm | General signals |
| RF_50ohm | 0.3mm | 0.3mm | RF signal paths |
| Power | 1.0mm | 0.3mm | Power distribution |
| HighPower | 2.54mm | 0.5mm | PA supply rails |

## Bill of Materials

See [`hardware/BOM.csv`](hardware/BOM.csv) for the full component list (~60 parts). Key components:

| Ref | Part | Function |
|-----|------|----------|
| U1 | M5StickC Plus 2 | ESP32 controller module |
| U4 | MAX2751 | GPS L1 VCO (1.575 GHz) |
| U5 | MAX2750 | WiFi VCO (2.4 GHz) |
| U6 | TGA2215-SM | GaN RF power amplifier (GPS) |
| U7 | ZVE-3W-83+ | 3W RF amplifier module (WiFi) |
| F1 | BFCN-1575+ | GPS L1 bandpass filter |
| F2 | BFCN-2440+ | WiFi bandpass filter |
| ISO1 | B1015 | GPS RF isolator |
| ISO2 | B2425 | WiFi RF isolator |

## Building

### Requirements

- [KiCad 9.0](https://www.kicad.org/) or later
- [MicroPython](https://micropython.org/) for ESP32 firmware

### Opening the Project

```bash
kicad hardware/jamrf-v2.kicad_pro
```

The project uses a custom symbol library (`jamrf-v2.kicad_sym`) included in the `hardware/` directory. Standard KiCad footprint libraries are referenced via `KICAD7_FOOTPRINT_DIR`.

### Flashing Firmware

```bash
# Connect M5StickC Plus 2 via USB
mpremote cp firmware/failsafe.py :main.py
```

## Known Limitations

- Component references are unannotated (`U?`, `R?`) — run KiCad Annotate Schematic before generating production files
- Custom footprint library (`jamrf-v2.pretty/`) not yet created — some components reference placeholder footprints
- ZVE-3W-83+ absolute max supply is +16V; a fully charged 4S LiPo (16.8V) exceeds this — consider a regulated supply stage for production

## Acknowledgments

This design draws architectural inspiration from the [HackRF One](https://github.com/greatscottgadgets/hackrf) by Great Scott Gadgets, licensed under CERN-OHL-P v2. JamRF v2 is an independent design using different components and signal chains.

## License

This project is licensed under the [CERN Open Hardware Licence Version 2 - Permissive](LICENSE) (CERN-OHL-P v2).
