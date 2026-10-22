# Receiver – design note (work in progress)

## Pin map (ESP32-S3-WROOM-1-N4)
Shared SPI: SCK IO12, MOSI IO11, MISO IO13. RFM95W: NSS IO10, RESET IO14, DIO0 IO8, DIO1 IO15. W5500: CS IO9, INT IO16, RST IO17. Modem UART (through TXB0104 level shifter, modem side is 1.8 V): host TX IO4, host RX IO5, STATUS IO1, PWRKEY driver IO6, RESET driver IO7, modem supply enable IO2. Relay driver IO38, LEDs IO39/IO40, button IO0 (also boot), USB D- IO19, D+ IO20.

## Power chain
12 V screw terminal -> 2 A PTC -> P-MOSFET reverse protection (gate 10 V zener) -> 15 V TVS -> TPS62933 to 3.3 V (31.6k/10k divider) and TPS62933 to 3.8 V for the modem (37.4k/10k, enable by IO2, 330 uF polymer + 2x22 uF, 5.1 V zener). USB 5 V only feeds an AP2112K-3.3 through a Schottky (programming without 12 V). Relay: SRD-12VDC-SL-A, contacts take 12 V from the terminal before the fuse and MOSFET (beacon current does not flow through them); coil driver NPN with 10k pull-down so the relay stays off at boot.

## Simulation (ngspice, generic models, see simulasyon/)
Relay driver: coil 29.8 mA, Vce(sat) 62 mV, flyback peak 12.2 V. Input protection: normal 1 A -> 0.30 V total drop (Q1 about 50 mV); -12 V reverse -> output -0.08 V, input current 2e-11 A; 36 V surge through 2 ohm -> output clamped at 20.3 V, MOSFET Vgs -9.9 V.

## Open items
Layout/routing not finished; 50 ohm RF lines and wide relay/beacon tracks to be drawn by hand; modem pinout taken from the SIM7600E/E-H hardware design V1.02 (SA/SA-H document not found); beacon current is assumed (3 A design value); bulk capacitance on the modem rail needs bench validation (loop stability with 330 uF).
