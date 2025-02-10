import os

from datasets import load_dataset

from transcribe_app.config import HF_API_TOKEN

# Set the Hugging Face token in the environment variable if it exists
if HF_API_TOKEN is not None:
    os.environ["HUGGINGFACE_HUB_TOKEN"] = HF_API_TOKEN
else:
    print("Warning: HF_API_TOKEN is not set in config.py")


def main():
    # Load the dataset from Hugging Face; the token is now picked up from the environment.
    dataset = load_dataset("united-we-care/United-Syn-Med", split="train")

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
