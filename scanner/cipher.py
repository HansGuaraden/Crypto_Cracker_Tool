# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


def derive_key(password: bytes, salt: bytes, length: int = 32) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        iterations=100000,
    )
    return kdf.derive(password)


def encrypt_data(data: bytes, password: bytes) -> bytes:
    salt = os.urandom(16)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return salt + nonce + ciphertext


def decrypt_data(encrypted: bytes, password: bytes) -> bytes:
    salt = encrypted[:16]
    nonce = encrypted[16:28]
    ciphertext = encrypted[28:]
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)


def generate_auth_token(secret: bytes, message: bytes) -> str:
    return hmac.new(secret, message, hashlib.sha256).hexdigest()


def verify_auth_token(secret: bytes, message: bytes, token: str) -> bool:
    expected = generate_auth_token(secret, message)
    return hmac.compare_digest(expected, token)


def obfuscate(data: bytes, key: int = 0xAA) -> bytes:
    return bytes([b ^ key for b in data])


def deobfuscate(data: bytes, key: int = 0xAA) -> bytes:
    return obfuscate(data, key)


def hash_data(data: bytes, algorithm: str = "sha256") -> str:
    if algorithm == "sha256":
        return hashlib.sha256(data).hexdigest()
    elif algorithm == "sha512":
        return hashlib.sha512(data).hexdigest()
    elif algorithm == "md5":
        return hashlib.md5(data).hexdigest()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")


def base64_encode(data: bytes) -> str:
    return base64.b64encode(data).decode('utf-8')


def base64_decode(data: str) -> bytes:
    return base64.b64decode(data)