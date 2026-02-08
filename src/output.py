"""
Output Module
Formats and exports transcription results to JSON and CSV.
"""

import json
import csv
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class OutputFormatter:
    """Formats and exports transcription results."""

    def __init__(self, output_dir: str = "./output"):
        """
        Initialize OutputFormatter.

        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_json(
        self,
        data: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """
        Save data to JSON file.

        Args:
            data: Data to save
            filename: Output filename (optional)

        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transcription_{timestamp}.json"

        output_path = self.output_dir / filename

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"JSON output saved to {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error saving JSON: {e}")
            raise

    def save_csv(
        self,
        segments: List[Dict[str, Any]],
        filename: Optional[str] = None
    ) -> str:
        """
        Save transcription segments to CSV file.

        Args:
            segments: List of transcription segments
            filename: Output filename (optional)

        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transcription_{timestamp}.csv"

        output_path = self.output_dir / filename

        if not segments:
            logger.warning("No segments to save")
            return str(output_path)

        try:
            # Use a logical column order: time, speaker, then text fields
            preferred_order = ["start", "end", "speaker", "text", "original_text"]
            all_keys = set()
            for segment in segments:
                all_keys.update(segment.keys())
            fieldnames = [k for k in preferred_order if k in all_keys]
            fieldnames += sorted(all_keys - set(fieldnames))

            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(segments)

            logger.info(f"CSV output saved to {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error saving CSV: {e}")
            raise

    def save_text(
        self,
        segments: List[Dict[str, Any]],
        filename: Optional[str] = None,
        include_speakers: bool = True,
        include_timestamps: bool = True
    ) -> str:
        """
        Save transcription as formatted text file.

        Args:
            segments: List of transcription segments
            filename: Output filename (optional)
            include_speakers: Include speaker labels
            include_timestamps: Include timestamps

        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transcription_{timestamp}.txt"

        output_path = self.output_dir / filename

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for segment in segments:
                    parts = []

                    # Add timestamp
                    if include_timestamps and "start" in segment and "end" in segment:
                        start = self._format_timestamp(segment["start"])
                        end = self._format_timestamp(segment["end"])
                        parts.append(f"[{start} - {end}]")

                    # Add speaker
                    if include_speakers and "speaker" in segment and segment["speaker"]:
                        parts.append(f"{segment['speaker']}:")

                    # Add text
                    text = segment.get("text", "")
                    if parts:
                        f.write(" ".join(parts) + " " + text + "\n")
                    else:
                        f.write(text + "\n")

                    # Only add blank line if we have timestamps or speakers
                    if include_timestamps or include_speakers:
                        f.write("\n")

            logger.info(f"Text output saved to {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error saving text: {e}")
            raise

    def save_plain_text(
        self,
        segments: List[Dict[str, Any]],
        filename: Optional[str] = None
    ) -> str:
        """
        Save transcription as plain text file without timestamps or speakers.
        Each segment is written as continuous text with space separation.

        Args:
            segments: List of transcription segments
            filename: Output filename (optional)

        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transcription_{timestamp}_plain.txt"

        output_path = self.output_dir / filename

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                text_parts = []
                for segment in segments:
                    text = segment.get("text", "").strip()
                    if text:
                        text_parts.append(text)

                # Join all text parts with space
                full_text = " ".join(text_parts)
                f.write(full_text)

            logger.info(f"Plain text output saved to {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error saving plain text: {e}")
            raise

    def _format_timestamp(self, seconds: float) -> str:
        """
        Format timestamp in HH:MM:SS format.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def create_summary_report(
        self,
        segments: List[Dict[str, Any]],
        keywords: List[Dict[str, Any]],
        speaker_stats: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a comprehensive summary report.

        Args:
            segments: List of transcription segments
            keywords: List of extracted keywords
            speaker_stats: Speaker statistics (speaking time)
            metadata: Additional metadata

        Returns:
            Summary report dictionary
        """
        report = {
            "metadata": metadata or {},
            "statistics": {
                "total_segments": len(segments),
                "total_duration": 0.0,
                "total_words": 0,
                "speakers": []
            },
            "keywords": keywords,
            "segments": segments
        }

        # Calculate statistics
        if segments:
            # Total duration — use max end time across all segments
            ends = [s["end"] for s in segments if "end" in s]
            if ends:
                report["statistics"]["total_duration"] = max(ends)

            # Total words
            for segment in segments:
                text = segment.get("text", "")
                report["statistics"]["total_words"] += len(text.split())

            # Unique speakers
            speakers = set(s.get("speaker") for s in segments if s.get("speaker"))
            report["statistics"]["speakers"] = sorted(list(speakers))

        # Add speaker statistics if available
        if speaker_stats:
            report["speaker_statistics"] = speaker_stats

        return report
