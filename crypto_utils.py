import logging
from cryptography.fernet import Fernet

# Logging configuration
logging.basicConfig(
    filename='log.txt',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# Fixed keys only for demonstration
key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_data(data: bytes) -> bytes:
    # The original data is logged before encryption
    logging.info("Original data: %s", data.decode(errors='ignore'))
    encrypted = cipher.encrypt(data)
    # The encrypted data is logged after encryption
    logging.info("Encrypted data: %s", encrypted.decode(errors='ignore'))
    return encrypted

def decrypt_data(data: bytes) -> bytes:
    # The encrypted data is logged before decryption
    logging.info("Encrypted data for decryption: %s", data.decode(errors='ignore'))
    decrypted = cipher.decrypt(data)
    # The decrypted data is logged after decryption
    logging.info("Decrypted data: %s", decrypted.decode(errors='ignore'))
    return decrypted
