# JamRF v2 — Component Buy List

> **Supplier priority:** Turkish domestic suppliers (Direnc.net, Robotistan.com) first,
> then European distributors that ship to Türkiye (Mouser TR, Farnell TR, TME, RS Components TR).
> For specialty RF components (Mini-Circuits, Qorvo) the manufacturers' own stores or Mouser/DigiKey are used.

---

## Legend

| Symbol | Meaning |
|--------|---------|
| 🇹🇷 | Turkish domestic supplier (ships from within Turkey) |
| 🌍 | European distributor with Turkey shipping |
| 🌐 | Global supplier (manufacturer / international distributor) |

---

## Modules & Development Boards

### U1 — M5StickC Plus2 (ESP32-PICO-V3-02 controller)
| # | Supplier | Link | Notes |
|---|---------|------|-------|
| 1 | 🌐 M5Stack Official Store | [shop.m5stack.com — M5StickC PLUS2 ($19.95)](https://shop.m5stack.com/products/m5stickc-plus2-esp32-mini-iot-development-kit) | Ships worldwide from China |
| 2 | 🇹🇷 Robotistan.com | [robotistan.com — search "M5StickC Plus2"](https://www.robotistan.com/m5-stickc-plus2) | Check current stock; largest TR maker store |

### U2 — Pololu D24V10F5 (5V 1A Fixed Buck Converter Module)
| # | Supplier | Link | Notes |
|---|---------|------|-------|
| 1 | 🌐 Pololu Official | [pololu.com/product/2831](https://www.pololu.com/product/2831) | Ships internationally to Turkey |
| 2 | 🌍 TME (Transfer Multisort Elektronik) | [tme.eu — POLOLU-2831](https://www.tme.eu/en/details/pololu-2831/converter-modules/pololu/5v-1a-step-down-d24v10f5/) | EU warehouse, ships to Turkey |

### U_BOOST — Pololu U3V70F15 (15V Boost Regulator for WiFi PA)
| # | Supplier | Link | Notes |
|---|---------|------|-------|
| 1 | 🌐 Pololu Official | [pololu.com/product/2896](https://www.pololu.com/product/2896) | Ships internationally to Turkey |
| 2 | 🌍 TME | [tme.eu — search "U3V70F15"](https://www.tme.eu/en/search/?search=U3V70F15) | Check stock; TME carries Pololu modules |

---

## Power Connectors

### J1 — XT60 Battery Connector (4S LiPo, min 80C rating)
| # | Supplier | Link | Notes |
|---|---------|------|-------|
| 1 | 🇹🇷 Direnc.net | [direnc.net — XT60 60A LiPo Connector](https://www.direnc.net/xt60-plug-60a-li-po-konnektor) | Male+Female pair, ships from Turkey |
| 2 | 🇹🇷 Robotistan.com | [robotistan.com — XT60 Male Connector](https://www.robotistan.com/xt60-battery-male-connector) | Also see: [Female](https://www.robotistan.com/xt60-battery-female-connector-1) |

---

## RF SMA Connectors

### J2, J3 — SMA Edge-Mount Connector (50 Ω, PCB edge launch)
| # | Supplier | Link | Notes |
|---|---------|------|-------|
| 1 | 🇹🇷 Direnc.net | [direnc.net — SMA Female PCB Mount 50R 18GHz](https://www.direnc.net/sma-disi-pcb-dayanagi-konnektor-50r-18ghz-en) | SMD PCB mount 50Ω |
| 2 | 🌍 Mouser TR | [mouser.com.tr — SMA 50Ω Edge Launch](https://www.mouser.com.tr/c/connectors/rf-interconnects/rf-connectors-coaxial-connectors/?impedance=50+Ohms&maximum+frequency=18+GHz&mounting+style=Edge+Launch&rf+series=SMA) | Filter: Edge Launch, SMA, 50Ω |

---

## Protection & TVS

### D1 — SMAJ5.0A Unidirectional TVS Diode (5V, SMA package)
| # | Supplier | Link | Notes |
|---|---------|------|-------|
| 1 | 🇹🇷 Direnc.net | [direnc.net — SMAJ5.0A-E3/61T SMD Transil Diode](https://www.direnc.net/smaj50a-e3-61t-smd-transil-diyot-en) | Vishay brand, 400W, in stock (99k+ units) |
| 2 | 🌍 Mouser TR | [mouser.com.tr — search SMAJ5.0A](https://www.mouser.com.tr/Search/Refine?Keyword=SMAJ5.0A) | Littelfuse / Vishay variants available |

---

## Power Management ICs

### U3 — TPS7A4700RGWT (Ultra-Low Noise LDO, VQFN-20)
| # | Supplier | Link | Notes |
|---|---------|------|-------|
| 1 | 🌍 Mouser TR | [mouser.com.tr — TPS7A4700RGWT](https://www.mouser.com.tr/ProductDetail/Texas-Instruments/TPS7A4700RGWT) | Search: TPS7A4700RGWT; ships to Turkey |
| 2 | 🌐 DigiKey | [digikey.com — TPS7A4700RGWT](https://www.digikey.com/en/products/detail/texas-instruments/TPS7A4700RGWT/3516858) | Cut tape available, ships same day |

### U8 — LM2776 (Inverting Charge Pump, −5V, SOT-23-6)
| # | Supplier | Link | Notes |
|---|---------|------|-------|
| 1 | 🌍 Mouser TR | [mouser.com.tr — LM2776 TI page](https://www.mouser.com.tr/new/texas-instruments/ti-lm2776-converter/) | Texas Instruments LM2776; ships to Turkey |
| 2 | 🌐 DigiKey | [digikey.com — search LM2776](https://www.digikey.com/en/products/result?keywords=LM2776) | SOT-23-6 or SC-70-6 variants |

### U9 — LM393 (Dual Comparator, SOIC-8)
| # | Supplier | Link | Notes |
|---|---------|------|-------|
| 1 | 🇹🇷 Direnc.net | [direnc.net — LM393 SOIC-8 SMD (Onsemi)](https://www.direnc.net/lm393-soic-8-smd-komparator-entegresi-en) | 2,494 units in stock; ~1.41 TL |
| 2 | 🌍 Mouser TR | [mouser.com.tr — search LM393 SOIC-8](https://www.mouser.com.tr/Search/Refine?Keyword=LM393&Ns=Pricing%7C0) | Multiple brands available |

---

## RF Oscillators (VCOs)

### U4 — MAX2751EUA+ (GPS L1 1.575 GHz VCO, SOT-23-6)
| # | Supplier | Link | Notes |
|---|---------|------|-------|
| 1 | 🌍 Mouser TR | [mouser.com.tr — search MAX2751EUA+](https://www.mouser.com.tr/Search/Refine?Keyword=MAX2751) | Analog Devices (Maxim); verify SOT-23-6 variant |
| 2 | 🌐 DigiKey | [digikey.com — MAX2751](https://www.digikey.com/en/products/base-product/maxim-integrated/175/MAX2751/119046) | Select EUA+ (SOT-23-6) variant from page |

### U5 — MAX2750EUA+ (2.4 GHz ISM VCO, SOT-23-6)
| # | Supplier | Link | Notes |
|---|---------|------|-------|
| 1 | 🌐 Mouser | [mouser.com — MAX2750EUA+](https://www.mouser.com/ProductDetail/Maxim-Integrated/MAX2750EUA+?qs=GxOUx7aO6nziIWwKBH4Icg%3D%3D) | Same-day shipping available |
| 2 | 🌐 DigiKey | [digikey.com — MAX2750EUA+](https://www.digikey.com/en/products/detail/analog-devices-inc-maxim-integrated/MAX2750EUA/1512311) | ~$9.02/unit; ships same day |

---

## RF Bandpass Filters

### F1 — BFCN-1575+ (GPS L1 1.575 GHz LTCC BPF, FV1206)
| # | Supplier | Link | Notes |
|---|---------|------|-------|
| 1 | 🌐 Mini-Circuits Official | [minicircuits.com — BFCN-1575+](https://www.minicircuits.com/WebStore/dashboard.html?model=BFCN-1575) | Direct from manufacturer; global shipping |
| 2 | 🌍 Mouser TR | [mouser.com.tr — search BFCN-1575+](https://www.mouser.com.tr/Search/Refine?Keyword=BFCN-1575%2B) | Mini-Circuits authorized distributor |

### F2 — BFCN-2440+ (2.44 GHz LTCC BPF, FV1206)
| # | Supplier | Link | Notes |
|---|---------|------|-------|
| 1 | 🌐 Mini-Circuits Official | [minicircuits.com — BFCN-2440+](https://www.minicircuits.com/WebStore/dashboard.html?model=BFCN-2440+) | Direct from manufacturer |
| 2 | 🌍 Mouser TR | [mouser.com.tr — search BFCN-2440+](https://www.mouser.com.tr/Search/Refine?Keyword=BFCN-2440%2B) | Check Mini-Circuits stock at Mouser |

---

## RF Amplifiers

### U6 — TGA2215-SM (Qorvo GaN PA, GPS L1, QFN-32)
> ⚠️ **Controlled component** — requires end-user statement. GaN on SiC depletion-mode device.
> This part may need to be ordered directly from Qorvo or via an authorized distributor with export documentation.

| # | Supplier | Link | Notes |
|---|---------|------|-------|
| 1 | 🌐 Mouser | [mouser.com — search TGA2215-SM](https://www.mouser.com/Search/Refine?Keyword=TGA2215-SM) | Qorvo authorized distributor |
| 2 | 🌐 DigiKey | [digikey.com — search TGA2215-SM](https://www.digikey.com/en/products/result?keywords=TGA2215-SM) | Contact Qorvo if not listed |

### U7 — ZVE-3W-83+ (Mini-Circuits WiFi PA, 2–8 GHz, 3W connectorized)
| # | Supplier | Link | Notes |
|---|---------|------|-------|
| 1 | 🌐 Mini-Circuits Official | [minicircuits.com — ZVE-3W-83+](https://www.minicircuits.com/WebStore/dashboard.html?model=ZVE-3W-83+) | Connectorized SMA module, direct buy |
| 2 | 🌐 Mouser | [mouser.com — ZVE-3W-83+](https://www.mouser.com/ProductDetail/Mini-Circuits/ZVE-3W-83+?qs=IPgv5n7u5QY6glWktaGMIw%3D%3D) | Same-day shipping |
| 3 | 🌐 DigiKey | [digikey.com — ZVE-3W-83+](https://www.digikey.com/en/products/detail/mini-circuits/ZVE-3W-83/20526845) | Ships today |

---

## RF Isolators

### ISO1 — Mini-Circuits B1015 (Drop-In Isolator, ~1.575 GHz)
| # | Supplier | Link | Notes |
|---|---------|------|-------|
| 1 | 🌐 Mini-Circuits Official | [minicircuits.com — model search B1015](https://www.minicircuits.com/WebStore/modelSearch.html?model=B1015&search=1) | Contact sales if not listed online |
| 2 | 🌍 Mouser TR | [mouser.com.tr — Mini-Circuits RF Isolators](https://www.mouser.com.tr/c/rf-wireless/rf-integrated-circuits/rf-isolators/?m=Mini-Circuits) | Browse or search "B1015" |

### ISO2 — Mini-Circuits B2425 (Drop-In Isolator, 2.4 GHz)
| # | Supplier | Link | Notes |
|---|---------|------|-------|
| 1 | 🌐 Mini-Circuits Official | [minicircuits.com — model search B2425](https://www.minicircuits.com/WebStore/modelSearch.html?model=B2425&search=1) | Contact sales if not listed online |
| 2 | 🌍 Mouser TR | [mouser.com.tr — Mini-Circuits RF Isolators](https://www.mouser.com.tr/c/rf-wireless/rf-integrated-circuits/rf-isolators/?m=Mini-Circuits) | Browse or search "B2425" |

---

## MOSFETs

### Q1, Q2 — SQJ407EP-T1_GE3 (P-Channel 60V 10A, PowerPAK SO-8)
| # | Supplier | Link | Notes |
|---|---------|------|-------|
| 1 | 🌍 Mouser TR | [mouser.com.tr — search SQJ407EP](https://www.mouser.com.tr/Search/Refine?Keyword=SQJ407EP) | Vishay Siliconix; ships to Turkey |
| 2 | 🌐 DigiKey | [digikey.com — search SQJ407EP](https://www.digikey.com/en/products/result?keywords=SQJ407EP) | ~$1.55/unit |

### Q_N1, Q3 — 2N7002 (N-Channel 60V 300mA, SOT-23)
| # | Supplier | Link | Notes |
|---|---------|------|-------|
| 1 | 🇹🇷 Direnc.net | [direnc.net — 2N7002 SOT-23 60V 250mA](https://www.direnc.net/2n7002-n-kanal-mosfet-sot-23-smd-60v-250ma) | Panjit brand; 99,999 units in stock |
| 2 | 🌐 DigiKey | [digikey.com — 2N7002 (Onsemi)](https://www.digikey.com/en/products/detail/onsemi/2N7002/244345) | Ships same day |

---

## Capacitors

> All Murata GRM series MLCC capacitors can be found at **TME** and **Mouser TR**.
> Search by exact part number (e.g. `GRM21BR61E106KA73L`) on these sites.

### Bulk Capacitors (by part number)

| Ref | Part Number | Value | Package | TME Link | Mouser TR |
|-----|------------|-------|---------|----------|-----------|
| C_IN1, C_LDO_IN, C_GaN_BULK | GRM21BR61E106KA73L | 10µF 25V X5R | 0805 | [tme.eu search](https://www.tme.eu/en/search/?search=GRM21BR61E106KA73L) | [mouser.com.tr search](https://www.mouser.com.tr/Search/Refine?Keyword=GRM21BR61E106KA73L) |
| C_IN2, C_GaN_HF | GRM188R71E104KA01D | 100nF 25V X7R | 0603 | [tme.eu search](https://www.tme.eu/en/search/?search=GRM188R71E104KA01D) | [mouser.com.tr search](https://www.mouser.com.tr/Search/Refine?Keyword=GRM188R71E104KA01D) |
| C_LDO_OUT | GRM21BR61C106KE15L | 10µF 16V X5R | 0805 | [tme.eu search](https://www.tme.eu/en/search/?search=GRM21BR61C106KE15L) | [mouser.com.tr search](https://www.mouser.com.tr/Search/Refine?Keyword=GRM21BR61C106KE15L) |
| C_NR, C_FLY | GRM155R71C105KA12D | 1µF 16V X7R | 0402 | [tme.eu search](https://www.tme.eu/en/search/?search=GRM155R71C105KA12D) | [mouser.com.tr search](https://www.mouser.com.tr/Search/Refine?Keyword=GRM155R71C105KA12D) |
| C_VCO1, C_VCO2 | GRM155R71C104KA88D | 100nF 16V X7R | 0402 | [tme.eu search](https://www.tme.eu/en/search/?search=GRM155R71C104KA88D) | [mouser.com.tr search](https://www.mouser.com.tr/Search/Refine?Keyword=GRM155R71C104KA88D) |
| C_SNUB | GRM188R71E105KA12D | 1µF 25V X7R | 0603 | [tme.eu search](https://www.tme.eu/en/search/?search=GRM188R71E105KA12D) | [mouser.com.tr search](https://www.mouser.com.tr/Search/Refine?Keyword=GRM188R71E105KA12D) |
| C_BULK_IN | GRM32ER71H336KE15L | 33µF 50V X7R | 1210 | [tme.eu search](https://www.tme.eu/en/search/?search=GRM32ER71H336KE15L) | [mouser.com.tr search](https://www.mouser.com.tr/Search/Refine?Keyword=GRM32ER71H336KE15L) |
| C_CP_OUT | GRM21BR61A106KE19L | 10µF 10V X5R | 0805 | [tme.eu search](https://www.tme.eu/en/search/?search=GRM21BR61A106KE19L) | [mouser.com.tr search](https://www.mouser.com.tr/Search/Refine?Keyword=GRM21BR61A106KE19L) |
| C_CP_IN | GRM155R71A105KE01D | 1µF 10V X5R | 0402 | [tme.eu search](https://www.tme.eu/en/search/?search=GRM155R71A105KE01D) | [mouser.com.tr search](https://www.mouser.com.tr/Search/Refine?Keyword=GRM155R71A105KE01D) |
| C_COMP | GRM155R71A104KA01D | 100nF 10V X7R | 0402 | [tme.eu search](https://www.tme.eu/en/search/?search=GRM155R71A104KA01D) | [mouser.com.tr search](https://www.mouser.com.tr/Search/Refine?Keyword=GRM155R71A104KA01D) |

### C1–C4 — Panasonic 25TQC100MYF (100µF 25V POSCAP-D)
| # | Supplier | Link | Notes |
|---|---------|------|-------|
| 1 | 🌍 Mouser TR | [mouser.com.tr — Panasonic TQC POSCAP series](https://eu.mouser.com/new/panasonic/panasonic-tqc-conductive-poscap/) | Search "25TQC100MYF" or "100uF 25V TQC" |
| 2 | 🌐 DigiKey | [digikey.com — search 25TQC100MYF](https://www.digikey.com/en/products/result?keywords=25TQC100MYF) | Also check 20TQC100MYF (20V variant as fallback) |

---

## Resistors

> All Vishay CRCW0603 series 1% resistors. Best ordered from Mouser TR or TME.
> TME URL format: `https://www.tme.eu/en/search/?search=<PART_NUMBER>`

### Vishay CRCW0603 Resistor Summary

| Ref(s) | Part Number | Value | Supplier 1 (Mouser TR) | Supplier 2 (TME) |
|--------|------------|-------|----------------------|-----------------|
| R1, R3, R4, R6 | CRCW0603292RFKTA | 292Ω 1% | [mouser.com.tr — CRCW0603292RFKTA](https://www.mouser.com.tr/Search/Refine?Keyword=CRCW0603292RFKTA) | [tme.eu — CRCW0603292RFKTA](https://www.tme.eu/en/search/?search=CRCW0603292RFKTA) |
| R2, R5 | CRCW060318R0FKTA | 18Ω 1% | [mouser.com.tr — CRCW060318R0FKTA](https://www.mouser.com.tr/Search/Refine?Keyword=CRCW060318R0FKTA) | [tme.eu — CRCW060318R0FKTA](https://www.tme.eu/en/search/?search=CRCW060318R0FKTA) |
| R_SNUB | CRCW060310R0FKTA | 10Ω 1% | [mouser.com.tr — CRCW060310R0FKTA](https://www.mouser.com.tr/Search/Refine?Keyword=CRCW060310R0FKTA) | [tme.eu — CRCW060310R0FKTA](https://www.tme.eu/en/search/?search=CRCW060310R0FKTA) |
| R_PU, R_TH | CRCW060310K0FKTA | 10kΩ 1% | [mouser.com.tr — CRCW060310K0FKTA](https://www.mouser.com.tr/Search/Refine?Keyword=CRCW060310K0FKTA) | [tme.eu — CRCW060310K0FKTA](https://www.tme.eu/en/search/?search=CRCW060310K0FKTA) |
| R_G1, R_Q2_PU, R_DIV1, R_REF1, R_BATT1 | CRCW0603100KFKTA | 100kΩ 1% | [mouser.com.tr — CRCW0603100KFKTA](https://www.mouser.com.tr/Search/Refine?Keyword=CRCW0603100KFKTA) | [tme.eu — CRCW0603100KFKTA](https://www.tme.eu/en/search/?search=CRCW0603100KFKTA) |
| R_DIV2 | CRCW0603270KFKTA | 270kΩ 1% | [mouser.com.tr — CRCW0603270KFKTA](https://www.mouser.com.tr/Search/Refine?Keyword=CRCW0603270KFKTA) | [tme.eu — CRCW0603270KFKTA](https://www.tme.eu/en/search/?search=CRCW0603270KFKTA) |
| R_REF2 | CRCW060382K0FKTA | 82kΩ 1% | [mouser.com.tr — CRCW060382K0FKTA](https://www.mouser.com.tr/Search/Refine?Keyword=CRCW060382K0FKTA) | [tme.eu — CRCW060382K0FKTA](https://www.tme.eu/en/search/?search=CRCW060382K0FKTA) |
| R_BATT2 | CRCW060322K0FKTA | 22kΩ 1% | [mouser.com.tr — CRCW060322K0FKTA](https://www.mouser.com.tr/Search/Refine?Keyword=CRCW060322K0FKTA) | [tme.eu — CRCW060322K0FKTA](https://www.tme.eu/en/search/?search=CRCW060322K0FKTA) |

> **Tip:** If exact Vishay CRCW part numbers are out of stock, any 0603 1% thick-film 100mW resistor in the correct value is a valid substitute (e.g., Yageo RC0603FR series, Panasonic ERA series).

---

## Thermistor

### TH1 — NTCS0805E3103FMT (Vishay 10kΩ NTC, 0805, B=3570K)
| # | Supplier | Link | Notes |
|---|---------|------|-------|
| 1 | 🌐 DigiKey | [digikey.com — NTCS0805E3103FMT](https://www.digikey.com/en/products/detail/vishay-beyschlag-draloric-bc-components/NTCS0805E3103FMT/2237367) | Ships today; ±1% tolerance |
| 2 | 🌍 TME | [tme.eu — NTCS0805E3103FMT](https://www.tme.eu/en/details/ntcs0805e3103fmt/smd-measurement-ntc-thermistors/vishay/) | EU warehouse, ships to Turkey |

---

## RF Shield Cans

### SH1, SH2 — Würth Elektronik 36103305 (SMD Shield Can)
| # | Supplier | Link | Notes |
|---|---------|------|-------|
| 1 | 🌍 Mouser TR | [mouser.com.tr — Wurth 36103305](https://www.mouser.com/ProductDetail/Wurth-Elektronik/36103305?qs=c50eh9DPO4O7TwWEHqYVOw%3D%3D) | Frame + cover; ~$3.91 per set |
| 2 | 🌐 DigiKey | [digikey.com — search 36103305](https://www.digikey.com/en/products/result?keywords=36103305) | ~$4.34; also see 36103305S (frame only) |

---

## Purchasing Tips

### For Turkish buyers
1. **Direnc.net** and **Robotistan.com** cover common passives, connectors, and discrete transistors at low cost with fast domestic shipping.
2. **Mouser TR (`mouser.com.tr`)** is fully stocked and ships from a local Turkish warehouse — best for ICs and specialty passives at volume.
3. **TME (`tme.eu`)** is a Polish distributor but ships to Turkey via DHL/UPS; excellent for Murata/Vishay passives and Pololu modules.
4. **Farnell TR (`tr.farnell.com`)** and **RS Components TR (`tr.rs-online.com`)** are also authorized distributors with Turkish offices.

### Hard-to-find components
| Component | Notes |
|-----------|-------|
| **TGA2215-SM** (Qorvo GaN PA) | Niche RF part; check Mouser/DigiKey. If unavailable, contact [Qorvo sales](https://www.qorvo.com/contact) directly. ECCN classification may require export documentation. |
| **B1015 / B2425** (Mini-Circuits Drop-In Isolators) | Legacy drop-in format; contact [Mini-Circuits sales](https://www.minicircuits.com/contact/) if not listed on web store. |
| **MAX2751 / MAX2750** | Older Maxim VCOs; check Mouser/DigiKey stock. May need to request from Analog Devices (ADI) directly. |

---

*Last updated: 2026-03-23*
