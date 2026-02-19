from security.encryption import generate_key
from security.key_manager import save_key, load_key

def initialize_key():
    existing_key=load_key()
    if existing_key is None:
        key=generate_key()
        save_key(key)
        print("New AES key generated and saved.")
    else:
        print("AES key already")