from yaosfe.circuits import LogicCircuit
from yaosfe.gates import LogicGate

G_XOR = [0, 1, 1, 0]
G_AND = [0, 0, 0, 1]
G_OR  = [0, 1, 1, 1]

# 1-bit Adder: (A0, B0) => (C1, C0)
LC_ADD_1BIT = LogicCircuit(
    [0, 1], [2, 3], [
        LogicGate(2, [0, 1], G_AND), # 2 = AND(0, 1)
        LogicGate(3, [0, 1], G_XOR), # 3 = XOR(0, 1)
    ]
)

# 2-bit Adder: (A1, A0, B1, B0) => (C2, C1, C0)
LC_ADD_2BIT = LogicCircuit(
    [0, 1, 2, 3], [9, 10, 5], [
        # (4, 5) = HalfAdder(1, 3)
        LogicGate(4, [1, 3], G_AND), # 4 = AND(1, 3)
        LogicGate(5, [1, 3], G_XOR), # 5 = XOR(1, 3)

        # (9, 10) = FullAdder(0, 2, 4)
        LogicGate(6, [0, 2], G_AND), # 6  = AND(0, 2)
        LogicGate(7, [0, 2], G_XOR), # 7  = XOR(0, 2)
        LogicGate(8, [4, 7], G_AND), # 8  = AND(4, 7)
        LogicGate(9, [6, 8], G_OR), # 9  = OR(6, 8)
        LogicGate(10, [4, 7], G_XOR), # 10 = XOR(4, 7)
    ]
)

# 3-bit Adder: (A2, A1, A0, B2, B1, B0) => (C3, C2, C1, C0)
LC_ADD_3BIT = LogicCircuit(
    [0, 1, 2, 3, 4, 5], [16, 17, 12, 7], [
        # (6, 7) = HalfAdder(2, 5)
        LogicGate(6, [2, 5], G_AND), # 4 = AND(2, 5)
        LogicGate(7, [2, 5], G_XOR), # 5 = XOR(2, 5)

        # (11, 12) = FullAdder(1, 4, 6)
        LogicGate(8, [1, 4], G_AND), # 8  = AND(1, 4)
        LogicGate(9, [1, 4], G_XOR), # 9  = XOR(1, 4)
        LogicGate(10, [6, 9], G_AND), # 10  = AND(6, 9)
        LogicGate(11, [8, 10], G_OR), # 11  = OR(8, 10)
        LogicGate(12, [6, 9], G_XOR), # 12 = XOR(6, 9)

        # (17, 19) = FullAdder(0, 3, 11)
        LogicGate(13, [0, 3], G_AND), # 13  = AND(0, 3)
        LogicGate(14, [0, 3], G_XOR), # 14  = XOR(0, 3)
        LogicGate(15, [11, 14], G_AND), # 15  = AND(11, 14)
        LogicGate(16, [13, 15], G_OR), # 16  = OR(13, 15)
        LogicGate(17, [11, 14], G_XOR), # 17 = XOR(11, 14)
    ]
)

# 3-bit two numbers average: (A2, A1, A0, B2, B1, B0) => (C2, C1, C0)
LC_AVG_3BIT = LogicCircuit(
    [0, 1, 2, 3, 4, 5], [16, 17, 12], [
        # (6, 7) = HalfAdder(2, 5)
        LogicGate(6, [2, 5], G_AND), # 4 = AND(2, 5)
        LogicGate(7, [2, 5], G_XOR), # 5 = XOR(2, 5)

        # (11, 12) = FullAdder(1, 4, 6)
        LogicGate(8, [1, 4], G_AND), # 8  = AND(1, 4)
        LogicGate(9, [1, 4], G_XOR), # 9  = XOR(1, 4)
        LogicGate(10, [6, 9], G_AND), # 10  = AND(6, 9)
        LogicGate(11, [8, 10], G_OR), # 11  = OR(8, 10)
        LogicGate(12, [6, 9], G_XOR), # 12 = XOR(6, 9)

        # (17, 19) = FullAdder(0, 3, 11)
        LogicGate(13, [0, 3], G_AND), # 13  = AND(0, 3)
        LogicGate(14, [0, 3], G_XOR), # 14  = XOR(0, 3)
        LogicGate(15, [11, 14], G_AND), # 15  = AND(11, 14)
        LogicGate(16, [13, 15], G_OR), # 16  = OR(13, 15)
        LogicGate(17, [11, 14], G_XOR), # 17 = XOR(11, 14)
    ]
)