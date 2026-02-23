from Crypto.Util.number import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import hashlib
import os, json
from flags import flag

secret_data = os.urandom(105)

aes_key = hashlib.sha256(secret_data).digest()

iv = os.urandom(16)
cipher = AES.new(aes_key, AES.MODE_CBC, iv)
ciphertext = cipher.encrypt(pad(flag.encode(), AES.block_size))

key = os.urandom(500)

def enc(msg):
    p, q = getPrime(32), getPrime(32)
    N = p * q
    e = 0x10001
    return [pow(bytes_to_long(msg), e, N), N]

output_data = []

for i in ''.join([format(b, '08b') for b in secret_data]):
    if i == '1':
        output_data.append(enc(key))
    elif i == '0':
        output_data.append(enc(os.urandom(500)))

export_data = {
    "iv": iv.hex(),
    "ciphertext": ciphertext.hex(),
    "rsa_outputs": output_data
}

with open('output.txt', 'w') as f:
    json.dump(export_data, f)
