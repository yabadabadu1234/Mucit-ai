# Teklif (İngilizce, ilana gönderilecek metin) -- "ürününüz hazır" sürümü

Kısa sürüm `teklif_kisa.txt` dosyasındadır. Bu dosya aynı teklifin ayrıntılı hâlidir. Fiyat: 333,33 USD (önceki taslaktaki 300 USD yerine; ilandaki teklif tutarıyla aynı olmalıdır, göndermeden önce kontrol edilecek).

---

Hello,

Your product is ready. Both designs are finished. I send the complete files as soon as you accept. No firmware, as you asked.

## What you receive (for each board)
- KiCad sources: schematic and PCB
- Gerber files (4 copper layers, mask, paste, silkscreen, board edge), drill files, zipped for PCBWay / JLCPCB
- Bill of materials (CSV) and pick-and-place file (CSV)
- PDFs of the schematic and of the board (front and back)
- A short design note: pin map, power budget, known weak points

## The two boards
- Transmitter, 40 x 100 mm, 4 layers: two AAA cells (Keystone 2468 holder), TPS63031 buck-boost to 3.3 V, slide switch, USB-C, ESP32-S3-WROOM-1 (native USB, so no USB-serial chip and no extra standby drain), Ra-01H SX1276 LoRa module (915 MHz) with an SMA connector, six buttons wired to wake-up capable pins, one status LED.
- Receiver, 88 x 102 mm, 4 layers: 12 V screw terminal, PTC fuse, P-MOSFET reverse-polarity protection, SMBJ15A surge protection, TPS62933 converter to 3.3 V and a second TPS62933 to 4.0 V for the modem (2.8 A bursts, 330 uF polymer capacitor), ESP32-S3-WROOM-1, Ra-01H LoRa with SMA, W5500 Ethernet with HR911105A RJ45, SIMCom A7670SA LTE Cat-1 modem (u.FL antenna, micro-SIM holder, ESD protection on PWRKEY/RESET and SIM lines, TXB0104 level translator because the modem serial lines are 1.8 V), LM66100 ideal diode on the USB power path, relay SRD-12VDC-SL-A with MMBT2222A driver and SS14 flyback diode. The lamp current path is 0.8 mm wide (about 2 A at 10 C rise; the real lamp current was not in your requirements).

## Changes from my first plan, and why
- ESP32-S3 instead of ESP32-WROOM-32E: native USB removes the CH340C and its battery drain problem.
- 4 layers instead of 2: continuous ground under the 50 ohm antenna lines.
- Micro-SIM holder instead of nano: only a micro holder was available in the library I used. A nano SIM works with an adapter; tell me if you need a nano holder.
- Level translator added for the modem (found while reading the modem document).
- A7670SA instead of SIM7600SA and Ra-01H instead of RFM95W: same function, much cheaper (see cost). The A7670SA datasheet lists LTE B1/2/3/4/5/7/8/28/66 and GSM 850/900/1800/1900, which includes the Chilean bands (B28, B7, B4, B2, B66, B5; carrier lists are from 2016-2021 sources I could not verify with the carriers).
- LM66100 ideal diode on the USB path, so the 3.3 V rail no longer sags to about 2.9 V when only USB is plugged in; ESD arrays and 22 ohm resistors on the SIM and PWRKEY/RESET lines, as SIMCom recommends.

## What was checked
- KiCad design rule check: 0 errors and 0 unconnected pads on both boards.
- Every pad compared with the netlist exported from the schematic: 0 mismatches (565 pads on the receiver).
- ngspice simulation of the relay driver and of the 12 V input protection (generic models, not the manufacturers' models).
- Trace widths of the lamp path checked against IPC-2221.
- Datasheets read for the MOSFET, TVS, resettable fuse, relay, Schottky diode, LDO, level translator, transistor, buck and buck-boost converters, Ethernet and LoRa chips (see `BELGELER.md`); this found and fixed the fuse suffix (16 V version required for a 12 V supply) and a wrong saturation-current note for the power inductors.
- Simulations (`simulasyon/SONUCLAR.md`): a 2.8 A modem current burst with the copper resistance taken from the board (18-19 mOhm to the modem pads): the modem pins stay at 3.83 V if the converter's control loop is 40 kHz fast and 3.54 V at 20 kHz, but would fall to 2.9 V at 10 kHz (minimum 3.4 V). The loop bandwidth is not in the datasheet, so this is the first thing I would measure on a prototype; transmitter battery life: about 2 years at 10-50 presses a day, 1.3 years at 200 a day (2 AAA alkaline, assumed capacity 1000 mAh, Ra-01H at 97 mA transmit); RF line impedance 43-53 ohm over stack-up tolerance; Ethernet pair skew 12-17 ps; crystal load shift about 2 ppm.

## Cost per set (one transmitter + one receiver, about 100 sets; `maliyet/MALIYET.md`)
About US$49: US$31 from LCSC prices read during this work (two Ra-01H 9.30, A7670SA modem 8.88, two ESP32-S3 6.72, W5500 and converters), the rest (PCB, assembly, passives, connectors, US$18) estimated. The previous SIM7600SA + RFM95W version was about US$101.

## If you want the cost lower or the supplier different (I adapt the files)
1. A different 4G module or LoRa module from a supplier you prefer.
2. Larger orders: price breaks (A7670SA US$9.10 at 1, US$8.88 at 10+ for the LASE variant).
3. The cheaper A7670SA-LASC variant (US$6.97): same band list in SIMCom's documents, but the suffix difference is not documented; I would ask the supplier first.

## What I did not check and will not claim
- Radio range, antenna matching, cellular coverage: these need built boards and a field test.
- The modem footprint and symbol come from SIMCom's A7670 Series Hardware Design (88 pads, Figures 2 and 4). The suffixes LASC/LASE/FASE/MASC are not explained in SIMCom's documents, so please confirm the variant and its stock with the supplier before ordering (LCSC showed 1 piece of LASE and 97 of LASC, fewer than 100 sets need).
- The Ra-01H pad drawing is taken from the Ra-01 manual (same 17 x 16 mm body and pin count); the Ra-01H document has no dimension drawing. I will confirm it with Ai-Thinker before fabrication.
- Part stock and LCSC numbers; the manufacturer documents of the USB protection array, the Ethernet connector and the Bourns inductor could not be downloaded (only distributor listings).
- Known weak points of the receiver layout: the W5500 crystal traces are 19-21 mm, the Ethernet pairs differ by 2-3 mm, the modem supply trace is 1.0 mm on part of its length (SIMCom asks for 2 mm; the computed resistance is 18-19 mOhm). They should work but are the first things to look at on a prototype.

## Questions, with the defaults the files already use
1. Range: open field, line of sight. (No range figure can be guaranteed.)
2. Transmitter battery: two AAA alkaline cells, no charger.
3. Antennas: SMA for LoRa on both boards, u.FL for the cellular antenna.
4. Lamp: 12 V, 3 A assumed. Tell me the real current and I resize the traces.
5. Modem: A7670SA (LTE Cat 1). If you need Cat 4 or another module, I adapt the files.
6. SIM: unlocked SIM from any Chilean carrier.
7. Ethernet and 4G: both present and independent.

I can adapt the files to your answers within 5 days of acceptance, at no extra charge.

Price: 333.33 USD.

Best regards,
[YOUR NAME]
