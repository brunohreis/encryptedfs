import logging
from cryptography.fernet import Fernet

# Logging configuration
logging.basicConfig(
    filename='log.txt',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# The key generation should be called only once to create a key file
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    print("Chave 'secret.key' gerada com sucesso!")

def load_cipher() -> Fernet:
    try:
        with open("secret.key", "rb") as key_file:
            key = key_file.read()
    except FileNotFoundError:
        # If the key file does not exist, generate a new key
        generate_key()
        return load_cipher()
    return Fernet(key)

def encrypt_data(cipher: Fernet, data: bytes) -> bytes:
    # The original data is logged before encryption
    logging.info("Original data: %s", data.decode(errors='ignore'))
    encrypted = cipher.encrypt(data)
    # The encrypted data is logged after encryption
    logging.info("Encrypted data: %s", encrypted.decode(errors='ignore'))
    return encrypted

def decrypt_data(cipher: Fernet, data: bytes) -> bytes:
    # The encrypted data is logged before decryption
    logging.info("Encrypted data for decryption: %s", data.decode(errors='ignore'))
    decrypted = cipher.decrypt(data)
    # The decrypted data is logged after decryption
    logging.info("Decrypted data: %s", decrypted.decode(errors='ignore'))
    return decrypted




