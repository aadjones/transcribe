import os
import subprocess

# Configure these paths to match your setup:
LIBRISPEECH_ROOT = "../LibriSpeech/dev-clean"  # Root of the LibriSpeech subset
AUDIO_OUT_DIR = "../benchmark_data/audio"  # Output directory for WAV files
TRANSCRIPTS_OUT_DIR = (
    "../benchmark_data/transcripts"  # Output directory for transcript text files
)


def convert_flac_to_wav(flac_path, wav_output):
    """Convert a FLAC file to WAV using ffmpeg."""
    cmd = ["ffmpeg", "-y", "-i", flac_path, wav_output]
    try:
        # Capture stdout/stderr to avoid cluttering the console (optional)
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Converted {flac_path} to {wav_output}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {flac_path}: {e.stderr.decode('utf-8')}")
        return False
    return True


def process_transcripts():
    """
    Traverse the LibriSpeech root, convert FLAC files to WAV,
    and write corresponding transcript files.
    """
    # Ensure output directories exist
    os.makedirs(AUDIO_OUT_DIR, exist_ok=True)
    os.makedirs(TRANSCRIPTS_OUT_DIR, exist_ok=True)

    # Walk through the LibriSpeech root
    for speaker in os.listdir(LIBRISPEECH_ROOT):
        speaker_path = os.path.join(LIBRISPEECH_ROOT, speaker)
        if not os.path.isdir(speaker_path):
            continue

        for chapter in os.listdir(speaker_path):
            chapter_path = os.path.join(speaker_path, chapter)
            if not os.path.isdir(chapter_path):
                continue

            # Look for transcript files ending with ".trans.txt"
            # in the chapter directory.
            for file in os.listdir(chapter_path):
                if file.endswith(".trans.txt"):
                    trans_file_path = os.path.join(chapter_path, file)
                    with open(trans_file_path, "r", encoding="utf-8") as f:
                        for line in f:
                            # Each line should be formatted as:
                            # <utterance_id> <transcription>
                            parts = line.strip().split(maxsplit=1)
                            if len(parts) != 2:
                                print(
                                    f"Warning: Malformed line in {trans_file_path}: {line}"
                                )
                                continue

                            utterance_id, transcription = parts
                            # Expected FLAC file for this utterance:
                            flac_file = os.path.join(
                                chapter_path, utterance_id + ".flac"
                            )
                            if not os.path.exists(flac_file):
                                print(
                                    f"Warning: FLAC file not found for {utterance_id} in {chapter_path}"
                                )
                                continue

                            # Define output paths (using the utterance ID as the base name)
                            wav_output = os.path.join(
                                AUDIO_OUT_DIR, utterance_id + ".wav"
                            )
                            transcript_output = os.path.join(
                                TRANSCRIPTS_OUT_DIR, utterance_id + ".txt"
                            )

                            # Convert FLAC to WAV
                            if not convert_flac_to_wav(flac_file, wav_output):
                                continue

                            # Write the transcript to the output file
                            with open(transcript_output, "w", encoding="utf-8") as outf:
                                outf.write(transcription + "\n")
                                print(
                                    f"Wrote transcript for {utterance_id} to {transcript_output}"
                                )


if __name__ == "__main__":
    process_transcripts()
