"""Chronological-order concatenation of every token the puzzle confirms it
revealed, in the order the creator actually reveals them across stages --
not permuted (section 38), not interleaved (section 38), not the community's
seven-token XOR set (section 26). Growing stage-by-stage prefixes are
included, since a solver reading the puzzle in order accumulates exactly
these prefixes before reaching the end.
"""
import hashlib

CHAIN = [
    "gsmg.io/theseedisplanted",
    "theflowerblossomsthroughwhatseemstobeaconcretesurface",
    "matrixsumlist", "enter",
    "lastwordsbeforearchichoice", "thispassword",
    "shabef", "ourfirsthintisyourlastcommand",
    "causality",
    "Safenet", "Luna", "HSM", "11110",
    "0x736B6E616220726F662074756F6C69616220646E6F63657320666F206B6E697262206E6F20726F6C6C65636E61684320393030322F6E614A2F33302073656D695420656854",
    "B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 b - - 0 1",
    "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple",
    "yinyang",
]

def candidates():
    seen = set()
    running = ""
    for tok in CHAIN:
        running += tok
        seen.add(running)
    running_sp = ""
    for tok in CHAIN:
        running_sp = (running_sp + " " + tok).strip()
        seen.add(running_sp)
    seen.add("".join(CHAIN))
    seen.add("".join(CHAIN[::-1]))
    seen.add(" ".join(CHAIN))
    return sorted(seen)

def forms(s):
    yield s
    yield s.lower()
    yield hashlib.sha256(s.encode()).hexdigest()
    yield hashlib.sha256(s.encode()).hexdigest().upper()

if __name__ == "__main__":
    for c in candidates():
        for pw in forms(c):
            print(pw)
