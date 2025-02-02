## **Benchmarking with LibriSpeech**

This section describes how to download and prepare the LibriSpeech dataset and then run the benchmark scripts to evaluate the Whisper transcription pipeline.

### **1\. Download the LibriSpeech Dataset**

For initial benchmarking, we recommend using the `dev-clean` subset of LibriSpeech. Download it from OpenSLR:

**Direct Download:**  
Visit http://www.openslr.org/resources/12/dev-clean.tar.gz  
or run the following command in your terminal:

```
wget http://www.openslr.org/resources/12/dev-clean.tar.gz
```

### **2\. Extract the Dataset**

After downloading, extract the archive with the following command:

```
tar -xzvf dev-clean.tar.gz
````

This will create a directory structure such as `LibriSpeech/dev-clean/` containing subdirectories for each speaker and chapter.
Move this directory to the root of the project.

### **3\. Prepare the Benchmark Data**

A script is provided to convert the FLAC files (the native audio format of LibriSpeech) to WAV format and to extract individual transcript files. This script will:

* Traverse the LibriSpeech directory structure,  
* Convert each FLAC file to a WAV file using `ffmpeg`, and  
* Write out the corresponding transcript (one per utterance) into the appropriate directory.

**Prerequisites:**

Make sure [ffmpeg](https://ffmpeg.org/) is installed on your system.  
On macOS, you can install it via Homebrew:

```
brew install ffmpeg
```

**Running the Script:**

Run the prepare_librispeech.py script from the project root:

```
python scripts/prepare_librispeech.py
```

This script will populate the following directories. You may have to create empty
directories first before running the script.

* `benchmark_data/audio/` – containing the converted WAV files.  
* `benchmark_data/transcripts/` – containing the corresponding transcript text files.

### **4\. Run the Benchmark**

Once the benchmark data is prepared, you can run the benchmark script to evaluate transcription accuracy. The benchmark script uses Jiwer to compute the Word Error Rate (WER).

From the project root, run:

```
python -m benchmarks.benchmark --model tiny --max-files 10
````

This command will:

* Load the specified Whisper model (in this case, `tiny`),  
* Process up to 10 randomly selected audio files from `benchmark_data/audio/`,  
* Compare the resulting transcriptions against the ground truth transcripts in `benchmark_data/transcripts/`, and  
* Compute and display the WER.

### **5\. Customization**

* **Model Selection:**  
  Change the `--model` parameter to use a different Whisper model (e.g., `base`, `small`, `medium`, `large`).  
* **Dataset Size:**  
  Omit the `--max-files` parameter to run the benchmark on the entire dataset.


