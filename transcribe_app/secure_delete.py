# transcribe_app/secure_delete.py

import os

def secure_delete(file_path: str, passes: int = 3):
    """
    Securely deletes a file by overwriting it with random data before removing it.
    
    :param file_path: The path to the file to be securely deleted.
    :param passes: Number of overwrite passes.
    """
    if not os.path.exists(file_path):
        print(f"{file_path} does not exist.")
        return
    
    file_size = os.path.getsize(file_path)
    try:
        with open(file_path, "r+b") as f:
            for _ in range(passes):
                f.seek(0)
                f.write(os.urandom(file_size))
        os.remove(file_path)
        print(f"File {file_path} securely deleted.")
    except Exception as e:
        print(f"Error securely deleting file {file_path}: {e}")
