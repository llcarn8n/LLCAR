#!/usr/bin/env python3
"""
Example usage of LLCAR Video Processing Pipeline
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import VideoPipeline


def example_video_processing():
    """Example: Process a video file."""
    # Set HuggingFace token (required)
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        print("Error: HF_TOKEN environment variable not set")
        print("Get your token from: https://huggingface.co/settings/tokens")
        return

    # Initialize pipeline for English
    pipeline = VideoPipeline(
        language="en",
        model_variant="default",
        hf_token=hf_token,
        device="auto",
        output_dir="./output"
    )

    # Process video
    video_path = "path/to/your/video.mp4"
    if not Path(video_path).exists():
        print(f"Error: Video file not found: {video_path}")
        print("Please update the video_path variable with your video file")
        return

    results = pipeline.process_video(
        video_path=video_path,
        num_speakers=None,  # Auto-detect
        extract_keywords=True,
        keyword_method="tfidf",
        top_keywords=10,
        save_formats=["json", "txt", "csv"]
    )

    print("\nProcessing completed!")
    print(f"Results saved to: {results['output_files']}")


def example_audio_processing():
    """Example: Process an audio file directly."""
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        print("Error: HF_TOKEN environment variable not set")
        return

    # Initialize pipeline for Russian
    pipeline = VideoPipeline(
        language="ru",
        model_variant="default",  # bond005/whisper-podlodka-turbo
        hf_token=hf_token,
        device="auto",
        output_dir="./output"
    )

    # Process audio
    audio_path = "path/to/your/audio.wav"
    if not Path(audio_path).exists():
        print(f"Error: Audio file not found: {audio_path}")
        print("Please update the audio_path variable with your audio file")
        return

    results = pipeline.process_audio(
        audio_path=audio_path,
        num_speakers=2,  # Expecting 2 speakers
        extract_keywords=True,
        keyword_method="textrank",
        top_keywords=15,
        save_formats=["json", "txt"]
    )

    print("\nProcessing completed!")
    print(f"Results saved to: {results['output_files']}")


if __name__ == "__main__":
    print("LLCAR Video Processing Pipeline - Example Usage")
    print("=" * 60)
    print("\n1. Video processing example")
    print("2. Audio processing example")
    print("\nUpdate the file paths in this script and run:")
    print("  python examples.py")
    print("\nOr use the CLI:")
    print("  python main.py --video video.mp4")
    print("=" * 60)

    # Uncomment to run examples:
    # example_video_processing()
    # example_audio_processing()
