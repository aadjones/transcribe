import os

from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

# Retrieve your Hugging Face API token
HF_API_TOKEN = os.environ.get("HF_API_TOKEN")
print("Loaded HF_API_TOKEN:", HF_API_TOKEN)  # Remove or comment out once confirmed

if HF_API_TOKEN is None:
    print(
        "Warning: HF_API_TOKEN not set. Please add it to your .env file or environment variables."
    )
