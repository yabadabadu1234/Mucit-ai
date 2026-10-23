import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
from pcbgen import Pano, mm, vec
from otoyer import Yer, pad_konum, sinir

W, H = 88.0, 102.0

SABIT = {
    # ref: (x, y, donme, arka, tht)
    'J5': (4.9, 7.0, 270, False, True), 'J6': (4.9, 19.0, 270, False, True),
    'K1': (14.0, 11.0, 0, False, True),
    'U5': (40.0, 9.0, 0, False, False),
    'U10': (28.0, 47.0, 270, False, False),
    'U8': (28.0, 27.0, 0, False, False),
    'U6': (34.0, 73.0, 0, False, False),
    'J1': (14.0, 94.8, 0, False, False),
    'U1': (66.0, 85.0, 180, False, False),
    'U4': (70.0, 16.0, 0, False, False),
    'J2': (62.5, 4.5, 90, False, False),
    'J3': (67.0, 66.0, 90, False, True),
    'U9': (56.0, 62.0, 0, False, False),
    'J4': (48.5, 47.0, 0, False, False),
    'J7': (28.0, 47.0, 0, True, False),
    'SW1': (36.0, 86.0, 0, False, False),
    'D5': (43.0, 87.0, 0, False, False), 'D6': (47.0, 87.0, 0, False, False),
}

# pasif: (capa_ref, capa_pin, arka)
A = {
    'F1': ('J5', '1'), 'Q1': ('F1', '2'), 'R1': ('Q1', '1'), 'D1': ('Q1', '2'), 'D2': ('Q1', '2'), 'C1': ('D2', '1'), 'C2': ('D2', '1'),
    'C3': ('U5', '3'), 'C4': ('U5', '3'), 'L1': ('U5', '5'), 'C5': ('U5', '6'), 'C6': ('U5', '7'), 'R2': ('U5', '8'), 'R3': ('U5', '8'),
    'C7': ('L1', '2'), 'C8': ('L1', '2'), 'C9': ('L1', '2'),
    'C10': ('U6', '3'), 'C11': ('U6', '3'), 'L2': ('U6', '5'), 'C12': ('U6', '6'), 'C13': ('U6', '7'), 'R4': ('U6', '8'), 'R5': ('U6', '8'),
    'C14': ('L2', '2'), 'C15': ('L2', '2'), 'C16': ('L2', '2'), 'D3': ('L2', '2'), 'R6': ('U6', '2'), 'R7': ('U6', '2'),
    'R8': ('J1', 'A5'), 'R9': ('J1', 'B5'), 'U7': ('J1', 'A6'), 'U11': ('J1', 'A4'), 'C17': ('U11', '1'), 'C18': ('U11', '5'), 'U15': ('U11', '5'),
    'R10': ('U1', '3'), 'C19': ('U1', '3'), 'C20': ('U1', '2'), 'C21': ('U1', '2'), 'R11': ('SW1', '1'), 'R12': ('D5', '2'), 'R13': ('D6', '2'),
    'C22': ('U4', '3'), 'C23': ('U4', '3'),
    'R14': ('U9', '1'), 'R15': ('U9', '2'), 'R16': ('U9', '5'), 'R17': ('U9', '6'),
    'R18': ('R14', '2'), 'R19': ('R15', '2'), 'R20': ('J3', '4'), 'C24': ('R20', '2'), 'R21': ('R16', '2'), 'R22': ('R17', '2'),
    'C25': ('R16', '2'), 'C26': ('R17', '2'), 'C27': ('R21', '2'), 'R23': ('J3', '5'), 'R24': ('J3', '10'), 'R25': ('J3', '11'),
    'L3': ('U9', '4'), 'C28': ('U9', '4'), 'C29': ('U9', '8'), 'C30': ('U9', '11'), 'C31': ('U9', '15'), 'C32': ('U9', '17'), 'C33': ('U9', '21'), 'C34': ('L3', '2'),
    'C35': ('U9', '28'), 'C36': ('U9', '28'), 'R26': ('U9', '10'), 'C37': ('U9', '22'), 'C38': ('U9', '20'), 'Y1': ('U9', '30'),
    'R27': ('Y1', '1'), 'R28': ('Y1', '3'), 'C39': ('Y1', '1'), 'C40': ('Y1', '3'), 'R29': ('U9', '36'), 'C41': ('J3', 'SH'),
    'C42': ('U8', '1'), 'C43': ('U8', '14'),
    'Q3': ('U10', '1'), 'R31': ('Q3', '1'), 'R32': ('Q3', '1'), 'C44': ('Q3', '3'), 'U13': ('Q3', '3'),
    'Q4': ('U10', '16'), 'R33': ('Q4', '1'), 'R34': ('Q4', '1'), 'C45': ('Q4', '3'),
    'C46': ('U10', '55'), 'C47': ('U10', '56'), 'C48': ('U10', '57'), 'C52': ('U10', '55'), 'C53': ('U10', '56'), 'C54': ('U10', '57'),
    'U12': ('J7', '2'), 'U14': ('J7', '7'), 'C49': ('J7', '1'), 'R39': ('U10', '33'), 'R40': ('U10', '32'), 'R41': ('U10', '31'),
    'R35': ('U10', '60'), 'C50': ('R35', '1'), 'C51': ('R35', '2'),
    'TP1': ('U10', '6'), 'TP2': ('U10', '28'), 'TP3': ('U10', '27'), 'TP4': ('U10', '24'), 'TP5': ('U10', '23'),
    'Q2': ('K1', '5'), 'R37': ('Q2', '1'), 'R38': ('Q2', '1'), 'D7': ('K1', '5'),
}
ETH = {'R14', 'R15', 'R16', 'R17', 'R18', 'R19', 'R21', 'R22', 'R26', 'R27', 'R28', 'R29', 'L3', 'Y1', 'C25', 'C26', 'C27', 'C28', 'C29', 'C30', 'C31', 'C32', 'C33', 'C34', 'C35', 'C36', 'C37', 'C38', 'C39', 'C40'}
ARKA = {'U12', 'U14', 'R39', 'R40', 'R41', 'C52', 'C53', 'C54', 'C49', 'C46', 'C47', 'C48', 'C28', 'C29', 'C30', 'C31', 'C32', 'C33', 'C35', 'C36', 'C37', 'C38', 'Y1', 'C39', 'C40', 'R27', 'R28'}

def kur(xml, W=W, H=H):
    p = Pano(xml, W, H, katman=4, yuvarlak=2.0)
    y = Yer(p, W, H)
    for ref, (x, yy, rot, arka, tht) in SABIT.items():
        y.sabit_ekle(ref, x, yy, rot, arka, tht)
    sonra = [r for r in A if r not in SABIT]
    yerlesti = set(SABIT)
    bekleyen = list(sonra)
    guard = 0
    while bekleyen and guard < 500:
        guard += 1
        r = bekleyen.pop(0)
        ref, pin = A[r]
        if ref not in yerlesti:
            bekleyen.append(r); continue
        pos = pad_konum(p.fps[ref], pin)
        if not pos:
            raise KeyError((r, ref, pin))
        konum = (p.fps[ref].GetPosition().x / 1e6, p.fps[ref].GetPosition().y / 1e6)
        # capa pad'i konumu
        ap = pos[0]
        sonuc = y.pasif_ekle(r, ap, r in ARKA, rmax=40.0, bos=0.9 if r in ETH else 0.3)
        yerlesti.add(r)
    assert not bekleyen, bekleyen
    eksik = set(p.parcalar) - set(p.fps)
    assert not eksik, eksik
    p.netleri_ata()
    return p, y

if __name__ == '__main__':
    p, y = kur(sys.argv[1])
    p.kaydet(sys.argv[2])
    print('kaydedildi', len(p.fps))
