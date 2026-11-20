import base64
import hashlib
import hmac

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

PASSPHRASE = "Testingsecretcode"
_master = hashlib.scrypt(PASSPHRASE.encode(), salt=b"simple-chat", n=2**14, r=8, p=1, dklen=64)
KEY, MAC_KEY = _master[:32], _master[32:]


def encrypt_message(text: str) -> bytes:
    iv = get_random_bytes(16)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(text.encode("utf-8"), AES.block_size))
    tag = hmac.new(MAC_KEY, iv + ct, hashlib.sha256).digest()
    return base64.b64encode(iv + ct + tag)


def decrypt_message(enc_msg: bytes) -> str:
    raw = base64.b64decode(enc_msg)
    iv, ct, tag = raw[:16], raw[16:-32], raw[-32:]
    expected = hmac.new(MAC_KEY, iv + ct, hashlib.sha256).digest()
    if not hmac.compare_digest(tag, expected):
        raise ValueError("message was tampered with")
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size).decode("utf-8")
