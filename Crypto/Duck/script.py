#!/usr/bin/env python3
import base64
import string
import json
from pathlib import Path

# Configuration
SECRET_FILE = Path("secret.txt")

# Substitution Table (cipher -> plain)
SUB_TABLE = {
    'a': 'j', 'b': 'y', 'c': 'n', 'd': 'c', 'e': 'r', 'f': 'g', 'g': 'v',
    'h': 'k', 'j': 'o', 'k': 'd', 'l': 's', 'm': 'h', 'n': 'w', 'o': 'l',
    'p': 'a', 'q': 'p', 'r': 'e', 's': 't', 't': 'i', 'v': 'm', 'w': 'b',
    'y': 'f', 'z': 'u'
}

def rotate_text(text, n):
    """Caesar shift helper."""
    low = string.ascii_lowercase
    up = string.ascii_uppercase
    trans = str.maketrans(low + up, low[n:] + low[:n] + up[n:] + up[:n])
    return text.translate(trans)

def vigenere_decrypt(text, key):
    """Vigenere decryption helper."""
    key = key.lower()
    res = []
    ki = 0
    for char in text:
        if char.isalpha():
            start = ord('a') if char.islower() else ord('A')
            shift = ord(key[ki % len(key)]) - ord('a')
            res.append(chr((ord(char) - start - shift) % 26 + start))
            ki += 1
        else:
            res.append(char)
    return "".join(res)

def apply_substitution(text):
    """Apply the final monoalphabetic substitution table."""
    res = []
    for char in text:
        low = char.lower()
        if low in SUB_TABLE:
            plain = SUB_TABLE[low]
            res.append(plain.upper() if char.isupper() else plain)
        else:
            res.append(char)
    return "".join(res)

def main():
    if not SECRET_FILE.exists():
        print(f"Error: {SECRET_FILE} not found.")
        return

    content = SECRET_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
    line3 = content[2].strip("=")
    dot_lines = content[3:7]

    print("[*] Decrypting hint lines...")
    # These lines are: reverse -> Caesar +12 -> Vigenere (key: sword/dswor)
    keys = ["dswor", "sword", "", ""]
    for line, key in zip(dot_lines, keys):
        processed = rotate_text(line.lstrip(".").strip()[::-1], 12)
        if key:
            processed = vigenere_decrypt(processed, key)
        print(f"  {processed}")

    print("\n[*] Decrypting main layer...")
    # Layer 3: reverse -> Caesar +12 -> Vigenere (key: words) -> Base64
    rev3 = line3[::-1]
    rot3 = rotate_text(rev3, 12)
    vig3 = vigenere_decrypt(rot3, "words")
    
    # Base64 decode handles missing padding usually, but we'll add it if needed
    decoded = base64.b64decode(vig3 + "==").decode("utf-8", errors="replace")
    
    print("[*] Final substitution layer...")
    final_lines = decoded.strip().splitlines()
    for line in final_lines:
        dec = apply_substitution(line)
        print(f"  {dec}")
        if "THJCC{" in dec:
            print(f"\n[+] Flag: {dec}")

if __name__ == "__main__":
    main()
