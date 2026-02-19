import os
from security.encryption import generate_key

KEY_FILE = "security/secret.key"

def save_key(key):
    with open(KEY_FILE, "wb") as f:
        f.write(key)

def load_key():
    if not os.path.exists(KEY_FILE):
        key = generate_key()
        save_key(key)
        return key
    with open(KEY_FILE, "rb") as f:
        return f.read()
