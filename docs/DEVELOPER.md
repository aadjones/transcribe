# **Developer README**

## **Overview**

**Transcribe** is a cross-platform desktop application for secure, local audio transcription using OpenAI's Whisper model. In addition to the desktop application (with features such as audio recording, transcription, and secure deletion), the project includes modular benchmarking pipelines to evaluate transcription performance. We have recently refactored the benchmarking code into a unified command-line interface (CLI) that supports:

* **Local Benchmarking** (e.g., LibriSpeech or other general audio datasets)  
* **Medical Benchmarking** (using a minimal text normalization pipeline)  
* **Model vs. Model Comparison** on medical datasets, with aggregated metrics (WER, processing time, RTF)

In order for the pipeline to work, you will first need to set up LibriSpeech Benchmarking and Medical Setup. The later sections in this README explain how this is done.

## **Unified Benchmarking Pipeline**

The benchmarking functionality has been refactored to use a single CLI with three subcommands:

* **Local:** Run a benchmark on local audio files (e.g., LibriSpeech).  
* **Medical:** Run a benchmark on medical audio data using a minimal text normalization transform.  
* **Compare:** Run a model-vs-model comparison on the medical dataset and aggregate metrics (WER, processing time, and real-time factor).

### **Running the CLI**

From the project root, use the unified CLI (located in `benchmarks/cli.py`):

```console
python -m benchmarks.cli <subcommand> [options]
```

For example:

* Local Benchmark:  
  ```console
  python -m benchmarks.cli local --model-name tiny --max-files 10
  ```  
    
    
* Medical Benchmark:  
  ```console
  python -m benchmarks.cli medical --model-name tiny --max-samples 10
  ```  
    
* Model Comparison:  
  ```
  python -m benchmarks.cli compare --baseline-model tiny --fine-tuned-model bqtsio/whisper-large-rad --max-samples 10
  ```

Each command uses random sampling to select a subset of files and prints both per-sample and aggregated results.

## **LibriSpeech Benchmarking**

For local benchmarking with LibriSpeech:

1. **Download the Dev-Clean Subset:**  
   ```console
   wget http://www.openslr.org/resources/12/dev-clean.tar.gz
   ```
2. **Extract the Dataset:**  
   ```console
   tar -xzvf dev-clean.tar.gz
   ```  
   **This creates a directory structure such as `LibriSpeech/dev-clean/.`**  
3. **Prepare the Data:**  
   Run the provided script to convert FLAC files to WAV and extract transcripts:  
   ```console
   python scripts/prepare_librispeech.py`
   ```  
   This populates:  
* `benchmark_data/audio/` (WAV files)  
* `benchmark_data/transcripts/` (transcript text files)  
4. **Run the Local Benchmark:**  
   ```console
   python -m benchmarks.cli local --model-name tiny --max-files 10
   ```

## **Medical Setup** 

Some medical datasets (e.g., [United-Syn-Med](https://huggingface.co/datasets/united-we-care/United-Syn-Med)) are gated and require a Hugging Face API key. 

### **Steps to Configure:**

1. **Create or Log In to Your Hugging Face Account:**  
   Visit [Hugging Face](https://huggingface.co) and sign in or create an account.  
2. **Generate an API Token:**  
   In your account settings under Access Tokens, create a new token (e.g., `transcribe-app`) with read permissions, and copy it.  
3. **Set Up Your Local Environment:**  
   Create a `.env` file in the project root and populate it with the following: 
   `HF_API_TOKEN=your_huggingface_api_token_here`
4. **Automatic Loading:**  
   The project's configuration module (`transcribe_app/config.py`) automatically loads the API key from `.env`. The API token is then used in benchmark scripts when loading gated datasets.

   

 


  
