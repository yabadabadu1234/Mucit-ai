# Teklif taslağı (İngilizce, ilana gönderilecek metin)

Hello,

I will deliver everything listed in your requirements, nothing less. No firmware, as stated.

## Additional items (not in your requirements, included at no extra charge; tell me if you do not want them)
- A short design note: power budget, antenna placement, connector pin-out
- Circuit simulation reports for the relay driver and the 12 V input protection
- Reverse polarity and surge protection on the 12 V input

## Cellular modem
I plan to use the SIMCom SIM7600SA-H (LTE Cat 4), a South America variant. Its published band list includes bands 2, 4, 5, 7, 28 and 66, which cover the bands commonly used by Chilean carriers. I will confirm the exact band list against the manufacturer datasheet and the target carrier's current bands before the schematic is frozen. Cat 4 is not a requirement; if cost matters, the Cat 1 SIM7600SA can replace it.

## How I verify the design
- Electrical rules check and design rules check in KiCad
- Power budget per rail, with current margins
- ngspice simulation of the relay driver and the input protection

I cannot measure radio range or cellular coverage without built boards. I will follow the module manufacturers' reference designs and layout guidelines; real range needs a field test.

## Questions before I start
1. Target range of the remote (open field, inside a building)?
2. Battery type and expected battery life of the transmitter?
3. Antenna type: on-board, wire, or external connector (SMA)?
4. Enclosure: do you provide dimensions and screw positions?
5. Maximum relay load current and voltage?
6. Quantity to be ordered?
7. Which carrier SIM will be used?

Timeline: [YOUR TIMELINE]. Price: [YOUR PRICE].

Best regards,
[YOUR NAME]
