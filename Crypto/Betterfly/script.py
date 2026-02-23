#!/usr/bin/env python3
from pathlib import Path

from encrypt import ChaosStreamCipher


def decrypt_bytes(ciphertext: bytes, key: float) -> bytes:
    cipher = ChaosStreamCipher(key)
    return cipher.decrypt(ciphertext)


def caesar_alpha(text: str, shift: int) -> str:
    out = []
    for ch in text:
        if "a" <= ch <= "z":
            out.append(chr((ord(ch) - ord("a") + shift) % 26 + ord("a")))
        elif "A" <= ch <= "Z":
            out.append(chr((ord(ch) - ord("A") + shift) % 26 + ord("A")))
        else:
            out.append(ch)
    return "".join(out)


def main() -> None:
    enc_path = Path("flag.txt.enc")
    key = 0.123456789

    ciphertext = enc_path.read_bytes()
    plaintext = decrypt_bytes(ciphertext, key)
    raw = plaintext.decode("utf-8", errors="replace")
    final_flag = caesar_alpha(raw, 11)
    print(final_flag)


if __name__ == "__main__":
    main()
