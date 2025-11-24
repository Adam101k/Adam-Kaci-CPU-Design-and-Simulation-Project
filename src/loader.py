from __future__ import annotations
from typing import List, Tuple
from memory import Bit

def hex_line_to_bits32(line: str) -> Tuple[Bit, ...]:
    s = line.strip().lower()
    if not s: return ()
    s = s.replace("0x","")
    if len(s) < 8: s = ("0"*(8-len(s))) + s
    s = s[-8:]
    val = 0
    for ch in s:
        if "0"<=ch<="9": d = ord(ch)-ord("0")
        elif "a"<=ch<="f": d = 10 + (ord(ch)-ord("a"))
        else: return ()
        val = (val<<4) | d
    return tuple(Bit(bool((val>>i)&1)) for i in range(31,-1,-1))

def load_hex_file(path: str) -> List[Tuple[Bit,...]]:
    out: List[Tuple[Bit,...]] = []
    with open(path,"r",encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            b = hex_line_to_bits32(line)
            if b: out.append(b)
    return out