# Teklif taslağı (İngilizce, ilana gönderilecek metin)

Hello,

I will design the hardware for both devices (remote transmitter and receiver) and deliver a complete, manufacturing-ready PCB package. No firmware is included, as stated in your requirements.

## What I will deliver (exactly the items in your requirements)
- Schematics for both boards (PDF and KiCad source files)
- PCB layout for both boards (KiCad source files)
- Gerber files and drill files
- Bill of materials
- Pick-and-place (component placement) files
- Files compatible with PCBWay / JLCPCB ordering

## Additional items, not in your requirements (included at no extra charge, tell me if you do not want them)
- A short design note: power budget, antenna placement, connector pin-out
- Circuit simulation reports for the relay driver and power input protection
- Reverse polarity and surge protection on the 12 V input

## Transmitter (about 40 x 100 mm)
- ESP32-WROOM, RFM95W LoRa radio (915–928 MHz), 6 buttons, 1 status LED
- USB programming port
- Replaceable battery (battery type to be confirmed; a charging circuit is added only if the battery type needs one)

## Receiver
- ESP32, RFM95W LoRa radio, Ethernet, 4G LTE modem with SIM slot
- 1 button, 2 status LEDs, USB programming port
- 12 V normally-open relay output with transistor driver and flyback diode
- 12 V external supply input, buck converter to 5 V and 3.3 V

## Cellular modem choice
I plan to use the SIMCom SIM7600SA-H (LTE Cat 4), a South America variant. Its published band list includes bands 2, 4, 5, 7, 28 and 66, which cover the bands commonly used by Chilean carriers. I will confirm the exact band list against the manufacturer datasheet and the target carrier's current bands before the schematic is frozen. Cat 4 is not a requirement for this device; if cost matters, the Cat 1 SIM7600SA can replace it.

## How I verify the design
- Schematic electrical rules check and PCB design rules check in KiCad
- Power budget calculated per rail, with current margins
- Circuit simulation (ngspice) of the relay driver and power input protection
- Fabrication files opened in a Gerber viewer and checked against the manufacturer's rules

## What I do not claim
- Radio range and cellular coverage are not measured by me. They depend on the antenna and the site. I will follow the module manufacturers' reference designs and layout guidelines, but real range needs a field test with the built boards.

## Questions before I start
1. Target range of the remote (open field, inside a building)?
2. Battery type and expected battery life of the transmitter?
3. Antenna type: on-board, wire, or external connector (SMA)?
4. Enclosure: do you provide dimensions and screw positions?
5. Relay: maximum load current and voltage?
6. Quantity to be ordered (affects component choices)?

Timeline: [YOUR TIMELINE]. Price: [YOUR PRICE].

Best regards,
[YOUR NAME]
