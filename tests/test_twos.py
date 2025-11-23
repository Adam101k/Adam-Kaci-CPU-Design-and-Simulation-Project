import pytest
from twos import encode_twos_complement, decode_twos_complement

def test_examples():
    e = encode_twos_complement(13)
    assert e["overflow"] == 0
    assert e["hex"] == "0x0000000D"
    assert e["bin"].endswith("00001101")

    e = encode_twos_complement(-13)
    assert e["overflow"] == 0
    assert e["hex"] == "0xFFFFFFF3"
    assert e["bin"].endswith("11110011")

    assert encode_twos_complement(2**31)["overflow"] == 1

    assert decode_twos_complement("0"*31 + "1")["value"] == 1
    assert decode_twos_complement("1" + "0"*31)["value"] == -2**31

@pytest.mark.parametrize("val", [-(2**31), -1, -13, -7, 0, 13, (2**31)-1])
def test_boundaries(val):
    enc = encode_twos_complement(val)
    roundtrip = decode_twos_complement(enc["bin"])["value"]
    assert roundtrip == val
