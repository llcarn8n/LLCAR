"""
Main Pipeline Module
Orchestrates the complete video-to-text processing pipeline.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from .audio_extraction import AudioExtractor
from .diarization import SpeakerDiarizer
from .transcription import Transcriber
from .postprocessing import TextPostProcessor, KeywordExtractor
from .output import OutputFormatter

logger = logging.getLogger(__name__)


class VideoPipeline:
    """
    Complete pipeline for video-to-text processing with speaker diarization.

    Pipeline steps:
    1. Extract audio from video
    2. Perform speaker diarization
    3. Transcribe audio to text
    4. Post-process text (clean, extract keywords)
    5. Generate structured output
    """

    def __init__(
        self,
        language: str = "en",
        model_variant: str = "default",
        hf_token: Optional[str] = None,
        device: str = "auto",
        output_dir: str = "./output"
    ):
        """
        Initialize VideoPipeline.

        Args:
            language: Language code ('en', 'ru', 'zh')
            model_variant: Model variant to use
            hf_token: HuggingFace token for pyannote
            device: Device to use ('cuda', 'cpu', or 'auto')
            output_dir: Directory for output files
        """
        self.language = language
        self.model_variant = model_variant
        self.device = device
        self.output_dir = output_dir

        # Initialize components
        logger.info("Initializing pipeline components...")

        self.audio_extractor = AudioExtractor()
        self.diarizer = SpeakerDiarizer(hf_token=hf_token, device=device)
        self.transcriber = Transcriber(
            language=language,
            model_variant=model_variant,
            device=device
        )
        self.text_processor = TextPostProcessor(language=language)
        self.keyword_extractor = KeywordExtractor(language=language)
        self.output_formatter = OutputFormatter(output_dir=output_dir)

        logger.info("Pipeline initialized successfully")

    def process_video(
        self,
        video_path: str,
        num_speakers: Optional[int] = None,
        extract_keywords: bool = True,
        keyword_method: str = "tfidf",
        top_keywords: int = 10,
        save_formats: List[str] = None
    ) -> Dict[str, Any]:
        """
        Process video file through the complete pipeline.

        Args:
            video_path: Path to input video file
            num_speakers: Expected number of speakers (optional)
            extract_keywords: Whether to extract keywords
            keyword_method: Keyword extraction method ('tfidf' or 'textrank')
            top_keywords: Number of top keywords to extract
            save_formats: List of output formats ('json', 'csv', 'txt')

        Returns:
            Processing results dictionary
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        start_time = datetime.now()
        logger.info(f"Starting pipeline for video: {video_path}")

        results = {
            "video_path": str(video_path),
            "language": self.language,
            "model_variant": self.model_variant,
            "start_time": start_time.isoformat(),
            "steps": {}
        }

        try:
            # Step 1: Extract audio
            logger.info("Step 1/5: Extracting audio from video...")
            audio_path = self.audio_extractor.extract_audio(str(video_path))
            duration = self.audio_extractor.get_audio_duration(audio_path)
            results["steps"]["audio_extraction"] = {
                "audio_path": audio_path,
                "duration": duration,
                "status": "completed"
            }
            logger.info(f"Audio extracted: {audio_path} (duration: {duration:.2f}s)")

            # Step 2: Speaker diarization
            logger.info("Step 2/5: Performing speaker diarization...")
            speaker_segments = self.diarizer.diarize(audio_path, num_speakers=num_speakers)
            speaker_stats = self.diarizer.get_speaker_statistics(speaker_segments)
            results["steps"]["diarization"] = {
                "num_segments": len(speaker_segments),
                "num_speakers": len(speaker_stats),
                "speaker_stats": speaker_stats,
                "status": "completed"
            }
            logger.info(f"Diarization completed: {len(speaker_segments)} segments, {len(speaker_stats)} speakers")

            # Step 3: Transcription
            logger.info("Step 3/5: Transcribing audio to text...")
            transcription_segments = self.transcriber.transcribe(
                audio_path,
                speaker_segments=speaker_segments
            )
            results["steps"]["transcription"] = {
                "num_segments": len(transcription_segments),
                "status": "completed"
            }
            logger.info(f"Transcription completed: {len(transcription_segments)} segments")

            # Step 4: Post-processing
            logger.info("Step 4/5: Post-processing text...")
            processed_segments = self.text_processor.process_segments(transcription_segments)

            keywords = []
            if extract_keywords:
                keywords = self.keyword_extractor.extract_keywords_from_segments(
                    processed_segments,
                    method=keyword_method,
                    top_n=top_keywords
                )
                logger.info(f"Extracted {len(keywords)} keywords")

            results["steps"]["postprocessing"] = {
                "num_keywords": len(keywords),
                "keyword_method": keyword_method,
                "status": "completed"
            }

            # Step 5: Generate output
            logger.info("Step 5/5: Generating output files...")

            # Create summary report
            report = self.output_formatter.create_summary_report(
                segments=processed_segments,
                keywords=keywords,
                speaker_stats=speaker_stats,
                metadata={
                    "video_path": str(video_path),
                    "language": self.language,
                    "processing_time": (datetime.now() - start_time).total_seconds()
                }
            )

            # Save in requested formats
            if save_formats is None:
                save_formats = ["json", "txt"]

            output_files = {}
            base_filename = video_path.stem

            if "json" in save_formats:
                json_path = self.output_formatter.save_json(
                    report,
                    filename=f"{base_filename}_report.json"
                )
                output_files["json"] = json_path

            if "csv" in save_formats:
                csv_path = self.output_formatter.save_csv(
                    processed_segments,
                    filename=f"{base_filename}_segments.csv"
                )
                output_files["csv"] = csv_path

            if "txt" in save_formats:
                txt_path = self.output_formatter.save_text(
                    processed_segments,
                    filename=f"{base_filename}_transcript.txt"
                )
                output_files["txt"] = txt_path

            results["steps"]["output"] = {
                "output_files": output_files,
                "status": "completed"
            }

            # Add final results
            results["segments"] = processed_segments
            results["keywords"] = keywords
            results["speaker_statistics"] = speaker_stats
            results["output_files"] = output_files
            results["end_time"] = datetime.now().isoformat()
            results["total_processing_time"] = (datetime.now() - start_time).total_seconds()
            results["status"] = "completed"

            logger.info(f"Pipeline completed successfully in {results['total_processing_time']:.2f}s")

            return results

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
            results["end_time"] = datetime.now().isoformat()
            raise

    def process_audio(
        self,
        audio_path: str,
        num_speakers: Optional[int] = None,
        extract_keywords: bool = True,
        keyword_method: str = "tfidf",
        top_keywords: int = 10,
        save_formats: List[str] = None
    ) -> Dict[str, Any]:
        """
        Process audio file directly (skip audio extraction step).

        Args:
            audio_path: Path to input audio file
            num_speakers: Expected number of speakers (optional)
            extract_keywords: Whether to extract keywords
            keyword_method: Keyword extraction method ('tfidf' or 'textrank')
            top_keywords: Number of top keywords to extract
            save_formats: List of output formats ('json', 'csv', 'txt')

        Returns:
            Processing results dictionary
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        start_time = datetime.now()
        logger.info(f"Starting pipeline for audio: {audio_path}")

        results = {
            "audio_path": str(audio_path),
            "language": self.language,
            "model_variant": self.model_variant,
            "start_time": start_time.isoformat(),
            "steps": {}
        }

        try:
            # Get audio duration
            duration = self.audio_extractor.get_audio_duration(str(audio_path))
            results["duration"] = duration

            # Step 1: Speaker diarization
            logger.info("Step 1/4: Performing speaker diarization...")
            speaker_segments = self.diarizer.diarize(str(audio_path), num_speakers=num_speakers)
            speaker_stats = self.diarizer.get_speaker_statistics(speaker_segments)
            results["steps"]["diarization"] = {
                "num_segments": len(speaker_segments),
                "num_speakers": len(speaker_stats),
                "speaker_stats": speaker_stats,
                "status": "completed"
            }

            # Step 2: Transcription
            logger.info("Step 2/4: Transcribing audio to text...")
            transcription_segments = self.transcriber.transcribe(
                str(audio_path),
                speaker_segments=speaker_segments
            )
            results["steps"]["transcription"] = {
                "num_segments": len(transcription_segments),
                "status": "completed"
            }

            # Step 3: Post-processing
            logger.info("Step 3/4: Post-processing text...")
            processed_segments = self.text_processor.process_segments(transcription_segments)

            keywords = []
            if extract_keywords:
                keywords = self.keyword_extractor.extract_keywords_from_segments(
                    processed_segments,
                    method=keyword_method,
                    top_n=top_keywords
                )

            results["steps"]["postprocessing"] = {
                "num_keywords": len(keywords),
                "keyword_method": keyword_method,
                "status": "completed"
            }

            # Step 4: Generate output
            logger.info("Step 4/4: Generating output files...")

            report = self.output_formatter.create_summary_report(
                segments=processed_segments,
                keywords=keywords,
                speaker_stats=speaker_stats,
                metadata={
                    "audio_path": str(audio_path),
                    "language": self.language,
                    "processing_time": (datetime.now() - start_time).total_seconds()
                }
            )

            if save_formats is None:
                save_formats = ["json", "txt"]

            output_files = {}
            base_filename = audio_path.stem

            if "json" in save_formats:
                json_path = self.output_formatter.save_json(
                    report,
                    filename=f"{base_filename}_report.json"
                )
                output_files["json"] = json_path

            if "csv" in save_formats:
                csv_path = self.output_formatter.save_csv(
                    processed_segments,
                    filename=f"{base_filename}_segments.csv"
                )
                output_files["csv"] = csv_path

            if "txt" in save_formats:
                txt_path = self.output_formatter.save_text(
                    processed_segments,
                    filename=f"{base_filename}_transcript.txt"
                )
                output_files["txt"] = txt_path

            results["steps"]["output"] = {
                "output_files": output_files,
                "status": "completed"
            }

            results["segments"] = processed_segments
            results["keywords"] = keywords
            results["speaker_statistics"] = speaker_stats
            results["output_files"] = output_files
            results["end_time"] = datetime.now().isoformat()
            results["total_processing_time"] = (datetime.now() - start_time).total_seconds()
            results["status"] = "completed"

            logger.info(f"Pipeline completed successfully in {results['total_processing_time']:.2f}s")

            return results

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
            results["end_time"] = datetime.now().isoformat()
            raise
