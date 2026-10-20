import os
from breadboard import Breadboard

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
TOP_P, TOP_N = ("top", "+"), ("top", "-")
BOT_P, BOT_N = ("bot", "+"), ("bot", "-")


def s1(path, with_load=False):
    b = Breadboard(title=None)
    b.lead("VS+", (2, TOP_P), "+10 V", color="red")
    b.lead("VS-", (2, BOT_N), "−", color="black")
    b.wire((2, TOP_P), (2, "j"), color="red")
    b.resistor("R1", (2, "h"), (8, "h"), 2200, "2,2 kΩ")
    b.resistor("R2", (8, "g"), (8, BOT_N), 3300, "3,3 kΩ")
    b.resistor("R3", (8, "f"), (14, "f"), 2200, "2,2 kΩ")
    b.lead("O+", (14, "g"), "+", color="red")
    b.lead("O-", (14, BOT_N), "−", color="black")
    expected = {"VS+": [("VS+", 1), ("R1", 1)], "B": [("R1", 2), ("R2", 1), ("R3", 1)],
                "G": [("R2", 2), ("VS-", 1), ("O-", 1)], "O": [("R3", 2), ("O+", 1)]}
    if with_load:
        b.resistor("RL", (14, "j"), (14, BOT_N), 3520, "3,52 kΩ")
        expected["O"] += [("RL", 1)]
        expected["G"] += [("RL", 2)]
    b.check(expected)
    return b.draw(path, figsize=(12, 5.0))


def s3(path):
    b = Breadboard(title=None)
    b.lead("VS1+", (2, "j"), "+12 V", color="red")
    b.lead("VS1-", (2, BOT_N), "−", color="black")
    b.resistor("R1", (2, "f"), (12, "f"), 15000, "15 kΩ", below=True)
    b.resistor("R2", (2, "h"), (8, "h"), 15000, "15 kΩ", below=True)
    b.lead("VS2+", (8, "g"), "+5 V", color="red")
    b.lead("VS2-", (8, BOT_N), "−", color="black")
    b.resistor("R5", (8, "f"), (8, BOT_N), 1000, "1 kΩ")
    b.resistor("R4", (8, "j"), (14, "j"), 1000, "1 kΩ")
    b.resistor("R3", (12, "h"), (14, "h"), 3900, "3,9 kΩ", below=True)
    b.resistor("R6", (14, "g"), (14, BOT_N), 8200, "8,2 kΩ")
    b.lead("C", (14, "f"), "C", color="magenta")
    b.lead("D", (16, BOT_N), "D", color="black")
    b.check({"M": [("VS1+", 1), ("R1", 1), ("R2", 1)],
             "G": [("VS1-", 1), ("VS2-", 1), ("R5", 2), ("R6", 2), ("D", 1)],
             "P": [("VS2+", 1), ("R2", 2), ("R4", 1), ("R5", 1)],
             "B": [("R1", 2), ("R3", 1)],
             "N": [("R3", 2), ("R4", 2), ("R6", 1), ("C", 1)]})
    return b.draw(path, figsize=(12, 6.0))


if __name__ == "__main__":
    print(s1(os.path.join(OUT, "bb2_s1.png")))
    print(s1(os.path.join(OUT, "bb2_s2.png"), with_load=True))
    print(s3(os.path.join(OUT, "bb2_s3.png")))
