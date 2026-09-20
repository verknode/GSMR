"""Permutation null for section 47's seg0-minus-VIC-plaintext finding.

Shuffles seg0's own 91 letters (keeping its exact letter multiset) against the
fixed, real phase-3.2.2 VIC plaintext, N times, and counts how often the same
landmarks appear: the literal claimed pattern (V at 1, I at 4, C at 21, YOUWON
at 22-27 together), "VIC" as a loose in-order subsequence anywhere, and any
contiguous 6-letter English dictionary word anywhere. Needs a word list at
the path below; swap in any list of one-word-per-line 6-letter words.

Usage: seg0_vic_diff_null.py <six-letter-wordlist> [N]
"""
import random, sys
from seg0_vic_diff import SEG0, VIC_PLAINTEXT, diff


def run(wordlist_path: str, n: int = 200_000, seed: int = 1) -> None:
    words6 = {w.strip().upper() for w in open(wordlist_path) if len(w.strip()) == 6}
    random.seed(seed)
    letters = list(SEG0)
    exact = subseq = anyword = 0
    for _ in range(n):
        random.shuffle(letters)
        d = diff(letters, VIC_PLAINTEXT)
        if d[0] == "V" and d[3] == "I" and d[20] == "C" and d[21:27] == "YOUWON":
            exact += 1
        i = d.find("V")
        if i != -1:
            j = d.find("I", i + 1)
            if j != -1 and d.find("C", j + 1) != -1:
                subseq += 1
        if any(d[p:p + 6] in words6 for p in range(len(d) - 5)):
            anyword += 1
    print(f"N={n}")
    print(f"exact claimed pattern: {exact}/{n}")
    print(f"'VIC' as any in-order subsequence: {subseq}/{n} = {subseq/n:.4f}")
    print(f"any dictionary 6-letter word anywhere: {anyword}/{n} = {anyword/n:.4f}")


if __name__ == "__main__":
    run(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 200_000)
