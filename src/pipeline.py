"""
Main Pipeline Module
Orchestrates the complete video-to-text processing pipeline.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from .audio_extraction import AudioExtractor
from .diarization import SpeakerDiarizer
from .transcription import Transcriber
from .postprocessing import TextPostProcessor, KeywordExtractor, ComprehensivePostProcessor
from .output import OutputFormatter

logger = logging.getLogger(__name__)


class VideoPipeline:
    """
    Complete pipeline for video-to-text processing with speaker diarization.

    Pipeline steps:
    1. Extract audio from video (video input only)
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
        output_dir: str = "./output",
        enable_noise_reduction: bool = True,
        enable_automotive_analysis: bool = True
    ):
        """
        Initialize VideoPipeline.

        Args:
            language: Language code ('en', 'ru', 'zh')
            model_variant: Model variant to use
            hf_token: HuggingFace token for pyannote
            device: Device to use ('cuda', 'cpu', or 'auto')
            output_dir: Directory for output files
            enable_noise_reduction: Enable audio noise reduction filters
            enable_automotive_analysis: Enable automotive typology analysis
        """
        self.language = language
        self.model_variant = model_variant
        self.device = device
        self.output_dir = output_dir
        self.enable_automotive_analysis = enable_automotive_analysis

        # Initialize components
        logger.info("Initializing pipeline components...")

        self.audio_extractor = AudioExtractor(enable_noise_reduction=enable_noise_reduction)
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

    def _run_pipeline(
        self,
        audio_path: str,
        base_filename: str,
        results: Dict[str, Any],
        start_time: datetime,
        num_speakers: Optional[int] = None,
        extract_keywords: bool = True,
        keyword_method: str = "tfidf",
        top_keywords: int = 10,
        save_formats: Optional[List[str]] = None,
        total_steps: int = 4,
        step_offset: int = 0,
        source_path_key: str = "audio_path",
        source_path_value: str = "",
    ) -> Dict[str, Any]:
        """
        Core pipeline logic shared between video and audio processing.

        Args:
            audio_path: Path to audio file to process
            base_filename: Base name for output files
            results: Results dict to populate
            start_time: Processing start time
            num_speakers: Expected number of speakers (optional)
            extract_keywords: Whether to extract keywords
            keyword_method: Keyword extraction method
            top_keywords: Number of top keywords to extract
            save_formats: Output formats list
            total_steps: Total number of pipeline steps (for logging)
            step_offset: Current step number offset (for logging)
            source_path_key: Key for source path in metadata
            source_path_value: Value for source path in metadata
        """
        step = step_offset

        # Speaker diarization
        step += 1
        logger.info(f"Step {step}/{total_steps}: Performing speaker diarization...")
        speaker_segments = self.diarizer.diarize(audio_path, num_speakers=num_speakers)
        speaker_stats = self.diarizer.get_speaker_statistics(speaker_segments)
        results["steps"]["diarization"] = {
            "num_segments": len(speaker_segments),
            "num_speakers": len(speaker_stats),
            "speaker_stats": speaker_stats,
            "status": "completed"
        }
        logger.info(f"Diarization completed: {len(speaker_segments)} segments, {len(speaker_stats)} speakers")

        # Transcription
        step += 1
        logger.info(f"Step {step}/{total_steps}: Transcribing audio to text...")
        transcription_segments = self.transcriber.transcribe(
            audio_path,
            speaker_segments=speaker_segments
        )
        results["steps"]["transcription"] = {
            "num_segments": len(transcription_segments),
            "status": "completed"
        }
        logger.info(f"Transcription completed: {len(transcription_segments)} segments")

        # Post-processing
        step += 1
        logger.info(f"Step {step}/{total_steps}: Post-processing text...")
        processed_segments = self.text_processor.process_segments(transcription_segments)

        keywords = []
        automotive_typology = None

        if extract_keywords:
            keywords = self.keyword_extractor.extract_keywords_from_segments(
                processed_segments,
                method=keyword_method,
                top_n=top_keywords
            )
            logger.info(f"Extracted {len(keywords)} keywords")

        # Perform automotive typology analysis if enabled
        if self.enable_automotive_analysis:
            from .automotive_typology import AutomotiveTypologyAnalyzer
            automotive_analyzer = AutomotiveTypologyAnalyzer(language=self.language)
            automotive_typology = automotive_analyzer.analyze_segments(processed_segments)
            logger.info(
                f"Automotive analysis: {automotive_typology['summary']['total_automotive_segments']}/"
                f"{automotive_typology['summary']['total_segments']} segments contain automotive content"
            )

        results["steps"]["postprocessing"] = {
            "num_keywords": len(keywords),
            "keyword_method": keyword_method,
            "automotive_analysis_enabled": self.enable_automotive_analysis,
            "status": "completed"
        }

        # Generate output
        step += 1
        logger.info(f"Step {step}/{total_steps}: Generating output files...")

        report = self.output_formatter.create_summary_report(
            segments=processed_segments,
            keywords=keywords,
            speaker_stats=speaker_stats,
            automotive_typology=automotive_typology,
            metadata={
                source_path_key: source_path_value,
                "language": self.language,
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
        )

        if save_formats is None:
            save_formats = ["json", "txt"]

        output_files = {}

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

        if "plain" in save_formats or "plain_text" in save_formats:
            plain_txt_path = self.output_formatter.save_plain_text(
                processed_segments,
                filename=f"{base_filename}_plain.txt"
            )
            output_files["plain_text"] = plain_txt_path

        results["steps"]["output"] = {
            "output_files": output_files,
            "status": "completed"
        }

        # Final results
        results["segments"] = processed_segments
        results["keywords"] = keywords
        results["speaker_statistics"] = speaker_stats
        results["automotive_typology"] = automotive_typology
        results["output_files"] = output_files
        results["end_time"] = datetime.now().isoformat()
        results["total_processing_time"] = (datetime.now() - start_time).total_seconds()
        results["status"] = "completed"

        logger.info(f"Pipeline completed successfully in {results['total_processing_time']:.2f}s")

        return results

    def process_video(
        self,
        video_path: str,
        num_speakers: Optional[int] = None,
        extract_keywords: bool = True,
        keyword_method: str = "tfidf",
        top_keywords: int = 10,
        save_formats: Optional[List[str]] = None
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

        extracted_audio_path = None
        try:
            # Step 1: Extract audio
            logger.info("Step 1/5: Extracting audio from video...")
            extracted_audio_path = self.audio_extractor.extract_audio(str(video_path))
            duration = self.audio_extractor.get_audio_duration(extracted_audio_path)
            results["steps"]["audio_extraction"] = {
                "audio_path": extracted_audio_path,
                "duration": duration,
                "status": "completed"
            }
            logger.info(f"Audio extracted: {extracted_audio_path} (duration: {duration:.2f}s)")

            # Steps 2-5: Shared pipeline
            return self._run_pipeline(
                audio_path=extracted_audio_path,
                base_filename=video_path.stem,
                results=results,
                start_time=start_time,
                num_speakers=num_speakers,
                extract_keywords=extract_keywords,
                keyword_method=keyword_method,
                top_keywords=top_keywords,
                save_formats=save_formats,
                total_steps=5,
                step_offset=1,
                source_path_key="video_path",
                source_path_value=str(video_path),
            )

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
            results["end_time"] = datetime.now().isoformat()
            raise

        finally:
            # Clean up extracted temporary audio file
            if extracted_audio_path:
                try:
                    os.remove(extracted_audio_path)
                    logger.debug(f"Cleaned up temporary audio file: {extracted_audio_path}")
                except OSError:
                    pass

    def process_audio(
        self,
        audio_path: str,
        num_speakers: Optional[int] = None,
        extract_keywords: bool = True,
        keyword_method: str = "tfidf",
        top_keywords: int = 10,
        save_formats: Optional[List[str]] = None
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

            # Steps 1-4: Shared pipeline
            return self._run_pipeline(
                audio_path=str(audio_path),
                base_filename=audio_path.stem,
                results=results,
                start_time=start_time,
                num_speakers=num_speakers,
                extract_keywords=extract_keywords,
                keyword_method=keyword_method,
                top_keywords=top_keywords,
                save_formats=save_formats,
                total_steps=4,
                step_offset=0,
                source_path_key="audio_path",
                source_path_value=str(audio_path),
            )

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
            results["end_time"] = datetime.now().isoformat()
            raise
