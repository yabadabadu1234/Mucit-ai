import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from semagen import Sema
import simcom_uret as SU

R = 'Resistor_SMD:R_0603_1608Metric'
C = 'Capacitor_SMD:C_0603_1608Metric'
C8 = 'Capacitor_SMD:C_0805_2012Metric'
C12 = 'Capacitor_SMD:C_1206_3216Metric'
L = 'Inductor_SMD:L_Bourns_SRP7028A_7.3x6.6mm'

def kur():
    s = Sema('alici', 'A1', 'LoRa Alici - 12 V, Ethernet, 4G, role')
    s.bayrak = ['+12V', '+12V_IN', 'VBUS', '+3V3_USB', '+3V3', '+1V8']
    n = 0
    def p(ref, lib, ad, val, fp, pins, grup, **k):
        return s.parca(ref, lib, ad, val, fp, pins, grup=grup, **k)

    # ---------------- 12 V GIRIS ----------------
    G = '12 V GIRISI: klemens, sigorta, ters baglanti ve asiri gerilim korumasi'
    p('J5', 'Connector', 'Screw_Terminal_01x02', '12 V GIRIS', 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal', {1: '+12V_IN', 2: 'GND'}, G, rot=0)
    p('F1', 'Device', 'Polyfuse', '1812L200/16DR (2 A, 16 V)', 'Fuse:Fuse_1812_4532Metric', {1: '+12V_IN', 2: '+12V_F'}, G, alanlar={'MPN': 'Littelfuse 1812L200/16DR (tutma 2 A, 16 V; 8 V olan 1812L200TH kullanilmaz)'})
    p('Q1', 'Transistor_FET', 'AO3401A', 'AO3401A', 'Package_TO_SOT_SMD:SOT-23', {1: 'KAPI_P', 2: '+12V', 3: '+12V_F'}, G, rot=0, alanlar={'MPN': 'AO3401A'})
    p('R1', 'Device', 'R', '100k', R, {1: 'KAPI_P', 2: 'GND'}, G)
    p('D1', 'Device', 'D_Zener', '10 V', 'Diode_SMD:D_SOD-123', {1: '+12V', 2: 'KAPI_P'}, G, rot=0, alanlar={'MPN': 'BZT52C10 (10 V zener)'})
    p('D2', 'Diode', 'SMAJ15A', 'SMBJ15A', 'Diode_SMD:D_SMB', {1: 'GND', 2: '+12V'}, G, rot=0, alanlar={'MPN': 'SMBJ15A (tek yonlu 15 V TVS)'})
    p('C1', 'Device', 'C_Polarized', '220uF 25V', 'Capacitor_SMD:CP_Elec_8x10', {1: '+12V', 2: 'GND'}, G, rot=0)
    p('C2', 'Device', 'C', '100nF 50V', C, {1: '+12V', 2: 'GND'}, G)

    # ---------------- 3,3 V CEVIRICI ----------------
    G = '3,3 V: TPS62933 (12 V -> 3,3 V, 500 kHz)'
    p('U5', 'Regulator_Switching', 'TPS62933', 'TPS62933DRLR', 'Package_TO_SOT_SMD:SOT-583-8',
      {3: '+12V', 4: 'GND', 5: 'SW_3V3', 6: 'BST_3V3', 7: 'SS_3V3', 8: 'FB_3V3'}, G, alanlar={'MPN': 'TPS62933DRLR'})
    p('C3', 'Device', 'C', '10uF 25V', C12, {1: '+12V', 2: 'GND'}, G)
    p('C4', 'Device', 'C', '100nF 50V', C, {1: '+12V', 2: 'GND'}, G)
    p('C5', 'Device', 'C', '100nF 25V X7R', C, {1: 'BST_3V3', 2: 'SW_3V3'}, G)
    p('C6', 'Device', 'C', '33nF', C, {1: 'SS_3V3', 2: 'GND'}, G)
    p('L1', 'Device', 'L', '4,7uH Isat 10A', L, {1: 'SW_3V3', 2: '+3V3'}, G, alanlar={'MPN': 'Bourns SRP7028A-4R7M (Isat 10 A, Irms 5,5 A, DCR 40 mOhm; LCSC C840529)'})
    p('R2', 'Device', 'R', '31,6k 1%', R, {1: '+3V3', 2: 'FB_3V3'}, G)
    p('R3', 'Device', 'R', '10k 1%', R, {1: 'FB_3V3', 2: 'GND'}, G)
    p('C7', 'Device', 'C', '22uF 10V', C12, {1: '+3V3', 2: 'GND'}, G)
    p('C8', 'Device', 'C', '22uF 10V', C12, {1: '+3V3', 2: 'GND'}, G)
    p('C9', 'Device', 'C', '10uF 10V', C, {1: '+3V3', 2: 'GND'}, G)

    # ---------------- MODEM CEVIRICISI ----------------
    G = 'MODEM BESLEMESI: TPS62933 (12 V -> 4,0 V, >= 2 A tepe) ve toplu kondansator'
    p('U6', 'Regulator_Switching', 'TPS62933', 'TPS62933DRLR', 'Package_TO_SOT_SMD:SOT-583-8',
      {3: '+12V', 4: 'GND', 5: 'SW_MOD', 6: 'BST_MOD', 7: 'SS_MOD', 8: 'FB_MOD', 2: 'MODEM_EN'}, G, alanlar={'MPN': 'TPS62933DRLR'})
    p('C10', 'Device', 'C', '10uF 25V', C12, {1: '+12V', 2: 'GND'}, G)
    p('C11', 'Device', 'C', '100nF 50V', C, {1: '+12V', 2: 'GND'}, G)
    p('C12', 'Device', 'C', '100nF 25V X7R', C, {1: 'BST_MOD', 2: 'SW_MOD'}, G)
    p('C13', 'Device', 'C', '33nF', C, {1: 'SS_MOD', 2: 'GND'}, G)
    p('L2', 'Device', 'L', '4,7uH Isat 10A', L, {1: 'SW_MOD', 2: 'VBAT_MOD'}, G, alanlar={'MPN': 'Bourns SRP7028A-4R7M (Isat 10 A, Irms 5,5 A, DCR 40 mOhm; LCSC C840529)'})
    p('R4', 'Device', 'R', '40,2k 1%', R, {1: 'VBAT_MOD', 2: 'FB_MOD'}, G)
    p('R5', 'Device', 'R', '10k 1%', R, {1: 'FB_MOD', 2: 'GND'}, G)
    p('C14', 'Device', 'C', '22uF 10V', C12, {1: 'VBAT_MOD', 2: 'GND'}, G)
    p('C15', 'Device', 'C', '22uF 10V', C12, {1: 'VBAT_MOD', 2: 'GND'}, G)
    p('C16', 'Device', 'C_Polarized', '330uF 6,3V polimer ESR en fazla 40 mOhm', 'Capacitor_SMD:CP_Elec_6.3x7.7', {1: 'VBAT_MOD', 2: 'GND'}, G, rot=0)
    p('D3', 'Device', 'D_Zener', '5,1 V', 'Diode_SMD:D_SOD-123', {1: 'VBAT_MOD', 2: 'GND'}, G, rot=0, alanlar={'MPN': 'BZT52C5V1 (SIMCom onerisi, 500 mW)'})
    p('R6', 'Device', 'R', '100k', R, {1: '+3V3', 2: 'MODEM_EN'}, G)
    p('R7', 'Device', 'R', '1k', R, {1: 'MODEM_EN_CTL', 2: 'MODEM_EN'}, G)

    # ---------------- USB ----------------
    G = 'USB-C: programlama; 5 V yalniz 3,3 V LDO ve ideal diyot (LM66100) ile beslemeye girer'
    p('J1', 'Connector', 'USB_C_Receptacle_USB2.0_16P', 'USB-C', 'Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal',
      {'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND', 'S1': 'GND', 'A4': 'VBUS', 'A9': 'VBUS', 'B4': 'VBUS', 'B9': 'VBUS', 'A5': 'CC1', 'B5': 'CC2',
       'A6': 'USB_DP', 'B6': 'USB_DP', 'A7': 'USB_DM', 'B7': 'USB_DM'}, G, rot=0, alanlar={'MPN': 'GCT USB4105-GF-A'})
    p('R8', 'Device', 'R', '5,1k', R, {1: 'CC1', 2: 'GND'}, G)
    p('R9', 'Device', 'R', '5,1k', R, {1: 'CC2', 2: 'GND'}, G)
    p('U7', 'Power_Protection', 'USBLC6-2SC6', 'USBLC6-2SC6', 'Package_TO_SOT_SMD:SOT-23-6', {1: 'USB_DP', 6: 'USB_DP', 3: 'USB_DM', 4: 'USB_DM', 2: 'GND', 5: 'VBUS'}, G, alanlar={'MPN': 'USBLC6-2SC6'})
    p('U11', 'Regulator_Linear', 'AP2112K-3.3', 'AP2112K-3.3', 'Package_TO_SOT_SMD:SOT-23-5', {1: 'VBUS', 2: 'GND', 3: 'VBUS', 5: '+3V3_USB'}, G, alanlar={'MPN': 'AP2112K-3.3TRG1'})
    p('C17', 'Device', 'C', '1uF', C, {1: 'VBUS', 2: 'GND'}, G)
    p('C18', 'Device', 'C', '1uF', C, {1: '+3V3_USB', 2: 'GND'}, G)
    p('U15', 'Ozel', 'LM66100', 'LM66100', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', {1: '+3V3_USB', 2: 'GND', 3: '+3V3', 5: 'GND', 6: '+3V3'}, G, rot=0, alanlar={'MPN': 'TI LM66100DCKR (ideal diyot, 79-91 mOhm; CE VOUT\'a bagli: ters akim kesilir; LCSC C2869734)'})

    # ---------------- ISLEMCI ----------------
    G = 'ISLEMCI: ESP32-S3-WROOM-1'
    p('U1', 'RF_Module', 'ESP32-S3-WROOM-1', 'ESP32-S3-WROOM-1-N4', 'RF_Module:ESP32-S3-WROOM-1',
      {1: 'GND', 40: 'GND', 41: 'GND', 2: '+3V3', 3: 'EN', 27: 'DUGME', 39: 'MODEM_STATUS', 38: 'MODEM_EN_CTL', 4: 'MODEM_TXD_H', 5: 'MODEM_RXD_H', 6: 'MODEM_PWRKEY_CTL',
       7: 'MODEM_RST_CTL', 12: 'LORA_DIO0', 17: 'ETH_CS', 18: 'LORA_NSS', 19: 'SPI_MOSI', 20: 'SPI_SCK', 21: 'SPI_MISO', 22: 'LORA_RESET', 8: 'LORA_DIO1',
       9: 'ETH_INT', 10: 'ETH_RST', 13: 'USB_DM', 14: 'USB_DP', 31: 'ROLE_CTL', 32: 'LED1_CTL', 33: 'LED2_CTL'}, G, rot=0, alanlar={'MPN': 'ESP32-S3-WROOM-1-N4'})
    p('R10', 'Device', 'R', '10k', R, {1: '+3V3', 2: 'EN'}, G)
    p('C19', 'Device', 'C', '1uF', C, {1: 'EN', 2: 'GND'}, G)
    p('C20', 'Device', 'C', '22uF 10V', C8, {1: '+3V3', 2: 'GND'}, G)
    p('C21', 'Device', 'C', '100nF', C, {1: '+3V3', 2: 'GND'}, G)
    p('SW1', 'Switch', 'SW_Push', 'DUGME', 'Button_Switch_SMD:SW_SPST_TL3342', {1: 'DUGME', 2: 'GND'}, G, rot=0)
    p('R11', 'Device', 'R', '10k', R, {1: '+3V3', 2: 'DUGME'}, G)
    p('R12', 'Device', 'R', '470', R, {1: 'LED1_CTL', 2: 'LED1_A'}, G)
    p('D5', 'Device', 'LED', 'YESIL', 'LED_SMD:LED_0603_1608Metric', {2: 'LED1_A', 1: 'GND'}, G, rot=0)
    p('R13', 'Device', 'R', '470', R, {1: 'LED2_CTL', 2: 'LED2_A'}, G)
    p('D6', 'Device', 'LED', 'KIRMIZI', 'LED_SMD:LED_0603_1608Metric', {2: 'LED2_A', 1: 'GND'}, G, rot=0)

    # ---------------- LoRa ----------------
    G = 'LoRa: Ra-01H (SX1276, 803-930 MHz)'
    p('U4', 'Ozel', 'Ra-01H', 'Ra-01H', 'Ozel:Ra-01H',
      {3: '+3V3', 2: 'GND', 9: 'GND', 16: 'GND', 14: 'SPI_MOSI', 13: 'SPI_MISO', 12: 'SPI_SCK', 15: 'LORA_NSS', 4: 'LORA_RESET', 5: 'LORA_DIO0', 6: 'LORA_DIO1', 1: 'ANT_RF'}, G, rot=0, alanlar={'MPN': 'Ai-Thinker Ra-01H (LCSC C503593)'})
    p('C22', 'Device', 'C', '100nF', C, {1: '+3V3', 2: 'GND'}, G)
    p('C23', 'Device', 'C', '10uF 6,3V', C, {1: '+3V3', 2: 'GND'}, G)
    p('J2', 'Connector', 'Conn_Coaxial', 'SMA', 'Connector_Coaxial:SMA_Amphenol_132289_EdgeMount', {1: 'ANT_RF', 2: 'GND'}, G, rot=0, alanlar={'MPN': 'Amphenol 132289 (kenar SMA)'})

    # ---------------- ETHERNET ----------------
    G = 'ETHERNET: W5500 (WIZnet referans devresi, RJ45 + manyetik)'
    p('U9', 'Interface_Ethernet', 'W5500', 'W5500', 'Package_QFP:LQFP-48_7x7mm_P0.5mm',
      {1: 'W_TXN', 2: 'W_TXP', 5: 'W_RXN', 6: 'W_RXP', 3: 'GND', 9: 'GND', 14: 'GND', 16: 'GND', 19: 'GND', 48: 'GND', 29: 'GND',
       4: '+3V3A', 8: '+3V3A', 11: '+3V3A', 15: '+3V3A', 17: '+3V3A', 21: '+3V3A', 28: '+3V3', 10: 'EXRES1', 20: 'TOCAP', 22: '1V2O',
       30: 'XI', 31: 'XO', 23: 'GND', 25: 'W_LINKLED', 27: 'W_ACTLED', 32: 'ETH_CS', 33: 'SPI_SCK', 34: 'SPI_MISO', 35: 'SPI_MOSI', 36: 'ETH_INT', 37: 'ETH_RST',
       43: '+3V3', 44: '+3V3', 45: '+3V3'}, G, rot=0, alanlar={'MPN': 'W5500'})
    p('J3', 'Connector', 'RJ45_Hanrun_HR911105A_Horizontal', 'RJ45', 'Connector_RJ:RJ45_Hanrun_HR911105A_Horizontal',
      {1: 'TD_P', 2: 'TD_N', 3: 'RD_P', 4: 'TCT', 5: 'RCT', 6: 'RD_N', 8: 'GND', 9: '+3V3', 10: 'LNK_K', 11: 'ACT_K', 12: '+3V3', 'SH': 'SHELL'}, G, rot=0, alanlar={'MPN': 'HanRun HR911105A'})
    for ref, a, b, v in [('R14', 'W_TXN', 'TD_P', '0'), ('R15', 'W_TXP', 'TD_N', '0'), ('R16', 'W_RXN', 'RX_A', '0'), ('R17', 'W_RXP', 'RX_B', '0')]:
        p(ref, 'Device', 'R', v, R, {1: a, 2: b}, G)
    p('R18', 'Device', 'R', '49,9 1%', R, {1: '+3V3A', 2: 'TD_P'}, G)
    p('R19', 'Device', 'R', '49,9 1%', R, {1: '+3V3A', 2: 'TD_N'}, G)
    p('R20', 'Device', 'R', '10 1%', R, {1: '+3V3A', 2: 'TCT'}, G)
    p('C24', 'Device', 'C', '22nF', C, {1: 'TCT', 2: 'GND'}, G)
    p('R21', 'Device', 'R', '49,9 1%', R, {1: 'RX_A', 2: 'RX_M'}, G)
    p('R22', 'Device', 'R', '49,9 1%', R, {1: 'RX_B', 2: 'RX_M'}, G)
    p('C25', 'Device', 'C', '6,8nF', C, {1: 'RX_A', 2: 'RD_P'}, G)
    p('C26', 'Device', 'C', '6,8nF', C, {1: 'RX_B', 2: 'RD_N'}, G)
    p('C27', 'Device', 'C', '10nF', C, {1: 'RX_M', 2: 'GND'}, G)
    s.parca('R23', 'Device', 'R', '0', R, {1: 'RX_M', 2: 'RCT'}, grup=G)
    p('R24', 'Device', 'R', '330', R, {1: 'W_LINKLED', 2: 'LNK_K'}, G)
    p('R25', 'Device', 'R', '330', R, {1: 'W_ACTLED', 2: 'ACT_K'}, G)
    p('L3', 'Device', 'FerriteBead', '120R @100MHz', 'Inductor_SMD:L_0603_1608Metric', {1: '+3V3', 2: '+3V3A'}, G, alanlar={'MPN': 'HH-1M1608-121JT (WIZnet referansi)'})
    for i, ref in enumerate(['C28', 'C29', 'C30', 'C31', 'C32', 'C33']):
        p(ref, 'Device', 'C', '100nF', C, {1: '+3V3A', 2: 'GND'}, G)
    p('C34', 'Device', 'C', '10uF 16V', C, {1: '+3V3A', 2: 'GND'}, G)
    p('C35', 'Device', 'C', '10uF 16V', C, {1: '+3V3', 2: 'GND'}, G)
    p('C36', 'Device', 'C', '100nF', C, {1: '+3V3', 2: 'GND'}, G)
    p('R26', 'Device', 'R', '12,4k 1%', R, {1: 'EXRES1', 2: 'GND'}, G)
    p('C37', 'Device', 'C', '10nF', C, {1: '1V2O', 2: 'GND'}, G)
    p('C38', 'Device', 'C', '4,7uF', C, {1: 'TOCAP', 2: 'GND'}, G)
    p('Y1', 'Device', 'Crystal_GND24', '25 MHz', 'Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm', {1: 'XI', 3: 'XB', 2: 'GND', 4: 'GND'}, G, rot=0, alanlar={'MPN': '25 MHz, 18 pF yuk, +-30 ppm, C0 en fazla 7 pF (W5500 belgesi 5.5.3)'})
    p('R27', 'Device', 'R', '1M', R, {1: 'XI', 2: 'XO'}, G)
    p('R28', 'Device', 'R', '0', R, {1: 'XO', 2: 'XB'}, G)
    p('C39', 'Device', 'C', '18pF', C, {1: 'XI', 2: 'GND'}, G)
    p('C40', 'Device', 'C', '18pF', C, {1: 'XB', 2: 'GND'}, G)
    p('C41', 'Device', 'C', '1nF 2kV', C12, {1: 'SHELL', 2: 'GND'}, G)
    p('R29', 'Device', 'R', '10k', R, {1: '+3V3', 2: 'ETH_INT'}, G)

    # ---------------- MODEM ----------------
    G = '4G MODEM: A7670SA (SIMCom), SIM yuvasi, anten, seviye cevirici'
    modem = {}
    ata = {'VBAT': 'VBAT_MOD', 'GND': 'GND', 'PWRKEY': 'PWRKEY', 'RESET': 'MODEM_RESET', 'VDD_1V8': '+1V8', 'TXD': 'M_TXD', 'RXD': 'M_RXD', 'STATUS': 'M_STATUS',
           'SIM_VDD': 'USIM_VDD', 'SIM_DATA': 'USIM_DATA_M', 'SIM_RST': 'USIM_RST_M', 'SIM_CLK': 'USIM_CLK_M', 'RF_ANT': 'MODEM_ANT',
           'USB_BOOT': 'USB_BOOT', 'USB_DM': 'M_USB_DN', 'USB_DP': 'M_USB_DP', 'VBUS': 'M_USB_VBUS', 'UART_LOG_TX': 'LOG_TX'}
    for num, ad in SU.ISIM.items():
        if ad in ata:
            modem[num] = ata[ad]
    p('U10', 'Simcom', 'A7670SA', 'A7670SA', 'Simcom:A7670SA_LGA88', modem, G, rot=0, alanlar={'MPN': 'SIMCom A7670SA-LASE (LCSC C47088708; LTE-FDD B1/2/3/4/5/7/8/28/66, GSM 850/900/1800/1900)'})
    p('U8', 'Logic_LevelTranslator', 'TXB0104PW', 'TXB0104PW', 'Package_SO:TSSOP-14_4.4x5mm_P0.65mm',
      {1: '+1V8', 8: '+1V8', 14: '+3V3', 7: 'GND', 5: 'GND', 10: 'GND', 2: 'M_TXD', 13: 'MODEM_RXD_H', 3: 'M_RXD', 12: 'MODEM_TXD_H', 4: 'M_STATUS', 11: 'MODEM_STATUS'}, G, alanlar={'MPN': 'TXB0104PWR'})
    p('C42', 'Device', 'C', '100nF', C, {1: '+1V8', 2: 'GND'}, G)
    p('C43', 'Device', 'C', '100nF', C, {1: '+3V3', 2: 'GND'}, G)
    for q, ctl, col, c in [('Q3', 'MODEM_PWRKEY_CTL', 'PWRKEY', 'C44'), ('Q4', 'MODEM_RST_CTL', 'MODEM_RESET', 'C45')]:
        p(q, 'Device', 'Q_NPN_BEC', 'MMBT2222A', 'Package_TO_SOT_SMD:SOT-23', {1: q + '_B', 2: 'GND', 3: col}, G, rot=0, alanlar={'MPN': 'MMBT2222A'})
        p('R' + str(30 + (1 if q == 'Q3' else 3)), 'Device', 'R', '1k', R, {1: ctl, 2: q + '_B'}, G)
        p('R' + str(31 + (1 if q == 'Q3' else 3)), 'Device', 'R', '10k', R, {1: q + '_B', 2: 'GND'}, G)
        p(c, 'Device', 'C', '1nF', C, {1: col, 2: 'GND'}, G, alanlar={'MPN': 'A7670 belgesi: PWRKEY ve RESET uzerinde 10 nF ustu kondansator yasak'})
    p('U13', 'Power_Protection', 'USBLC6-2SC6', 'USBLC6-2SC6', 'Package_TO_SOT_SMD:SOT-23-6', {1: 'PWRKEY', 6: 'PWRKEY', 3: 'MODEM_RESET', 4: 'MODEM_RESET', 2: 'GND', 5: 'VBAT_MOD'}, G, alanlar={'MPN': 'USBLC6-2SC6 (PWRKEY ve RESET ESD, hat basina en fazla 3,5 pF)'})
    p('C46', 'Device', 'C', '100nF', C, {1: 'VBAT_MOD', 2: 'GND'}, G)
    p('C47', 'Device', 'C', '100nF', C, {1: 'VBAT_MOD', 2: 'GND'}, G)
    p('C48', 'Device', 'C', '10uF 10V', C, {1: 'VBAT_MOD', 2: 'GND'}, G)
    p('C52', 'Device', 'C', '33pF', C, {1: 'VBAT_MOD', 2: 'GND'}, G)
    p('C53', 'Device', 'C', '10pF', C, {1: 'VBAT_MOD', 2: 'GND'}, G)
    p('C54', 'Device', 'C', '1uF', C, {1: 'VBAT_MOD', 2: 'GND'}, G)
    p('J7', 'Connector', 'SIM_Card', 'MICRO-SIM', 'Connector_Card:microSIM_JAE_SF53S006VCBR2000', {1: 'USIM_VDD', 2: 'USIM_RST', 3: 'USIM_CLK', 5: 'GND', 7: 'USIM_DATA'}, G, rot=0, alanlar={'MPN': 'JAE SF53S006VCBR2000 (6 uclu micro-SIM)'})
    for ref, a_, b_ in [('R39', 'USIM_RST_M', 'USIM_RST'), ('R40', 'USIM_CLK_M', 'USIM_CLK'), ('R41', 'USIM_DATA_M', 'USIM_DATA')]:
        p(ref, 'Device', 'R', '22', R, {1: a_, 2: b_}, G, alanlar={'MPN': 'A7670 belgesi Sekil 19: SIM hatlarina 22 ohm seri'})
    p('U12', 'Power_Protection', 'USBLC6-2SC6', 'USBLC6-2SC6', 'Package_TO_SOT_SMD:SOT-23-6', {1: 'USIM_RST', 6: 'USIM_RST', 3: 'USIM_CLK', 4: 'USIM_CLK', 2: 'GND', 5: 'USIM_VDD'}, G, alanlar={'MPN': 'USBLC6-2SC6 (SIM RST ve CLK ESD; SIMCom siniri 60 pF, parca hat basina en fazla 3,5 pF)'})
    p('U14', 'Power_Protection', 'USBLC6-2SC6', 'USBLC6-2SC6', 'Package_TO_SOT_SMD:SOT-23-6', {1: 'USIM_DATA', 6: 'USIM_DATA', 2: 'GND', 5: 'USIM_VDD'}, G, alanlar={'MPN': 'USBLC6-2SC6 (SIM DATA ESD; ikinci hat kullanilmaz)'})
    p('C49', 'Device', 'C', '100nF', C, {1: 'USIM_VDD', 2: 'GND'}, G)
    p('R35', 'Device', 'R', '0', R, {1: 'MODEM_ANT', 2: 'ANT_4G'}, G)
    p('C50', 'Device', 'C', 'DNP', C, {1: 'MODEM_ANT', 2: 'GND'}, G, dnp=True)
    p('C51', 'Device', 'C', 'DNP', C, {1: 'ANT_4G', 2: 'GND'}, G, dnp=True)
    p('J4', 'Connector', 'Conn_Coaxial', 'u.FL (ANA ANTEN)', 'Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical', {1: 'ANT_4G', 2: 'GND'}, G, rot=0, alanlar={'MPN': 'Hirose U.FL-R-SMT-1(10)'})
    p('TP1', 'Connector', 'TestPoint', 'USB_BOOT', 'TestPoint:TestPoint_Pad_1.0x1.0mm', {1: 'USB_BOOT'}, G, rot=0)
    p('TP2', 'Connector', 'TestPoint', 'USB_DM', 'TestPoint:TestPoint_Pad_1.0x1.0mm', {1: 'M_USB_DN'}, G, rot=0)
    p('TP3', 'Connector', 'TestPoint', 'USB_DP', 'TestPoint:TestPoint_Pad_1.0x1.0mm', {1: 'M_USB_DP'}, G, rot=0)
    p('TP4', 'Connector', 'TestPoint', 'USB_VBUS', 'TestPoint:TestPoint_Pad_1.0x1.0mm', {1: 'M_USB_VBUS'}, G, rot=0)
    p('TP5', 'Connector', 'TestPoint', 'UART_LOG_TX', 'TestPoint:TestPoint_Pad_1.0x1.0mm', {1: 'LOG_TX'}, G, rot=0)

    # ---------------- ROLE ----------------
    G = 'ROLE: 12 V isaret lambasi (normalde acik)'
    p('K1', 'Relay', 'SANYOU_SRD_Form_A', 'SRD-12VDC-SL-A', 'Relay_THT:Relay_SPST_SANYOU_SRD_Series_Form_A', {2: '+12V', 5: 'ROLE_L', 1: '+12V_IN', 3: 'LAMBA_SW'}, G, rot=0, alanlar={'MPN': 'Songle SRD-12VDC-SL-A (bobin 400 ohm, kontak 10 A 30 VDC)'})
    p('Q2', 'Device', 'Q_NPN_BEC', 'MMBT2222A', 'Package_TO_SOT_SMD:SOT-23', {1: 'Q2_B', 2: 'GND', 3: 'ROLE_L'}, G, rot=0, alanlar={'MPN': 'MMBT2222A'})
    p('R37', 'Device', 'R', '1k', R, {1: 'ROLE_CTL', 2: 'Q2_B'}, G)
    p('R38', 'Device', 'R', '10k', R, {1: 'Q2_B', 2: 'GND'}, G)
    p('D7', 'Diode', 'SS14', 'SS14', 'Diode_SMD:D_SMA', {1: '+12V', 2: 'ROLE_L'}, G, alanlar={'MPN': 'SS14'})
    p('J6', 'Connector', 'Screw_Terminal_01x02', 'LAMBA', 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal', {1: 'LAMBA_SW', 2: 'GND'}, G, rot=0)
    return s

if __name__ == '__main__':
    kur().yaz(sys.argv[1])
    print('yazildi')
