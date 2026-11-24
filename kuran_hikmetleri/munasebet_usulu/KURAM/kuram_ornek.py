"""Usul örnekleri: iki kısa sûrenin L0 kodlaması. BU BİR TEFSİR DEĞİL, KODLAMA USULÜNÜN SINAMA MALZEMESİDİR.
Her atom: sûre:âyet, kelime aralığı [b, s) (kaynak âyetin kelime sırası), biçim (usul notasyonunda), örtük (varsa).
Bağlar: (âyet, âyet, bağ, derece); derece daima 'hikmet ihtimali'dir, murâd-ı ilâhî iddiası değildir (F 3-I 318)."""
ORNEK = {
    103: {
        'kelime': {1: 1, 2: 4, 3: 9},
        'atomlar': [
            ('103:1', 0, 1, 'a1', '⟐(Asr) ⊢ ↑!(⟨Cevap⟩)', None),
            ('103:2', 0, 4, 'a2', '↑!(∀x∈İnsan.Hüsran(x))', None),
            ('103:3', 0, 2, 'a3', 'İnsan ∖ Mümin4', None),
            ('103:3', 2, 3, 'v1', 'İman(x)', None),
            ('103:3', 3, 5, 'v2', 'SalihAmel(x)', None),
            ('103:3', 5, 7, 'v3', 'TevasiHak(x)', None),
            ('103:3', 7, 9, 'v4', 'TevasiSabr(x)', None),
        ],
        'baglar': [('103:1', '103:2', 'İstidlâl', 'hikmet ihtimali'), ('103:2', '103:3', 'Takyîd', 'hikmet ihtimali')],
    },
    112: {
        'kelime': {1: 4, 2: 2, 3: 4, 4: 5},
        'atomlar': [
            ('112:1', 0, 1, 'b1', 'O(Söyle(Peygamber))', '⟨Allah → Peygamber⟩'),
            ('112:1', 1, 4, 'b2', 'hüve[Allah] ∧ Ahad(Allah)', None),
            ('112:2', 0, 2, 'b3', 'Allah{Samed}', None),
            ('112:3', 0, 2, 'b4', '¬∃x.Doğur(Allah → x)', None),
            ('112:3', 2, 4, 'b5', '¬∃y.Doğur(y → Allah)', None),
            ('112:4', 0, 5, 'b6', '¬∃x.Küfüv(x, Allah)', '⟨Allah ≇ x⟩'),
        ],
        'baglar': [('112:1', '112:2', 'Tafsîl', 'hikmet ihtimali'), ('112:2', '112:3', 'Tefrî‘', 'hikmet ihtimali'), ('112:3', '112:4', 'Te’kîd', 'hikmet ihtimali')],
    },
}
SEKIZ_BAG = ('Ta’lîl', 'Tefrî‘', 'Tafsîl', 'İcmâl', 'Mukâbele', 'İstidlâl', 'Takyîd', 'Temsîl', 'Te’kîd')   # F 6.1'deki sekiz bağ + İcmâl (Tafsîl'in tersi) -- sekiz başlık, dokuz ad
