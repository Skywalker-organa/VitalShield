from cryptography.fernet import Fernet, InvalidToken

def generate_key():
    return Fernet.generate_key()

def encrypt_data(data, key):
    f = Fernet(key)
    return f.encrypt(data.encode())

def decrypt_data(encrypted_data, key):
    f = Fernet(key)
    try:
        return f.decrypt(encrypted_data).decode()
    except InvalidToken:
        return "⚠️ Corrupted or invalid encrypted data"
