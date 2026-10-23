# Receiver – design note

Status: schematic, 4-layer PCB (88 x 102 mm), Gerber/drill, BOM, placement files, PDFs in `uretim_dosyalari/`. KiCad DRC: 0 errors, 0 unconnected pads (warnings only: silkscreen overlaps, library-footprint differences, a few dangling stubs and one via drilled in a through-hole pad). All 531 pads were compared with the exported netlist (`alici.xml`): 0 mismatches. KiCad 7 CLI has no ERC; the schematic was checked by netlist comparison only.

## Changes from the offer text (necessity)
- MCU is ESP32-S3-WROOM-1-N4 (native USB): no USB-UART chip.
- 4-layer board: GND plane (In1), +3V3 plane (In2), 50 ohm RF lines on the outer layers.
- A TXB0104 level translator was added: the SIM7600 serial interface is 1.8 V. Unused channel 4 (A4/B4) is tied to GND.
- Micro-SIM holder (JAE SF53S006VCBR2000) instead of nano: only micro was in the symbol/footprint library used.

## Pin map (ESP32-S3-WROOM-1-N4)
Shared SPI: SCK IO12, MOSI IO11, MISO IO13. RFM95W: NSS IO10, RESET IO14, DIO0 IO8, DIO1 IO15. W5500: CS IO9, INT IO16, RST IO17. Modem UART (through TXB0104, modem side 1.8 V): host TX IO4, host RX IO5, STATUS IO1, PWRKEY driver IO6, RESET driver IO7, modem supply enable IO2. Relay driver IO38, LEDs IO39/IO40, button IO0 (also boot), USB D- IO19, D+ IO20.

## Power chain
12 V screw terminal -> 2 A PTC -> P-MOSFET reverse protection (gate 10 V zener) -> 15 V TVS -> TPS62933 to 3.3 V (31.6k/10k divider) and TPS62933 to 3.8 V for the modem (37.4k/10k, enable by IO2, 330 uF polymer + 2x22 uF, 5.1 V zener). USB 5 V only feeds an AP2112K-3.3 through a Schottky (programming without 12 V). Relay: SRD-12VDC-SL-A, contacts take 12 V from the terminal before the fuse and MOSFET; coil driver NPN with 10k pull-down so the relay stays off at boot.

## Simulation (ngspice, generic models, see simulasyon/)
Relay driver: coil 29.8 mA, Vce(sat) 62 mV, flyback peak 12.2 V. Input protection: normal 1 A -> 0.30 V total drop; -12 V reverse -> output -0.08 V; 36 V surge through 2 ohm -> output clamped at 20.3 V.

## Layout / routing facts (measured on the board file)
- Lamp path (+12V_IN, LAMBA_SW): 1.4 mm wide, no vias, outer copper. IPC-2221 for 3 A at 10 C rise needs about 1.37 mm. The 3 A lamp current is an assumption.
- Modem supply (VBAT_MOD): 0.7 mm, 4 vias on the path. Peak 2 A is short; the vias have not been checked against a current rating [unverified].
- RF lines: 0.40 mm (50 ohm only if the real prepreg is about 0.21 mm; ask the fabricator).
- Routing was done with Freerouting plus a custom grid router (`uretim/izgara.py`). Three nets (ETH_CS, SPI_MISO, XO) use a few segments on In2.Cu, which is otherwise the +3V3 plane.

## Known weaknesses (not fixed)
- W5500 crystal lines are long: XI about 28 mm, XO about 32 mm (datasheet advice: short). The crystal sits about 15 mm from the chip. It will probably work but is the first thing to check on a prototype.
- Ethernet pairs are not length matched: TD_P 35 mm vs TD_N 21 mm, RD_P 24 mm vs RD_N 12 mm.
- Modem pin table: compared by script with SIMCom SIM7600 Series Hardware Design V1.08 Table 3 (the document lists SA and SA-H, Table 1): all 87 pin numbers and names match the symbol (pin 85 is called USB_BOOT there, BOOT_CFG0 in our symbol; only a name). Pad row order and the 4.5 mm corner offset match Figures 2-4. The document has one common pin table, not an SA-only one. Pad width/length were not stated in it; not verified.
- Modem target market: Chile. The SA band list (FDD B1/2/3/4/5/7/8/28/66, TDD B40, from SIMCom's product brief) contains the bands that search results give for Chilean carriers (B28, B7, B4; dated 2016-2021 sources, not verified with the carriers).
- Differences from SIMCom's recommendations (V1.08 sec. 3.1, 3.2, 3.5; reference design V1.02): VBAT trace is 0.7 mm (they say wider than 2 mm; about 67 mm of 0.7 mm segments in total including branches, 4 vias; drop at 2 A not measured, rough estimate a few tens of millivolts against their 300 mV budget); no ESD diode on PWRKEY/RESET (they strongly recommend one); no 22 ohm series resistors on USIM lines (reference design has them); USB_VBUS (pin 11) not wired, so the modem USB cannot be used for firmware update (only test points DN/DP). 330 uF polymer capacitor and 5.1 V zener on VBAT match their advice.
- UART level shifter uses VDD_1V8 (pin 15, 1.8 V, 50 mA max), as in their reference design.
- Not verified: radio range, cellular coverage, antenna matching, stock and LCSC numbers, datasheets of AO3401A, SMBJ15A, 1812L200, HR911105A, AP2112K, SRD relay, SS14, USBLC6, TXB0104 and inductor saturation currents.
- Four-layer stack-up is an assumption; confirm with the fabricator.
