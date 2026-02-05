"""
Speaker Diarization Module
Identifies and separates speakers in audio using pyannote.audio.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import torch
from pyannote.audio import Pipeline

logger = logging.getLogger(__name__)


class SpeakerDiarizer:
    """Performs speaker diarization using pyannote.audio."""

    def __init__(self, hf_token: Optional[str] = None, device: str = "auto"):
        """
        Initialize SpeakerDiarizer.

        Args:
            hf_token: HuggingFace token for accessing pyannote models
            device: Device to use ('cuda', 'cpu', or 'auto')
        """
        self.hf_token = hf_token or os.getenv("HF_TOKEN")

        if not self.hf_token:
            raise ValueError(
                "HuggingFace token is required. Set HF_TOKEN environment variable "
                "or pass it as an argument."
            )

        # Determine device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        logger.info(f"Using device: {self.device}")

        # Load diarization pipeline
        self.pipeline = None
        self._load_pipeline()

    def _load_pipeline(self):
        """Load the pyannote.audio diarization pipeline."""
        try:
            logger.info("Loading pyannote speaker diarization model...")
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=self.hf_token
            )
            self.pipeline.to(torch.device(self.device))
            logger.info("Diarization model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading diarization pipeline: {e}")
            raise

    def diarize(self, audio_path: str, num_speakers: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Perform speaker diarization on audio file.

        Args:
            audio_path: Path to audio file
            num_speakers: Expected number of speakers (optional)

        Returns:
            List of speaker segments with format:
            [{"speaker": "SPEAKER_00", "start": 0.5, "end": 3.2}, ...]
        """
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Performing speaker diarization on {audio_path}")

        try:
            # Run diarization
            if num_speakers:
                diarization = self.pipeline(
                    str(audio_path),
                    num_speakers=num_speakers
                )
            else:
                diarization = self.pipeline(str(audio_path))

            # Convert to list of segments
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    "speaker": speaker,
                    "start": turn.start,
                    "end": turn.end
                })

            logger.info(f"Diarization completed: {len(segments)} segments found")
            logger.info(f"Unique speakers: {len(set(s['speaker'] for s in segments))}")

            return segments

        except Exception as e:
            logger.error(f"Error during diarization: {e}")
            raise

    def get_speaker_statistics(self, segments: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate speaking time statistics for each speaker.

        Args:
            segments: List of speaker segments

        Returns:
            Dictionary with speaker labels as keys and total speaking time as values
        """
        stats = {}
        for segment in segments:
            speaker = segment["speaker"]
            duration = segment["end"] - segment["start"]

            if speaker not in stats:
                stats[speaker] = 0.0
            stats[speaker] += duration

        return stats
