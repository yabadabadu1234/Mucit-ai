# Receiver – design note

Status: schematic, 4-layer PCB (88 x 102 mm), Gerber/drill, BOM, placement files, PDFs in `uretim_dosyalari/`. KiCad DRC: 0 errors, 0 unconnected pads (warnings only: silkscreen overlaps, library-footprint differences, a few dangling stubs). All 565 pads were compared with the exported netlist (`alici.xml`): 0 mismatches. KiCad 7 CLI has no ERC; the schematic was checked by netlist comparison only.

## Parts changed in this revision (and why)
- Modem: SIMCom A7670SA (LTE Cat 1, 24 x 24 mm LGA, 88 pads) instead of SIM7600SA. Datasheet band list: LTE-FDD B1/2/3/4/5/7/8/28/66 plus GSM 850/900/1800/1900, which contains the Chilean bands (B28, B7, B4, B2, B66, B5). The suffix (LASC / LASE / FASE / MASC) is not explained in SIMCom's documents; the BOM names A7670SA-LASE (no GNSS/BT needed). Ask the supplier in writing before ordering. LCSC stock seen: LASE 1, LASC 97 (below the 100 sets you need).
- LoRa: Ai-Thinker Ra-01H (SX1276, 803-930 MHz, 16 half-hole pads) instead of RFM95W. Pad geometry is taken from the Ra-01/Ra-02 manual (same 17 x 16 mm body, same 16 pins); the Ra-01H document has no dimension drawing. Confirm with Ai-Thinker before fabrication.
- Power inductors: Bourns SRP7028A-4R7M (Isat about 10 A) after the first inductor turned out too weak for the modem burst.
- USB-only power path: LM66100 ideal diode instead of the Schottky, so +3V3 no longer drops to about 2.9 V when only USB is plugged in.
- ESD: USBLC6-2SC6 on PWRKEY/RESET and on the SIM lines; 22 ohm series resistors on the three SIM signals; test points for USB_BOOT, VDD_1V8, log UART and USB D+/D-/VBUS.

## Pin map (ESP32-S3-WROOM-1-N4)
Shared SPI: SCK IO12, MOSI IO11, MISO IO13. Ra-01H: NSS IO10, RESET IO14, DIO0 IO8, DIO1 IO15. W5500: CS IO9, INT IO16, RST IO17. Modem UART (through TXB0104, modem side 1.8 V): host TX IO4, host RX IO5, STATUS IO1, PWRKEY driver IO6, RESET driver IO7, modem supply enable IO2. Relay driver IO38, LEDs IO39/IO40, button IO0 (also boot), USB D- IO19, D+ IO20.

## Power chain
12 V screw terminal -> 2 A PTC -> P-MOSFET reverse protection -> 15 V TVS -> TPS62933 to 3.3 V and TPS62933 to 4.0 V for the modem (enable by IO2, 330 uF polymer with ESR at most 40 mOhm + 2 x 22 uF + 10 uF). A7670SA supply range 3.4-4.2 V. USB 5 V only feeds the AP2112K-3.3 through the LM66100 (programming without 12 V). Relay SRD-12VDC-SL-A; coil driver NPN with 10k pull-down so the relay stays off at boot.

## Simulation (ngspice and scripts in simulasyon/; see SONUCLAR.md)
- Relay driver and input protection: unchanged from the previous revision.
- Modem burst (2.8 A for 577 us at 216 Hz) with copper resistance taken from the board (L2 to the modem pads about 18.5 mOhm): the modem pins stay at 3.83 V if the TPS62933 loop bandwidth is 40 kHz and 3.54 V at 20 kHz, but fall to 2.9 V at 10 kHz (below the 3.4 V minimum). The loop bandwidth is an assumption, not a datasheet value, so this is the first thing to measure on a prototype.

## Layout / routing facts (measured on the board file)
- +12V_IN and LAMBA_SW: 0.8 mm outer copper, enough for about 2 A at 10 C rise (IPC-2221). The lamp current is not in your requirements; tell me the real value if it is above 2 A.
- VBAT_MOD: 1.0 mm on 41 mm of the path, 0.4 mm on 43 mm, 3 vias. Resistance from the buck inductor to the modem pads: 18-19 mOhm (computed from the track geometry). SIMCom asks for at least 2 mm.
- RF lines: 0.40 mm on the outer layer, 50 ohm only if the real prepreg is about 0.21 mm (ask the fabricator). The modem antenna line is also 0.40 mm now.
- Routing: Freerouting plus a custom grid router (`uretim/izgara.py`) and manual fixes; some nets use In2.Cu segments, which is otherwise the +3V3 plane.

## Known weaknesses (not fixed)
- W5500 crystal lines: XI 19.5 mm, XO 20.9 mm (WIZnet advises short). Estimated load shift about 2 ppm; first thing to check on a prototype.
- Ethernet pairs are not length matched: TX pair differs by 2.1 mm, RX pair by 2.8 mm (about 12 and 17 ps against an 8000 ps symbol). Which board segments form each pair was read from the net names, not from the schematic.
- Footprint of the A7670SA comes from Figures 2 and 4 of SIMCom's hardware design (outer pads 0.6 x 0.8 mm, 1.0 mm pitch, inner ground pads 2.1 x 2.1 mm); the two "forbidden area" squares are kept free of copper on the top layer.
- UART level shifter uses VDD_1V8 as in SIMCom's reference design.
- Not verified: radio range, cellular coverage, antenna matching, stock (see above) and datasheets of AO3401A, SMBJ15A, 1812L200, HR911105A, SRD relay and the SIM holder.
- Four-layer stack-up is an assumption; confirm with the fabricator.
