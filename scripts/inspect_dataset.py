import sys
import os
# Add the parent directory (repository root) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datasets import load_dataset
from transcribe_app.config import HF_API_TOKEN

def main():
    # Load the United-Syn-Med dataset. Make sure that you have authenticated via HF_API_TOKEN.
    dataset = load_dataset("united-we-care/United-Syn-Med", split="train", use_auth_token=HF_API_TOKEN)
    
    print(f"Total samples in dataset: {len(dataset)}")
    
    # Inspect the structure of the first sample.
    sample = dataset[0]
    print("Keys in the first sample:")
    for key in sample.keys():
        print(f" - {key}")
    
    print("\nComplete structure of the first sample:")
    for key, value in sample.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main() 