"""
Audio Extraction Module
Extracts audio from video files using ffmpeg.
"""

import os
import logging
import tempfile
from pathlib import Path
import ffmpeg

logger = logging.getLogger(__name__)


class AudioExtractor:
    """Extracts audio from video files."""

    def __init__(self, sample_rate: int = 16000, channels: int = 1, enable_noise_reduction: bool = True):
        """
        Initialize AudioExtractor.

        Args:
            sample_rate: Target sample rate for audio (default: 16000 Hz for ASR)
            channels: Number of audio channels (default: 1 for mono)
            enable_noise_reduction: Apply noise reduction filters (default: True)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.enable_noise_reduction = enable_noise_reduction

    def extract_audio(self, video_path: str, output_path: str = None) -> str:
        """
        Extract audio from video file.

        Args:
            video_path: Path to input video file
            output_path: Path for output audio file (optional)

        Returns:
            Path to extracted audio file
        """
        video_path = Path(video_path)

        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Generate output path if not provided — use temp directory to avoid
        # writing next to the source file (which may be on a read-only filesystem)
        if output_path is None:
            tmp_dir = Path(tempfile.gettempdir()) / "llcar"
            tmp_dir.mkdir(parents=True, exist_ok=True)
            output_path = tmp_dir / (video_path.stem + '.wav')
        else:
            output_path = Path(output_path)

        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Extracting audio from {video_path} to {output_path}")

        try:
            # Extract audio using ffmpeg
            stream = ffmpeg.input(str(video_path))

            # Apply audio filters for noise reduction and speech enhancement
            if self.enable_noise_reduction:
                # Audio filter chain for speech enhancement:
                # 1. highpass=200 - Remove low-frequency rumble and noise below 200Hz
                # 2. lowpass=3000 - Remove high-frequency noise above 3kHz (speech is typically 80-3000Hz)
                # 3. afftdn - Apply FFT-based noise reduction (denoiser)
                audio_filters = [
                    'highpass=f=200',       # Remove low-frequency noise
                    'lowpass=f=3000',       # Remove high-frequency noise
                    'afftdn=nf=-25',        # Denoise (noise floor reduction)
                ]
                filter_complex = ','.join(audio_filters)

                stream = ffmpeg.output(
                    stream,
                    str(output_path),
                    acodec='pcm_s16le',
                    ac=self.channels,
                    ar=self.sample_rate,
                    audio_filters=filter_complex,
                    loglevel='error'
                )
            else:
                stream = ffmpeg.output(
                    stream,
                    str(output_path),
                    acodec='pcm_s16le',
                    ac=self.channels,
                    ar=self.sample_rate,
                    loglevel='error'
                )

            ffmpeg.run(stream, overwrite_output=True)

            logger.info(f"Audio extracted successfully to {output_path}")
            return str(output_path)

        except ffmpeg.Error as e:
            logger.error(f"Error extracting audio: {e.stderr.decode() if e.stderr else str(e)}")
            raise

    def get_audio_duration(self, audio_path: str) -> float:
        """
        Get duration of audio file in seconds.

        Args:
            audio_path: Path to audio file

        Returns:
            Duration in seconds
        """
        try:
            probe = ffmpeg.probe(audio_path)
            duration = float(probe['format']['duration'])
            return duration
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            raise
