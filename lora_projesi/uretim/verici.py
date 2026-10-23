import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from semagen import Sema

R = 'Resistor_SMD:R_0603_1608Metric'
C = 'Capacitor_SMD:C_0603_1608Metric'
C8 = 'Capacitor_SMD:C_0805_2012Metric'

def kur():
    s = Sema('verici', 'A2', 'LoRa Uzaktan Kumanda - Verici')
    s.bayrak = ['VIN', 'VBUS', 'VBAT_RAW']
    G = 'BESLEME: pil, anahtar, VBUS ile birlestirme, 3,3 V cevirici'
    s.parca('BT1', 'Device', 'Battery', '2xAAA', 'Battery:BatteryHolder_Keystone_2468_2xAAA', {1: 'VBAT_RAW', 2: 'GND'}, rot=0, grup=G, alanlar={'MPN': 'Keystone 2468'})
    s.parca('SW1', 'Switch', 'SW_SPDT', 'ANA ACMA-KAPAMA', 'Button_Switch_SMD:SW_SPDT_PCM12', {1: 'VBAT_RAW', 2: 'VBAT_SW'}, rot=0, grup=G, alanlar={'MPN': 'MSK12C02 (kayar anahtar)'})
    s.parca('D1', 'Diode', 'SS14', 'SS14', 'Diode_SMD:D_SMA', {1: 'VIN', 2: 'VBAT_SW'}, grup=G, alanlar={'MPN': 'SS14'})
    s.parca('D2', 'Diode', 'SS14', 'SS14', 'Diode_SMD:D_SMA', {1: 'VIN', 2: 'VBUS'}, grup=G, alanlar={'MPN': 'SS14'})
    s.parca('C1', 'Device', 'C', '10uF 6,3V', C, {1: 'VIN', 2: 'GND'}, grup=G)
    s.parca('C2', 'Device', 'C', '100nF', C, {1: 'VIN', 2: 'GND'}, grup=G)
    s.parca('U2', 'Regulator_Switching', 'TPS63031DSK', 'TPS63031DSKR', 'Package_SON:WSON-10-1EP_2.5x2.5mm_P0.5mm_EP1.2x2mm',
            {1: '+3V3', 2: 'L2N', 3: 'GND', 4: 'L1N', 5: 'VIN', 6: 'VIN', 7: 'GND', 8: 'VIN', 9: 'GND', 10: '+3V3', 11: 'GND'}, grup=G, alanlar={'MPN': 'TPS63031DSKR'})
    s.parca('L1', 'Device', 'L', '1,5uH', 'Inductor_SMD:L_Cenker_CKCS3015', {1: 'L1N', 2: 'L2N'}, grup=G, alanlar={'MPN': '1,5uH 3x3mm (Coilcraft LPS3015-152 esdegeri)'})
    s.parca('C3', 'Device', 'C', '10uF 6,3V', C, {1: '+3V3', 2: 'GND'}, grup=G)
    s.parca('C4', 'Device', 'C', '10uF 6,3V', C, {1: '+3V3', 2: 'GND'}, grup=G)

    G = 'USB-C: programlama ve besleme (yalniz 5 V girisi)'
    s.parca('J1', 'Connector', 'USB_C_Receptacle_USB2.0_16P', 'USB-C',
            'Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal',
            {'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND', 'S1': 'GND', 'A4': 'VBUS', 'A9': 'VBUS', 'B4': 'VBUS', 'B9': 'VBUS',
             'A5': 'CC1', 'B5': 'CC2', 'A6': 'USB_DP', 'B6': 'USB_DP', 'A7': 'USB_DM', 'B7': 'USB_DM'}, rot=0, grup=G, alanlar={'MPN': 'GCT USB4105-GF-A'})
    s.parca('R9', 'Device', 'R', '5,1k', R, {1: 'CC1', 2: 'GND'}, grup=G)
    s.parca('R10', 'Device', 'R', '5,1k', R, {1: 'CC2', 2: 'GND'}, grup=G)
    s.parca('U3', 'Power_Protection', 'USBLC6-2SC6', 'USBLC6-2SC6', 'Package_TO_SOT_SMD:SOT-23-6',
            {1: 'USB_DP', 6: 'USB_DP', 3: 'USB_DM', 4: 'USB_DM', 2: 'GND', 5: 'VBUS'}, grup=G, alanlar={'MPN': 'USBLC6-2SC6'})

    G = 'ISLEMCI: ESP32-S3-WROOM-1'
    s.parca('U1', 'RF_Module', 'ESP32-S3-WROOM-1', 'ESP32-S3-WROOM-1-N4', 'RF_Module:ESP32-S3-WROOM-1',
            {1: 'GND', 40: 'GND', 41: 'GND', 2: '+3V3', 3: 'EN', 27: 'BTN1', 4: 'BTN2', 38: 'BTN3', 5: 'BTN4', 39: 'BTN5', 6: 'BTN6', 7: 'LED_CTL',
             12: 'LORA_DIO0', 17: 'LORA_DIO1', 18: 'LORA_NSS', 19: 'LORA_MOSI', 20: 'LORA_SCK', 21: 'LORA_MISO', 22: 'LORA_RESET',
             13: 'USB_DM', 14: 'USB_DP'}, rot=0, grup=G, alanlar={'MPN': 'ESP32-S3-WROOM-1-N4'})
    s.parca('R1', 'Device', 'R', '10k', R, {1: '+3V3', 2: 'EN'}, grup=G)
    s.parca('C7', 'Device', 'C', '1uF', C, {1: 'EN', 2: 'GND'}, grup=G)
    s.parca('C5', 'Device', 'C', '22uF', C8, {1: '+3V3', 2: 'GND'}, grup=G)
    s.parca('C6', 'Device', 'C', '100nF', C, {1: '+3V3', 2: 'GND'}, grup=G)

    G = 'DUGMELER (alti, hepsi uyandirma yapabilen RTC pinlerinde) VE DURUM LED\'i'
    pins = ['BTN1', 'BTN2', 'BTN3', 'BTN4', 'BTN5', 'BTN6']
    for i, n in enumerate(pins):
        s.parca('SW%d' % (i + 2), 'Switch', 'SW_Push', 'DUGME %d' % (i + 1), 'Button_Switch_SMD:SW_SPST_TL3342', {1: n, 2: 'GND'}, rot=0, grup=G)
        s.parca('R%d' % (i + 2), 'Device', 'R', '100k', R, {1: '+3V3', 2: n}, grup=G)
    s.parca('R8', 'Device', 'R', '470', R, {1: 'LED_CTL', 2: 'LED_A'}, grup=G)
    s.parca('D3', 'Device', 'LED', 'YESIL', 'LED_SMD:LED_0603_1608Metric', {2: 'LED_A', 1: 'GND'}, rot=0, grup=G)

    G = 'LoRa: Ra-01H (SX1276) ve anten konnektoru'
    s.parca('U4', 'Ozel', 'Ra-01H', 'Ra-01H', 'Ozel:Ra-01H',
            {3: '+3V3', 2: 'GND', 9: 'GND', 16: 'GND', 14: 'LORA_MOSI', 13: 'LORA_MISO', 12: 'LORA_SCK', 15: 'LORA_NSS', 4: 'LORA_RESET',
             5: 'LORA_DIO0', 6: 'LORA_DIO1', 1: 'ANT_RF'}, rot=0, grup=G, alanlar={'MPN': 'Ai-Thinker Ra-01H (LCSC C503593)'})
    s.parca('C8', 'Device', 'C', '100nF', C, {1: '+3V3', 2: 'GND'}, grup=G)
    s.parca('C9', 'Device', 'C', '10uF 6,3V', C, {1: '+3V3', 2: 'GND'}, grup=G)
    s.parca('J2', 'Connector', 'Conn_Coaxial', 'SMA', 'Connector_Coaxial:SMA_Amphenol_132289_EdgeMount', {1: 'ANT_RF', 2: 'GND'}, rot=0, grup=G, alanlar={'MPN': 'Amphenol 132289 (kenar SMA)'})
    return s

if __name__ == '__main__':
    yol = sys.argv[1]
    kur().yaz(yol)
    print('yazildi', yol)
