# Teklif taslağı (İngilizce, ilana gönderilecek metin)

Hello,

I have already started the design and may have finished it before you accept this offer.

I will deliver everything listed in your requirements, nothing less. No firmware, as stated.

## Additional items (not in your requirements, included at no extra charge; tell me if you do not want them)
- A short design note: power budget, antenna placement, connector pin-out
- Circuit simulation reports for the relay driver and the 12 V input protection
- Reverse polarity and surge protection on the 12 V input

## Cellular modem
Default: SIMCom SIM7600SA (LTE Cat 1), the cheaper one. Its published band list includes bands 2, 4, 5, 7, 28 and 66, which cover the bands commonly used by Chilean carriers. If you state that it is not sufficient, I will use the SIM7600SA-H (LTE Cat 4) instead. I will confirm the exact band list against the manufacturer datasheet and the target carrier's current bands before the schematic is frozen.

## Parts not specified in your requirements: my choices
Chosen for low cost and good availability from the PCBWay / JLCPCB parts libraries; final values are confirmed in the design.
- Microcontroller (both boards): ESP32-WROOM-32E
- LoRa radio (both boards): RFM95W-915S2
- USB programming: USB-C connector with CH340C USB-to-serial chip and automatic reset circuit
- Ethernet: W5500 chip with HR911105A connector (RJ45 with built-in magnetics)
- Relay: Songle SRD-12VDC-SL-A (10 A, normally open), driven by an MMBT2222A transistor with an SS14 flyback diode
- Receiver power: TPS62933 step-down converters (12 V to 5 V and to the modem voltage), 3.3 V rail from a step-down converter instead of a linear regulator, to reduce heat
- 12 V input protection: SMBJ15A surge protector, AO3401A reverse polarity protection
- Transmitter power: two AAA cells in a Keystone 2468 holder, TPS63031 buck-boost converter to 3.3 V, slide switch MSK12C02
- Buttons and LEDs: 6 mm tact switches, 0603 LEDs with series resistors
- Connectors: 5.08 mm screw terminals (12 V input, relay contacts), SMA edge-mount connectors for LoRa antennas, u.FL connector for the cellular antenna, Nano-SIM push-push holder

## How I verify the design
- Electrical rules check and design rules check in KiCad
- Power budget per rail, with current margins
- ngspice simulation of the relay driver and the input protection

I cannot measure radio range or cellular coverage without built boards. I will follow the module manufacturers' reference designs and layout guidelines; real range needs a field test.

## Questions, with the defaults I will design to if you do not answer
1. Target range of the remote: open field, line of sight. (I design for it but cannot guarantee a range figure.)
2. Transmitter battery: two AAA alkaline cells in a user-replaceable holder (easy to source), with a converter to 3.3 V and the main ON/OFF switch. No charging circuit.
3. Antennas: SMA connectors for the LoRa radio on both boards, plus the standard cellular antenna connectors on the receiver.
4. Board size: transmitter 40 x 100 mm is treated as the maximum; the receiver has no size limit in your requirements. For both I will aim for the smallest and most power-efficient board possible. Four M3 mounting holes, no enclosure assumed.
5. Relay: 12 V coil, normally open contact rated for 12 VDC at 10 A, wired to a screw terminal. The 12 V input also feeds the board through a screw terminal.
6. Quantity: one design per device. No physical production by me, design files only.
7. SIM: standard unlocked SIM from any Chilean carrier.
8. Ethernet and 4G: both present and independent on the board.

Timeline: 5 days from your answers. Price: 300 USD, fixed.

Best regards,
[YOUR NAME]
