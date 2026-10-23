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
- Transmitter, 40 x 100 mm, 4 layers: two AAA cells (Keystone 2468 holder), TPS63031 buck-boost to 3.3 V, slide switch, USB-C, ESP32-S3-WROOM-1 (native USB, so no USB-serial chip and no extra standby drain), RFM95W-915S2 with an SMA connector, six buttons wired to wake-up capable pins, one status LED.
- Receiver, 88 x 102 mm, 4 layers: 12 V screw terminal, PTC fuse, P-MOSFET reverse-polarity protection, SMBJ15A surge protection, TPS62933 converter to 3.3 V and a second TPS62933 to 4.0 V for the modem (2 A bursts, 330 uF polymer capacitor), ESP32-S3-WROOM-1, RFM95W-915S2 with SMA, W5500 Ethernet with HR911105A RJ45, SIM7600SA 4G modem (u.FL antenna, micro-SIM holder, TXB0104 level translator because the modem serial lines are 1.8 V), relay SRD-12VDC-SL-A with MMBT2222A driver and SS14 flyback diode. The lamp current path is 1.4 mm wide with no vias (sized for 3 A; the real lamp current was not in your requirements).

## Changes from my first plan, and why
- ESP32-S3 instead of ESP32-WROOM-32E: native USB removes the CH340C and its battery drain problem.
- 4 layers instead of 2: continuous ground under the 50 ohm antenna lines.
- Micro-SIM holder instead of nano: only a micro holder was available in the library I used. A nano SIM works with an adapter; tell me if you need a nano holder.
- Level translator added for the modem (found while reading the modem document).

## What was checked
- KiCad design rule check: 0 errors and 0 unconnected pads on both boards.
- Every pad compared with the netlist exported from the schematic: 0 mismatches.
- ngspice simulation of the relay driver and of the 12 V input protection (generic models, not the manufacturers' models).
- Trace widths of the lamp path checked against IPC-2221.
- Datasheets read for the MOSFET, TVS, resettable fuse, relay, Schottky diode, LDO, level translator, transistor, buck and buck-boost converters, Ethernet and LoRa chips (see `BELGELER.md`); this found and fixed the fuse suffix (16 V version required for a 12 V supply) and a wrong saturation-current note for the power inductors.
- Simulations (`simulasyon/SONUCLAR.md`): a 2 A modem current burst with the copper resistance taken from the board (modem supply stays above its 3.4 V minimum; 3.9 V in the typical case after raising the modem supply from 3.8 V to 4.0 V); transmitter battery life: about 2 years at 10-50 presses a day, 1.3 years at 200 a day (2 AAA alkaline, assumed capacity 1000 mAh); RF line impedance 43-53 ohm over stack-up tolerance; Ethernet pair skew 70-86 ps; crystal load shift about 4 ppm.

## Cost per set (one transmitter + one receiver, about 100 sets; `maliyet/MALIYET.md`)
About US$101: US$80 from distributor prices read during this work (modem 36.60, two RFM95W 31.52, two ESP32-S3 7.32, W5500, converter), the rest estimated. The modem and the two LoRa modules are two thirds of it.

## If you want the cost lower (each needs your approval; I adapt the files)
1. Ra-01H (SX1276, same chip as RFM95W, LCSC about US$4.4): about US$23 less per set. Pin table not yet checked.
2. A cheaper 4G Cat-1 module covering Chilean bands: not identified yet; needs a band and pin check. The modem is US$37 of the set.
3. Larger orders: price breaks (SIM7600SA US$47.31 at 1, US$36.60 at 100; RFM95W much cheaper per piece at 1000).
4. USB-only powering, power inductors with higher saturation current (SRP7028A-4R7M, larger footprint), and a low-loss diode for USB power are design improvements, not cost items.

## What I did not check and will not claim
- Radio range, antenna matching, cellular coverage: these need built boards and a field test.
- The modem pin table was compared with SIMCom's SIM7600 Series Hardware Design V1.08, which lists SA/SA-H among the covered models (87 pins; all 87 names and numbers match). That document has one common pin table, not an SA-only one, so please still confirm with the supplier before ordering.
- Part stock and LCSC numbers; the manufacturer documents of the USB protection array, the Ethernet connector and the Bourns inductor could not be downloaded (only distributor listings).
- Known weak points of the receiver layout: the W5500 crystal traces are long (about 28-32 mm) and the Ethernet pairs are not length matched. They should work but are the first things to look at on a prototype.

## Questions, with the defaults the files already use
1. Range: open field, line of sight. (No range figure can be guaranteed.)
2. Transmitter battery: two AAA alkaline cells, no charger.
3. Antennas: SMA for LoRa on both boards, u.FL for the cellular antenna.
4. Lamp: 12 V, 3 A assumed. Tell me the real current and I resize the traces.
5. Modem: SIM7600SA (Cat 1). If you need SIM7600SA-H (Cat 4), I adapt the files.
6. SIM: unlocked SIM from any Chilean carrier.
7. Ethernet and 4G: both present and independent.

I can adapt the files to your answers within 5 days of acceptance, at no extra charge.

Price: 333.33 USD.

Best regards,
[YOUR NAME]
