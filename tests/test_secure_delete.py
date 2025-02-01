import os
from transcribe_app.secure_delete import secure_delete

def test_secure_delete(tmp_path):
    # Create a temporary file and write some dummy content.
    test_file = tmp_path / "dummy.txt"
    test_file.write_text("sensitive data")
    assert test_file.exists(), "File should exist before deletion."
    
    # Securely delete the file.
    secure_delete(str(test_file))
    
    # Assert that the file no longer exists.
    assert not test_file.exists(), "File should be deleted securely."
