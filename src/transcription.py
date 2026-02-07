"""
Transcription Module
Converts speech to text using various ASR models based on language.
Supports:
- English: WhisperX
- Russian: bond005/whisper-podlodka-turbo, antony66/whisper-large-v3-russian
- Chinese: Whisper (with optional FireRedASR support)
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Literal
import torch
from transformers import pipeline
import whisper

logger = logging.getLogger(__name__)

# Language-specific model mappings
LANGUAGE_MODELS = {
    "en": {
        "default": "openai/whisper-large-v3",
        "whisperx": "whisperx"
    },
    "ru": {
        "default": "bond005/whisper-podlodka-turbo",
        "alternative": "antony66/whisper-large-v3-russian",
        "turbo": "dvislobokov/whisper-large-v3-turbo-russian"
    },
    "zh": {
        "default": "openai/whisper-large-v3",
        # FireRedASR can be added here if needed
    }
}


class Transcriber:
    """Transcribes audio to text with support for multiple languages."""

    def __init__(
        self,
        language: Literal["en", "ru", "zh"] = "en",
        model_variant: str = "default",
        device: str = "auto"
    ):
        """
        Initialize Transcriber.

        Args:
            language: Language code ('en', 'ru', 'zh')
            model_variant: Model variant to use ('default', 'alternative', 'turbo')
            device: Device to use ('cuda', 'cpu', or 'auto')
        """
        self.language = language
        self.model_variant = model_variant

        # Determine device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        logger.info(f"Using device: {self.device}")

        # Load model
        self.model = None
        self.model_name = None
        self._load_model()

    def _load_model(self):
        """Load the appropriate transcription model."""
        if self.language not in LANGUAGE_MODELS:
            raise ValueError(f"Unsupported language: {self.language}")

        model_config = LANGUAGE_MODELS[self.language]

        if self.model_variant not in model_config:
            logger.warning(
                f"Model variant '{self.model_variant}' not found for language '{self.language}'. "
                f"Using 'default'."
            )
            self.model_variant = "default"

        self.model_name = model_config[self.model_variant]

        logger.info(f"Loading transcription model: {self.model_name}")

        try:
            if self.model_name == "whisperx":
                # WhisperX requires special handling
                logger.warning(
                    "WhisperX requires separate installation. "
                    "Using standard Whisper model instead."
                )
                self.model = whisper.load_model("large-v3", device=self.device)
            elif self.model_name.startswith("openai/whisper"):
                # Use standard Whisper — extract size like "large-v3" from "openai/whisper-large-v3"
                model_size = self.model_name.split("openai/whisper-", 1)[-1]
                self.model = whisper.load_model(model_size, device=self.device)
            else:
                # Use HuggingFace transformers
                self.model = pipeline(
                    "automatic-speech-recognition",
                    model=self.model_name,
                    device=0 if self.device == "cuda" else -1
                )

            logger.info("Transcription model loaded successfully")

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def transcribe(
        self,
        audio_path: str,
        speaker_segments: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Transcribe audio to text.

        Args:
            audio_path: Path to audio file
            speaker_segments: Optional speaker diarization segments

        Returns:
            List of transcription segments with format:
            [{"speaker": "SPEAKER_00", "start": 0.5, "end": 3.2, "text": "..."}, ...]
        """
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Transcribing audio from {audio_path}")

        try:
            if isinstance(self.model, whisper.Whisper):
                # Use Whisper model
                result = self.model.transcribe(
                    str(audio_path),
                    language=self.language,
                    task="transcribe"
                )
                segments = self._process_whisper_result(result, speaker_segments)
            else:
                # Use HuggingFace pipeline
                result = self.model(str(audio_path), return_timestamps=True)
                segments = self._process_hf_result(result, speaker_segments)

            logger.info(f"Transcription completed: {len(segments)} segments")
            return segments

        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise

    def _process_whisper_result(
        self,
        result: Dict[str, Any],
        speaker_segments: Optional[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Process Whisper transcription result."""
        segments = []

        for segment in result["segments"]:
            segment_data = {
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip(),
                "speaker": None
            }

            # Match with speaker if diarization data is available
            if speaker_segments:
                segment_data["speaker"] = self._match_speaker(
                    segment["start"],
                    segment["end"],
                    speaker_segments
                )

            segments.append(segment_data)

        return segments

    def _process_hf_result(
        self,
        result: Dict[str, Any],
        speaker_segments: Optional[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Process HuggingFace pipeline result."""
        segments = []

        if "chunks" in result:
            for chunk in result["chunks"]:
                ts = chunk.get("timestamp")
                segment_data = {
                    "start": ts[0] if ts and ts[0] is not None else 0.0,
                    "end": ts[1] if ts and ts[1] is not None else 0.0,
                    "text": chunk["text"].strip(),
                    "speaker": None
                }

                # Match with speaker if diarization data is available
                if speaker_segments:
                    segment_data["speaker"] = self._match_speaker(
                        segment_data["start"],
                        segment_data["end"],
                        speaker_segments
                    )

                segments.append(segment_data)
        else:
            # Single segment result
            segments.append({
                "start": 0.0,
                "end": 0.0,
                "text": result["text"].strip(),
                "speaker": None
            })

        return segments

    def _match_speaker(
        self,
        start: float,
        end: float,
        speaker_segments: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Match transcription segment with speaker.

        Args:
            start: Start time of transcription segment
            end: End time of transcription segment
            speaker_segments: List of speaker diarization segments

        Returns:
            Speaker label or None
        """
        # Find speaker with maximum overlap
        max_overlap = 0.0
        matched_speaker = None

        for speaker_seg in speaker_segments:
            # Calculate overlap
            overlap_start = max(start, speaker_seg["start"])
            overlap_end = min(end, speaker_seg["end"])
            overlap = max(0.0, overlap_end - overlap_start)

            if overlap > max_overlap:
                max_overlap = overlap
                matched_speaker = speaker_seg["speaker"]

        return matched_speaker
