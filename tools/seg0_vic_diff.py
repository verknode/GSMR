"""Raised in a parallel investigation, not this repository's own idea: subtract
seg0 (dbbi, 91 letters) from the already-solved phase-3.2.2 VIC plaintext
(also 91 letters -- not a coincidence anyone chose, both lengths are fixed
puzzle facts), letter by letter mod 26. The result spells "VIC" at positions
1, 4, 21 and "YOUWON" at positions 22-27, followed by a 64-letter tail.

Reproduced here from this repository's own data/seg0.txt, then checked with a
real permutation null (shuffle seg0's own letters, keep the same 91-length VIC
plaintext fixed, recompute) instead of trusting the probability quoted
alongside the finding. Section 47 has the numbers and the correction: "VIC" as
a scattered subsequence is not rare (~69% of shuffles produce it somewhere),
so the entire signal is in "YOUWON" landing as a contiguous dictionary word
(~0.9% of shuffles), not in "VIC" independently confirming it.
"""
import hashlib

SEG0 = open("data/seg0.txt").read().strip().upper()
VIC_PLAINTEXT = ("INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTER"
                 "HALFANDTHEYALSONEEDFUNDSTOLIVE")


def diff(a: str, b: str) -> str:
    return "".join(chr((ord(x) - ord(y)) % 26 + 65) for x, y in zip(a, b))


def tail64() -> str:
    return diff(SEG0, VIC_PLAINTEXT)[27:]


def base26_bytes(s: str) -> bytes:
    vals = [ord(c) - 65 for c in s.upper()]
    out = bytearray()
    for i in range(0, len(vals) - 1, 2):
        out.append((vals[i] * 26 + vals[i + 1]) % 256)
    return bytes(out)


def candidates():
    full = diff(SEG0, VIC_PLAINTEXT)
    t = tail64()
    for base in (full, t, "youwon" + t, "YOUWON" + t, "vic" + t):
        yield base
        yield base.lower()
        yield hashlib.sha256(base.encode()).hexdigest()
    yield base26_bytes(t).hex()


if __name__ == "__main__":
    d = diff(SEG0, VIC_PLAINTEXT)
    assert d[0] == "V" and d[3] == "I" and d[20] == "C" and d[21:27] == "YOUWON"
    print("diff:", d)
    print("64-letter tail:", tail64())
    for c in candidates():
        print(c)
