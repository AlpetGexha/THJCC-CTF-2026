import hashlib
import json
import math
import multiprocessing
import os
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import gmpy2
from sympy import Matrix

E_val = 65537
OUTPUT_PATH = Path("output.txt")
KEY_BYTES = 500

def factor_n(n):
    n = gmpy2.mpz(n)
    if gmpy2.is_prime(n): return {n: 1}
    def pollard_rho(n):
        if n % 2 == 0: return gmpy2.mpz(2)
        x, y, d, c = gmpy2.mpz(2), gmpy2.mpz(2), gmpy2.mpz(1), gmpy2.mpz(1)
        f = lambda z: (z * z + c) % n
        while d == 1:
            x, y = f(x), f(f(y))
            d = gmpy2.gcd(abs(x - y), n)
            if d == n:
                c += 1
                x, y, d = gmpy2.mpz(2), gmpy2.mpz(2), gmpy2.mpz(1)
        return d
    factors = {}
    curr = n
    while curr > 1:
        if gmpy2.is_prime(curr):
            factors[int(curr)] = factors.get(int(curr), 0) + 1
            break
        p = pollard_rho(curr)
        while not gmpy2.is_prime(p): p = pollard_rho(p)
        count = 0
        while curr % p == 0:
            count += 1
            curr //= p
        factors[int(p)] = count
    return factors

def decrypt_sample(args):
    idx, c, n, center, E = args
    factors = factor_n(n)
    phi = gmpy2.mpz(1)
    for p, k in factors.items(): phi *= (gmpy2.mpz(p) - 1) * (gmpy2.mpz(p)**(k - 1))
    d = gmpy2.invert(gmpy2.mpz(E), phi)
    m = gmpy2.powmod(gmpy2.mpz(c), d, gmpy2.mpz(n))
    return idx, (int((m - center) % n), int(n))

def decrypt_rsa_residues(rsa_outputs):
    center = 1 << (500 * 8 - 1)
    print(f"[*] Decrypting {len(rsa_outputs)} RSA samples in parallel...")
    args = [(i, c, n, center, E_val) for i, (c, n) in enumerate(rsa_outputs, 1)]
    residues = [None] * len(rsa_outputs)
    with multiprocessing.Pool() as pool:
        for i, res in pool.imap_unordered(decrypt_sample, args):
            residues[i - 1] = res
            if i % 200 == 0: print(f"[+] Decrypted {i}/{len(rsa_outputs)}")
    return residues

def crt_moments(residues):
    s1, s2, mod = gmpy2.mpz(0), gmpy2.mpz(0), gmpy2.mpz(1)
    for r, n in residues:
        r, n = gmpy2.mpz(r), gmpy2.mpz(n)
        inv = gmpy2.invert(mod, n)
        r1, r2 = r % n, (r * r) % n
        k1, k2 = ((r1 - s1) % n) * inv % n, ((r2 - s2) % n) * inv % n
        s1, s2 = s1 + mod * k1, s2 + mod * k2
        mod *= n
    return s1, s2, mod

def integer_roots_quadratic(c0, c1, c2):
    roots = set()
    c0, c1, c2 = map(gmpy2.mpz, (c0, c1, c2))
    if c2 == 0:
        if c1 != 0 and (-c0) % c1 == 0: roots.add(int((-c0) // c1))
        return roots
    disc = c1 * c1 - 4 * c2 * c0
    if disc < 0: return roots
    s, rem = gmpy2.isqrt_rem(disc)
    if rem != 0: return roots
    for num in (-c1 + s, -c1 - s):
        if num % (2 * c2) == 0: roots.add(int(num // (2 * c2)))
    return roots

def recover_shifted_key(residues):
    bound = 1 << (KEY_BYTES * 8 - 1)
    # Subset of 300 is usually plenty and much faster in sympy
    lll_size = min(len(residues), 300)
    print(f"[*] Recovering key (LLL size {lll_size})...")
    s1, s2, mod = crt_moments(residues[:lll_size])
    basis = Matrix([[int(mod), 0, 0], [-int(s1), bound, 0], [-int(s2), 0, bound * bound]])
    reduced = basis.lll()
    print("[+] LLL reduction completed")
    
    best_support, best_root = -1, None
    for row in reduced.tolist():
        c0, c1, c2 = int(row[0]), int(row[1] // bound), int(row[2] // (bound * bound))
        if c0 == 0 and c1 == 0 and c2 == 0: continue
        for root in integer_roots_quadratic(c0, c1, c2):
            if abs(root) > bound: continue
            support = sum(1 for r, n in residues if int(root % n) == r)
            if support > best_support: best_support, best_root = support, root
            
    if best_root is None: raise RuntimeError("Key recovery failed")
    print(f"[+] Key found! Support: {best_support}/{len(residues)}")
    return best_root

def main():
    if not OUTPUT_PATH.exists(): raise FileNotFoundError("output.txt not found")
    data = json.loads(OUTPUT_PATH.read_text())
    residues = decrypt_rsa_residues(data["rsa_outputs"])
    shifted_key = recover_shifted_key(residues)
    
    bits = ["1" if int(shifted_key % n) == r else "0" for r, n in residues]
    secret_data = int("".join(bits), 2).to_bytes(len(bits) // 8, "big")
    aes_key = hashlib.sha256(secret_data).digest()
    cipher = AES.new(aes_key, AES.MODE_CBC, bytes.fromhex(data["iv"]))
    flag = unpad(cipher.decrypt(bytes.fromhex(data["ciphertext"])), 16)
    print(f"\n[+] Flag: {flag.decode()}")

if __name__ == "__main__":
    main()
