"""Tests PBKDF2-HMAC-SHA256 key derivation against the recovered blobs, instead
of the classic digest-chaining EVP_BytesToKey every other tool here uses.

Both are compatible with the same "Salted__" + 8-byte-salt header a plain
`openssl enc -aes-256-cbc` blob carries -- passing -pbkdf2 changes only the
derivation, not the visible file format, so a blob's header can't tell you
which one made it. Nothing in this repository had tried PBKDF2 before.

Usage: pbkdf2_crack.py <candidates file, one per line> [iterations...]
Defaults to iteration counts 10000 (OpenSSL's own -pbkdf2 default since
1.1.1), 1000, and the puzzle's own thematic numbers 16, 23, 7.
"""
import base64, ctypes, ctypes.util, hashlib, sys

BLOBS = {
    "salphaseion": ("U2FsdGVkX186tYU0hVJBXXUnBUO7C0+X4KUWnWkCvoZSxbRD3wNsGWVHefvdrd9z"
                    "QvX0t8v3jPB4okpspxebRi6sE1BMl5HI8Rku+KejUqTvdWOX6nQjSpepXwGuN/jJ"),
    "phase322":    ("U2FsdGVkX1+0Wl49gnWTyiimluu7V3+vl7st0gUt9sWDzNLxDmlPMsDSiuW2a46z"
                    "gKlIi8aaqY5gpJPPEzW1n9n3/26qs4zstWtPKF8Zs/BTNN4IiEh4qu18mdC0NAv4"),
}


def load_cosmic(path="data/cosmic-duality.b64"):
    raw = base64.b64decode(open(path).read())
    assert raw[:8] == b"Salted__"
    return raw[8:16], raw[16:]


_lib = ctypes.CDLL(ctypes.util.find_library("crypto"))


class _AES_KEY(ctypes.Structure):
    _fields_ = [("rd_key", ctypes.c_uint * 60), ("rounds", ctypes.c_int)]


_lib.AES_set_decrypt_key.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(_AES_KEY)]
_lib.AES_decrypt.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(_AES_KEY)]


def _block(key, ct):
    ak = _AES_KEY()
    _lib.AES_set_decrypt_key(key, 256, ctypes.byref(ak))
    buf = ctypes.create_string_buffer(16)
    _lib.AES_decrypt(ct, buf, ctypes.byref(ak))
    return bytes(buf.raw[:16])


def pbkdf2_key_iv(pw: bytes, salt: bytes, iters: int):
    d = hashlib.pbkdf2_hmac("sha256", pw, salt, iters, dklen=48)
    return d[:32], d[32:48]


def printable_first_block(pw, salt, ct, iters):
    key, iv = pbkdf2_key_iv(pw, salt, iters)
    pt0 = bytes(a ^ b for a, b in zip(_block(key, ct[:16]), iv))
    return sum(32 <= c < 127 for c in pt0), pt0


def padding_check(pw, salt, ct, iters):
    key, iv = pbkdf2_key_iv(pw, salt, iters)
    prev = ct[-32:-16] if len(ct) >= 32 else iv
    last = bytes(a ^ b for a, b in zip(_block(key, ct[-16:]), prev))
    p = last[-1]
    return 1 <= p <= 16 and all(c == p for c in last[16 - p:])


def main():
    cand_path = sys.argv[1]
    iters_list = [int(x) for x in sys.argv[2:]] or [10000, 1000, 16, 23, 7]
    cosmic_salt, cosmic_ct = load_cosmic()

    candidates = [l.rstrip("\n") for l in open(cand_path) if l.strip()]
    print(f"{len(candidates)} candidates x {len(iters_list)} iteration counts")

    for iters in iters_list:
        cosmic_hits = 0
        for line in candidates:
            pw = line.encode()
            pr, _ = printable_first_block(pw, cosmic_salt, cosmic_ct, iters)
            if pr >= 12:
                cosmic_hits += 1
                print(f"[cosmic iters={iters}] pr={pr}/16 pw={line!r}")
        lock_hits = 0
        for name, b64 in BLOBS.items():
            raw = base64.b64decode(b64)
            salt, ct = raw[8:16], raw[16:]
            for line in candidates:
                pw = line.encode()
                if padding_check(pw, salt, ct, iters):
                    lock_hits += 1
                    print(f"[{name} iters={iters}] PAD OK pw={line!r}")
        print(f"iters={iters}: cosmic printable-hits={cosmic_hits} lock-padding-hits={lock_hits}")


if __name__ == "__main__":
    main()
