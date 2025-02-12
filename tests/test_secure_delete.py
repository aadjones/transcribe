from transcribe_app.secure_delete import secure_delete
from transcribe_app.security import decrypt_file, encrypt_file, generate_key


def test_generate_key():
    key = generate_key()
    # A Fernet key is a URL-safe base64-encoded 32-byte key;
    # its encoded length is 44 bytes.
    assert isinstance(key, bytes)
    assert len(key) == 44


def test_encrypt_decrypt(tmp_path):
    # Create a temporary file with known content.
    original_content = b"This is a test"
    input_file = tmp_path / "original.txt"
    input_file.write_bytes(original_content)

    key = generate_key()

    # Define paths for the encrypted and decrypted files.
    encrypted_file = tmp_path / "encrypted.enc"
    decrypted_file = tmp_path / "decrypted.txt"

    # Encrypt the original file.
    encrypt_file(str(input_file), str(encrypted_file), key)
    # Verify that the encrypted file exists and its content is different.
    assert encrypted_file.exists()
    encrypted_content = encrypted_file.read_bytes()
    assert encrypted_content != original_content

    # Decrypt the encrypted file.
    decrypt_file(str(encrypted_file), str(decrypted_file), key)
    # Verify that the decrypted content matches the original.
    assert decrypted_file.exists()
    decrypted_content = decrypted_file.read_bytes()
    assert decrypted_content == original_content


def test_secure_delete(tmp_path):
    # Create a temporary file.
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(b"Sensitive data")
    assert test_file.exists()

    # Call secure_delete on the test file.
    secure_delete(str(test_file))
    # After secure deletion, the file should not exist.
    assert not test_file.exists()
