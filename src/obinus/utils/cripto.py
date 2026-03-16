from Crypto.Cipher import AES
from Crypto.Hash import MD5
from hashlib import md5
import base64
import os


def evp_bytes_to_key(password, salt, key_len, iv_len):
    d = b""
    while len(d) < key_len + iv_len:
        d_i = MD5.new(d + password + salt).digest()
        d += d_i
    return d[:key_len], d[key_len : key_len + iv_len]


def encrypt(message, password):
    salt = os.urandom(8)

    key, iv = evp_bytes_to_key(password.encode(), salt, 32, 16)

    cipher = AES.new(key, AES.MODE_CBC, iv)

    message = message.encode()
    pad = 16 - len(message) % 16
    message += bytes([pad]) * pad

    encrypted = cipher.encrypt(message)

    return base64.b64encode(b"Salted__" + salt + encrypted).decode()


def decrypt(encrypted_b64, password):
    # 1. Decodifica o Base64
    data = base64.b64decode(encrypted_b64)

    # 2. Extrai o Salt (bytes 8 a 16)
    salt = data[8:16]
    ciphertext = data[16:]

    # 3. Derivação de Key e IV (O segredo da compatibilidade)
    # Precisamos de 32 bytes para Key + 16 bytes para IV = 48 bytes total
    password_bytes = password.encode("utf-8")
    hasher = md5(password_bytes + salt).digest()
    result = hasher
    while len(result) < 48:
        hasher = md5(hasher + password_bytes + salt).digest()
        result += hasher

    key = result[:32]
    iv = result[32:48]

    # 4. Descriptografar
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(ciphertext)

    # 5. Remover o Padding PKCS7 manualmente (evita erros de unpad)
    padding_len = decrypted[-1]
    # Se o padding_len for lixo (ex: 253), a chave está errada
    if padding_len < 1 or padding_len > 16:
        return "Erro: Chave incorreta ou falha na integridade (Padding inválido)"

    final_text = decrypted[:-padding_len]

    try:
        return final_text.decode("utf-8")
    except UnicodeDecodeError:
        return "Erro: Descriptografou, mas o resultado não é um texto UTF-8 válido."
