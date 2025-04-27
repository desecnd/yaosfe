
def gen_nbit_inputs(n_bits: int):
    """Generate all binary values made out of n_bits as list of int type bits"""

    for val in range(1 << n_bits):
        bits = [ (val & (1 << i)) >> i for i in range(n_bits - 1, -1, -1) ]
        yield bits

def bits_from_str(bits: str) -> list[int]:
    return [ int(b) for b in bits ]

def bits_to_str(bits: list[int]) -> str:
    return ''.join(str(b) for b in bits)

def bytes_to_hex(b: bytes) -> str:
    return b.hex()

def bytes_from_hex(b: str) -> bytes:
    return bytes.fromhex()