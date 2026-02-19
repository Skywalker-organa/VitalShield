from security.encryption import generate_key, encrypt_data, decrypt_data
key=generate_key()
data="blood pressure high"
encrypted=encrypt_data(data,key)
print("encrypted: ",encrypted)

decrypted=decrypt_data(encrypted,key)
print("decrypted: ", decrypted)