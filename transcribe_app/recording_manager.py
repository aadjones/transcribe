# recording_manager.py
import logging
import os
import wave
import time
import numpy as np

from PySide6.QtCore import QIODevice, QTemporaryFile
from PySide6.QtMultimedia import (
    QAudioFormat, 
    QAudioSource, 
    QMediaDevices,
    QAudio
)

# Configure logging to capture all messages with timestamps
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create a logger specific to the recording manager
logger = logging.getLogger('RecordingManager')
logger.setLevel(logging.DEBUG)

# Ensure all handlers also have DEBUG level
for handler in logger.handlers:
    handler.setLevel(logging.DEBUG)


class RecordingManager:
    """
    A robust recording manager that uses QAudioSource and QTemporaryFile.
    It records audio until stop_recording() is called.
    """

    def __init__(self, parent=None):
        self.parent = parent
        # Create a temporary file with .wav extension
        self.temp_file = QTemporaryFile(os.path.join(os.getcwd(), "XXXXXX.wav"), parent)
        self.temp_file.setAutoRemove(False)
        if not self.temp_file.open(QIODevice.ReadWrite):
            logger.error("Cannot open temporary file for recording")
            raise RuntimeError("Cannot open temporary file for recording")

        logger.info(f"Created temporary file: {self.temp_file.fileName()}")
        
        # Store the audio format
        self.audio_format = None
        self.audio_source = None
        self.recording_start_time = None
        
        # Initialize with default format
        fmt = QAudioFormat()
        fmt.setSampleRate(44100)
        fmt.setChannelCount(1)
        fmt.setSampleFormat(QAudioFormat.Int16)  # Explicitly set 16-bit PCM format
        
        devices = QMediaDevices()
        default_input = devices.defaultAudioInput()
        
        # Log available audio devices and their properties
        all_inputs = QMediaDevices.audioInputs()
        if all_inputs:
            logger.info(f"Available audio input devices:")
            for device in all_inputs:
                logger.info(
                    f"  - Device: {device.description()}\n"
                    f"    ID: {device.id()}\n"
                    f"    Format supported: {device.isFormatSupported(fmt)}\n"
                    f"    Preferred format: Sample Rate={device.preferredFormat().sampleRate()}, "
                    f"Channels={device.preferredFormat().channelCount()}, "
                    f"Format={device.preferredFormat().sampleFormat()}"
                )
        else:
            logger.error("No audio input devices found!")
            raise RuntimeError("No audio input devices available")
        
        if default_input is None:
            logger.error("No default audio input device found")
            raise RuntimeError("No default audio input device found")
            
        logger.info(
            f"Using default input device:\n"
            f"  Description: {default_input.description()}\n"
            f"  ID: {default_input.id()}\n"
            f"  Format supported: {default_input.isFormatSupported(fmt)}\n"
            f"  Preferred format: Sample Rate={default_input.preferredFormat().sampleRate()}, "
            f"Channels={default_input.preferredFormat().channelCount()}, "
            f"Format={default_input.preferredFormat().sampleFormat()}"
        )
        
        if not default_input.isFormatSupported(fmt):
            preferred_fmt = default_input.preferredFormat()
            # Ensure we still use Int16 even with preferred format
            preferred_fmt.setSampleFormat(QAudioFormat.Int16)
            logger.warning(
                f"Default format not supported. Using preferred format with Int16:\n"
                f"  Sample Rate: {preferred_fmt.sampleRate()} Hz\n"
                f"  Channels: {preferred_fmt.channelCount()}\n"
                f"  Sample Format: {preferred_fmt.sampleFormat()}\n"
                f"  Original format was: Sample Rate={fmt.sampleRate()}, "
                f"Channels={fmt.channelCount()}, Format={fmt.sampleFormat()}"
            )
            fmt = preferred_fmt
        else:
            logger.info(
                f"Using requested format:\n"
                f"  Sample Rate: {fmt.sampleRate()} Hz\n"
                f"  Channels: {fmt.channelCount()}\n"
                f"  Sample Format: {fmt.sampleFormat()}"
            )
        
        self.audio_format = fmt
        
        # Initialize WAV file header with actual format
        try:
            with wave.open(self.temp_file.fileName(), "wb") as wav_file:
                wav_file.setnchannels(self.audio_format.channelCount())
                wav_file.setsampwidth(2)  # 2 bytes for Int16
                wav_file.setframerate(self.audio_format.sampleRate())
                logger.info(
                    f"Initialized WAV header:\n"
                    f"  Channels: {wav_file.getnchannels()}\n"
                    f"  Sample Width: {wav_file.getsampwidth() * 8} bits\n"
                    f"  Sample Rate: {wav_file.getframerate()} Hz"
                )
                
            # Verify the header was written correctly
            with wave.open(self.temp_file.fileName(), "rb") as wav_verify:
                logger.debug(
                    f"WAV header verification:\n"
                    f"  File size: {os.path.getsize(self.temp_file.fileName())} bytes\n"
                    f"  Channels match: {wav_verify.getnchannels() == self.audio_format.channelCount()}\n"
                    f"  Sample rate match: {wav_verify.getframerate() == self.audio_format.sampleRate()}\n"
                    f"  Sample width correct: {wav_verify.getsampwidth() == 2}"
                )
        except Exception as e:
            logger.error(f"Failed to initialize WAV header: {e}")
            raise RuntimeError(f"Failed to initialize WAV header: {e}")

    def start_recording(self):
        if self.audio_source is not None:
            logger.warning("Recording already in progress")
            return

        devices = QMediaDevices()
        default_input = devices.defaultAudioInput()
        
        if default_input is None:
            logger.error("No default audio input device found when starting recording")
            return
            
        self.audio_source = QAudioSource(default_input, self.audio_format, self.parent)
        
        # Set a reasonable buffer size (e.g., 100ms worth of audio)
        buffer_size = int(self.audio_format.sampleRate() * 
                         self.audio_format.channelCount() * 
                         2 * 0.1)  # 2 bytes per sample, 0.1 seconds
        self.audio_source.setBufferSize(buffer_size)
        
        # Log the audio source state and properties
        logger.info(
            f"Audio source created:\n"
            f"  Buffer Size: {self.audio_source.bufferSize()} bytes\n"
            f"  State: {self.audio_source.state()}\n"
            f"  Error: {self.audio_source.error()}\n"
            f"  Volume: {self.audio_source.volume()}"
        )
        
        self.temp_file.seek(44)  # Skip WAV header
        self.audio_source.start(self.temp_file)
        self.recording_start_time = time.time()
        
        # Verify recording started properly
        if self.audio_source.state() != QAudio.ActiveState:
            logger.error(
                f"Recording failed to start properly:\n"
                f"  State: {self.audio_source.state()}\n"
                f"  Error: {self.audio_source.error()}"
            )
        else:
            logger.info("Recording started successfully")

    def stop_recording(self):
        if self.audio_source is None:
            logger.warning("No recording in progress")
            return None

        temp_filename = None
        try:
            # Stop recording and wait for buffers to flush
            logger.debug("Stopping audio source...")
            self.audio_source.stop()
            time.sleep(0.5)  # Wait for buffers to flush
            
            recording_duration = time.time() - self.recording_start_time
            logger.info(
                f"Recording stopped:\n"
                f"  Duration: {recording_duration:.2f} seconds\n"
                f"  Final State: {self.audio_source.state()}\n"
                f"  Final Error: {self.audio_source.error()}\n"
                f"  Buffer Size: {self.audio_source.bufferSize()} bytes\n"
                f"  Volume: {self.audio_source.volume()}"
            )
            
            # Store filename before closing
            temp_filename = self.temp_file.fileName()
            
            # Calculate file stats before closing
            file_size = self.temp_file.size()
            data_size = file_size - 44  # Subtract WAV header size
            expected_samples = data_size // (self.audio_format.channelCount() * 2)  # Account for channels
            
            logger.debug(
                f"Initial file statistics:\n"
                f"  Total file size: {file_size} bytes\n"
                f"  Estimated data size: {data_size} bytes\n"
                f"  Expected samples: {expected_samples}\n"
                f"  Sample rate: {self.audio_format.sampleRate()} Hz\n"
                f"  Channels: {self.audio_format.channelCount()}\n"
                f"  Bytes per sample: {self.audio_format.channelCount() * 2}\n"
                f"  Expected duration: {expected_samples / self.audio_format.sampleRate():.2f} seconds"
            )

            # Read and analyze the raw audio data before closing
            self.temp_file.seek(44)  # Skip header
            audio_bytes = self.temp_file.readAll()
            raw_data = audio_bytes.data()
            raw_len = len(raw_data)
            logger.debug(
                f"Raw audio read from temp file:\n"
                f"  Bytes read: {raw_len}\n"
                f"  Expected bytes: {data_size}\n"
                f"  Matches expected: {raw_len == data_size}"
            )
            
            if raw_len == 0:
                logger.error("No audio data captured from microphone!")
                return None
            
            # Analyze the raw audio data
            try:
                sample_array = np.frombuffer(raw_data[:1000], dtype=np.int16)
                mean_abs = np.mean(np.abs(sample_array)) if len(sample_array) else 0
                max_abs = np.max(np.abs(sample_array)) if len(sample_array) else 0
                zero_count = np.sum(sample_array == 0) if len(sample_array) else 0
                
                logger.debug(
                    f"Raw audio analysis:\n"
                    f"  Data size: {raw_len} bytes\n"
                    f"  First 10 samples: {sample_array[:10]}\n"
                    f"  Mean absolute value: {mean_abs:.2f}\n"
                    f"  Max absolute value: {max_abs}\n"
                    f"  Zero samples in first 1000: {zero_count}\n"
                    f"  Appears to be silence: {mean_abs < 10}\n"
                    f"  Sample count matches: {len(sample_array) * 2 == raw_len}"
                )
                
                if mean_abs < 1:
                    logger.warning("Audio appears to be completely silent!")
            except Exception as e:
                logger.warning(f"Could not analyze raw audio data: {e}")

            # Close current file handle
            self.temp_file.close()
            
            # Small delay to ensure Windows releases the file handle
            time.sleep(0.5)
            
            try:
                logger.debug(f"Opening WAV file for verification: {temp_filename}")
                
                # First, rewrite the WAV file with proper headers and data
                logger.debug(f"Rewriting WAV file with {raw_len} bytes of PCM data")
                with wave.open(temp_filename, "wb") as wav_write:
                    wav_write.setnchannels(self.audio_format.channelCount())
                    wav_write.setsampwidth(2)  # 2 bytes for Int16
                    wav_write.setframerate(self.audio_format.sampleRate())
                    wav_write.writeframes(raw_data)
                logger.debug("Finished rewriting WAV header + data")
                
                # Now verify the rewritten file
                with wave.open(temp_filename, "rb") as wav_read:
                    frames = wav_read.getnframes()
                    channels = wav_read.getnchannels()
                    rate = wav_read.getframerate()
                    width = wav_read.getsampwidth()
                    
                    expected_frames = raw_len // (channels * width)
                    
                    logger.info(
                        f"WAV file properties after rewrite:\n"
                        f"  Frames: {frames}\n"
                        f"  Expected frames: {expected_frames}\n"
                        f"  Frames match: {frames == expected_frames}\n"
                        f"  Channels: {channels}\n"
                        f"  Sample Rate: {rate} Hz\n"
                        f"  Sample Width: {width * 8} bits\n"
                        f"  Expected Duration: {frames / rate:.2f} seconds\n"
                        f"  File size: {os.path.getsize(temp_filename)} bytes"
                    )
                    
                    if frames == 0:
                        logger.error(
                            f"WAV file reports 0 frames after rewrite:\n"
                            f"  Raw data length: {raw_len} bytes\n"
                            f"  File size: {os.path.getsize(temp_filename)} bytes\n"
                            f"  Expected frames: {expected_frames}\n"
                            f"  Channels: {channels}\n"
                            f"  Sample width: {width} bytes"
                        )
                        raise RuntimeError("WAV file reports 0 frames after rewrite")
                    
                    # Read all audio frames
                    logger.debug(f"Attempting to read {frames} frames...")
                    audio_data = wav_read.readframes(frames)
                    actual_bytes = len(audio_data)
                    expected_bytes = frames * channels * width
                    
                    logger.debug(
                        f"Frame read results:\n"
                        f"  Expected bytes: {expected_bytes}\n"
                        f"  Actual bytes read: {actual_bytes}\n"
                        f"  Matches expected: {actual_bytes == expected_bytes}\n"
                        f"  Matches raw data: {actual_bytes == raw_len}"
                    )
                    
                    if not audio_data:
                        logger.error(
                            f"No audio data read from WAV file:\n"
                            f"  Frames reported: {frames}\n"
                            f"  File size: {os.path.getsize(temp_filename)} bytes\n"
                            f"  Header size: 44 bytes\n"
                            f"  Expected data size: {frames * channels * width} bytes\n"
                            f"  Raw data size: {raw_len} bytes"
                        )
                        raise RuntimeError("No audio data read from WAV file")
                    
                    # Analyze the WAV audio data
                    try:
                        sample_array = np.frombuffer(audio_data[:2000], dtype=np.int16)
                        mean_abs = np.mean(np.abs(sample_array)) if len(sample_array) else 0
                        max_abs = np.max(np.abs(sample_array)) if len(sample_array) else 0
                        zero_count = np.sum(sample_array == 0) if len(sample_array) else 0
                        
                        logger.info(
                            f"WAV audio analysis:\n"
                            f"  Data size: {len(audio_data)} bytes\n"
                            f"  Samples analyzed: {len(sample_array)}\n"
                            f"  First 10 samples: {sample_array[:10]}\n"
                            f"  Mean absolute value: {mean_abs:.2f}\n"
                            f"  Max absolute value: {max_abs}\n"
                            f"  Zero samples in first 2000: {zero_count}\n"
                            f"  Appears to be silence: {mean_abs < 10}\n"
                            f"  Matches raw data: {np.array_equal(sample_array, np.frombuffer(raw_data[:2000], dtype=np.int16))}"
                        )
                        
                        if mean_abs < 1:
                            logger.warning("Final audio appears to be completely silent!")
                    except Exception as e:
                        logger.warning(f"Could not analyze WAV audio data: {e}")
                
                # Final verification
                if os.path.exists(temp_filename):
                    file_size = os.path.getsize(temp_filename)
                    with wave.open(temp_filename, "rb") as verify_wav:
                        final_frames = verify_wav.getnframes()
                        final_duration = final_frames / verify_wav.getframerate()
                        logger.info(
                            f"Final WAV file verification:\n"
                            f"  File exists: True\n"
                            f"  File size: {file_size} bytes\n"
                            f"  Frames: {final_frames}\n"
                            f"  Duration: {final_duration:.2f} seconds\n"
                            f"  Matches expected: {abs(final_duration - recording_duration) < 0.1}\n"
                            f"  Data size matches: {file_size - 44 == len(audio_data)}\n"
                            f"  Frames match: {final_frames == frames}"
                        )
                    return temp_filename
                else:
                    logger.error("File does not exist after saving!")
                    return None
                
            except Exception as e:
                logger.error(f"Error finalizing WAV file: {e}")
                return None
        finally:
            # Ensure proper cleanup of resources
            if self.audio_source is not None:
                logger.debug("Cleaning up audio source...")
                self.audio_source.stop()
                self.audio_source = None
            
            if self.temp_file is not None and self.temp_file.isOpen():
                logger.debug("Closing temporary file...")
                self.temp_file.close()
            
            self.recording_start_time = None
            
        return temp_filename

    def delete_recording(self, filename=None, max_attempts=5, delay=0.5):
        """
        Securely delete a recording file with retry logic for Windows file locks.
        
        Args:
            filename (str, optional): The file to delete. If None, uses the temp file name.
            max_attempts (int): Maximum number of deletion attempts.
            delay (float): Delay in seconds between attempts.
            
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        if filename is None and self.temp_file is not None:
            filename = self.temp_file.fileName()
        
        if not filename or not os.path.exists(filename):
            logger.debug(f"No file to delete or file doesn't exist: {filename}")
            return True
            
        logger.debug(f"Attempting to delete file: {filename}")
        
        # Ensure the file is closed if it's our temp file
        if self.temp_file is not None and self.temp_file.isOpen():
            logger.debug("Closing temporary file before deletion...")
            self.temp_file.close()
            time.sleep(0.1)  # Small delay after closing
            
        # Try to delete with multiple attempts
        for attempt in range(max_attempts):
            try:
                logger.debug(f"Delete attempt {attempt + 1}/{max_attempts}")
                
                # First try to open and close the file to check if it's locked
                try:
                    with open(filename, 'rb') as test_file:
                        pass
                    logger.debug("File is not locked")
                except PermissionError:
                    logger.warning(f"File is locked on attempt {attempt + 1}")
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                    continue
                    
                # Try to delete the file
                os.remove(filename)
                logger.info(f"Successfully deleted file on attempt {attempt + 1}")
                return True
                
            except PermissionError as e:
                logger.warning(
                    f"Permission error on delete attempt {attempt + 1}: {e}\n"
                    f"File locked: {filename}"
                )
                if attempt < max_attempts - 1:
                    time.sleep(delay)
            except FileNotFoundError:
                logger.info("File already deleted")
                return True
            except Exception as e:
                logger.error(f"Unexpected error trying to delete file: {e}")
                return False
                
        logger.error(
            f"Failed to delete file after {max_attempts} attempts: {filename}\n"
            "File may be locked by another process"
        )
        return False
