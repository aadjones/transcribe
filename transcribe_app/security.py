from cryptography.fernet import Fernet


def generate_key() -> bytes:
    """
    Generates a new Fernet key.
    In production, you should securely store this key.
    """
    return Fernet.generate_key()


def encrypt_file(input_filename: str, output_filename: str, key: bytes) -> None:
    """
    Encrypts the contents of input_filename using the provided key and writes
    the ciphertext to output_filename.
    """
    fernet = Fernet(key)
    with open(input_filename, "rb") as infile:
        data = infile.read()
    encrypted_data = fernet.encrypt(data)
    with open(output_filename, "wb") as outfile:
        outfile.write(encrypted_data)


def decrypt_file(input_filename: str, output_filename: str, key: bytes) -> None:
    """
    Decrypts the contents of input_filename using the provided key and writes
    the plaintext to output_filename.
    """
    fernet = Fernet(key)
    with open(input_filename, "rb") as infile:
        encrypted_data = infile.read()
    decrypted_data = fernet.decrypt(encrypted_data)
    with open(output_filename, "wb") as outfile:
        outfile.write(decrypted_data)
