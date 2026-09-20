"""Solves the phase-3 FEN with Stockfish and turns the result into password
candidates, instead of treating the FEN string as opaque text (every prior
concatenation attempt in this file, including section 43's chain, used the raw
FEN). Requires the `stockfish` binary on PATH.

Finding: the position has exactly one legal move. Black's king is in check from
the bishop on h7, and Rb7xh7 is the only way out -- there is nothing to "solve"
beyond that forced recapture.
"""
import hashlib, subprocess

FEN = "B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 b - - 0 1"

def legal_moves():
    out = subprocess.run(
        ["stockfish"], input=f"position fen {FEN}\ngo perft 1\n",
        capture_output=True, text=True, timeout=10,
    ).stdout
    moves = []
    for line in out.splitlines():
        if ":" in line and line.split(":")[0].strip().isalnum() and len(line.split(":")[0].strip()) == 4:
            moves.append(line.split(":")[0].strip())
    return moves

MOVE_FORMS = ["Rxh7", "rxh7", "RXH7", "Rh7", "rh7", "b7h7", "B7H7"]

def candidates():
    return list(MOVE_FORMS)

def forms(s):
    yield s
    yield s.lower()
    yield hashlib.sha256(s.encode()).hexdigest()
    yield hashlib.sha256(s.encode()).hexdigest().upper()

if __name__ == "__main__":
    found = legal_moves()
    assert found == ["b7h7"], f"expected exactly one legal move b7h7, got {found}"
    for c in candidates():
        for pw in forms(c):
            print(pw)
