# Transmitter – design note

Status: schematic, 4-layer PCB (40 x 100 mm), Gerber/drill, BOM, placement files. KiCad DRC: 0 errors (2 warnings: library-footprint difference, one dangling ground via). Connectivity checked against the exported netlist (0 unconnected). KiCad 7 CLI has no ERC; the schematic was checked by netlist comparison only.

## Changes from the offer text (necessity)
- MCU is ESP32-S3-WROOM-1-N4 (native USB): removes the USB-UART chip, its idle drain and back-power problem on a battery device. Bootloader: hold button 1 (IO0) while plugging USB.
- 4-layer board (GND plane under the 0.40 mm RF line; width computed for a ~0.21 mm prepreg, must be confirmed with the fabricator's stack-up).
- No mounting holes on the right side (battery holder occupies it); two holes on the left edge only.

## ESP32-S3 pins
Buttons 1-6: IO0, IO4, IO2, IO5, IO1, IO6 (all wake-capable, 100k pull-ups to 3V3, pressed = low). Status LED: IO7. Ra-01H: SCK IO12, MISO IO13, MOSI IO11, NSS IO10, RESET IO14, DIO0 IO8, DIO1 IO9. USB D- IO19, D+ IO20.

## Power (estimates, not measurements)
Standby: ESP32-S3 deep sleep ~8 uA (datasheet), TPS63031 quiescent 25-35 uA + 4-6 uA (datasheet), SX1276 sleep ~0.2 uA (chip value; the Ra-01H document gives no sleep current) -> about 40-50 uA. Two AAA alkaline (~900 mAh usable, assumption) -> roughly 2 years standby; with 100 presses/day about 1.5-2 years. Real figures need a bench measurement.

## LoRa module
Ai-Thinker Ra-01H (SX1276, 803-930 MHz) replaces the RFM95W. Its document gives 97 mA average transmit current at 915 MHz, 12 mA receive; battery simulation was rerun with 97 mA (`simulasyon/verici_pil_omru.py`): about 2.0-2.4 years at 10-50 presses a day, 1.3 years at 200. The footprint uses the pad drawing of the same-size Ra-01 manual (the Ra-01H document has none); confirm with Ai-Thinker before fabrication.

## Not verified
Radio range, antenna matching, USB signal quality, LCSC stock/part numbers, 3D models. Footprint of the slide switch is the closest library part to MSK12C02.
