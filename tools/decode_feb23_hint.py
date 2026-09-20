"""Decodes the Feb 23, 2023 creator hint image from PR #30 (section 46): 161
space-separated 8-bit groups. Each byte's bits are reversed (LSB first, not MSB
first), and the resulting character string is reversed as a whole -- both
transforms are the creator's, not a cipher: undo them and the plaintext reads
directly as ASCII.

Usage: decode_feb23_hint.py < data/feb23_bytes.txt
"""
import sys


def decode(bytes_line: str) -> str:
    groups = bytes_line.split()
    chars = [chr(int(b[::-1], 2)) for b in groups]
    return "".join(chars)[::-1]


if __name__ == "__main__":
    print(decode(sys.stdin.read()))
