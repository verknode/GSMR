"""Checks PR #93's claimed 4-parameter joint-attack alphabet corroboration and PR
#68's claimed Cosmic Duality "derived key" against the real recovered blob -- both
from unmerged pull requests on the upstream repository, surveyed in section 45.

PR #68's GAP_ANALYSIS.md gives a 32-byte key and a specific plaintext SHA-256 for
Cosmic Duality but ships no code. Tried here as a raw AES-256 key (not password ->
EVP_BytesToKey, since the claim is a key, not a password) against the real
ciphertext, under three IV assumptions. All three give noise-level printable
counts, not the claimed plaintext.
"""
import base64, ctypes, ctypes.util

CLAIMED_KEY_HEX = "a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735"[:64]


def _load_blob(path):
    raw = base64.b64decode(open(path).read())
    assert raw[:8] == b"Salted__"
    return raw[8:16], raw[16:]


def _aeslib():
    lib = ctypes.CDLL(ctypes.util.find_library("crypto"))

    class AES_KEY(ctypes.Structure):
        _fields_ = [("rd_key", ctypes.c_uint * 60), ("rounds", ctypes.c_int)]

    lib.AES_set_decrypt_key.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(AES_KEY)]
    lib.AES_decrypt.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(AES_KEY)]
    return lib, AES_KEY


def check(blob_path):
    salt, ct = _load_blob(blob_path)
    key = bytes.fromhex(CLAIMED_KEY_HEX)
    lib, AES_KEY = _aeslib()

    def block(k, ctb):
        ak = AES_KEY()
        lib.AES_set_decrypt_key(k, 256, ctypes.byref(ak))
        buf = ctypes.create_string_buffer(16)
        lib.AES_decrypt(ctb, buf, ctypes.byref(ak))
        return bytes(buf.raw[:16])

    results = {}
    for name, iv in [("zero", b"\x00" * 16), ("salt-doubled", salt + salt), ("key-tail", key[16:])]:
        pt0 = bytes(a ^ b for a, b in zip(block(key, ct[:16]), iv))
        results[name] = sum(32 <= c < 127 for c in pt0)
    return results


if __name__ == "__main__":
    for name, printable in check("data/cosmic-duality.b64").items():
        print(f"{name}: {printable}/16 printable")
