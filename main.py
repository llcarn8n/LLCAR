#!/usr/bin/env python3
"""
LLCAR Video Processing Pipeline - Main CLI Entry Point

Command-line interface for processing videos to text with speaker diarization.
"""

import argparse
import sys
import os
import logging
from pathlib import Path
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.pipeline import VideoPipeline


def setup_logging(level: str = "INFO", log_file: str = None):
    """Setup logging configuration."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=handlers
    )


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    config_path = Path(config_path)

    if not config_path.exists():
        logging.warning(f"Config file not found: {config_path}. Using defaults.")
        return {}

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config or {}
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        return {}


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="LLCAR Video Processing Pipeline - Convert video to text with speaker diarization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch interactive console mode
  python main.py --interactive

  # Launch graphical user interface
  python main.py --gui

  # Process a video file
  python main.py --video /path/to/video.mp4

  # Process an audio file directly
  python main.py --audio /path/to/audio.wav

  # Process with specific language and model
  python main.py --video video.mp4 --language ru --model-variant default

  # Process with custom number of speakers
  python main.py --video video.mp4 --num-speakers 2

  # Save output in specific formats
  python main.py --video video.mp4 --formats json txt csv plain

  # Use custom configuration file
  python main.py --video video.mp4 --config custom_config.yaml
        """
    )

    # Mode arguments
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Launch interactive console mode'
    )
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Launch graphical user interface (GUI) mode'
    )

    # Input arguments
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument(
        '--video', '-v',
        type=str,
        help='Path to input video file'
    )
    input_group.add_argument(
        '--audio', '-a',
        type=str,
        help='Path to input audio file'
    )

    # Configuration arguments
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )

    # Language and model arguments
    parser.add_argument(
        '--language', '-l',
        type=str,
        choices=['en', 'ru', 'zh'],
        help='Language code (en=English, ru=Russian, zh=Chinese)'
    )

    parser.add_argument(
        '--model-variant', '-m',
        type=str,
        help='Model variant (default, alternative, turbo, whisperx)'
    )

    # Diarization arguments
    parser.add_argument(
        '--num-speakers', '-n',
        type=int,
        help='Expected number of speakers (optional)'
    )

    # Output arguments
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        help='Output directory (default: ./output)'
    )

    parser.add_argument(
        '--formats', '-f',
        nargs='+',
        choices=['json', 'csv', 'txt', 'plain'],
        help='Output formats (default: json txt). Use "plain" for plain text without timestamps/speakers'
    )

    # Keyword extraction arguments
    parser.add_argument(
        '--no-keywords',
        action='store_true',
        help='Disable keyword extraction'
    )

    parser.add_argument(
        '--keyword-method',
        type=str,
        choices=['tfidf', 'textrank'],
        help='Keyword extraction method (default: tfidf)'
    )

    parser.add_argument(
        '--top-keywords',
        type=int,
        help='Number of top keywords to extract (default: 10)'
    )

    # Device argument
    parser.add_argument(
        '--device',
        type=str,
        choices=['auto', 'cuda', 'cpu'],
        help='Device to use (default: auto)'
    )

    # HuggingFace token
    parser.add_argument(
        '--hf-token',
        type=str,
        help='HuggingFace token for pyannote (or set HF_TOKEN env var)'
    )

    # Logging arguments
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level (default: INFO)'
    )

    parser.add_argument(
        '--log-file',
        type=str,
        help='Log file path'
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Setup logging
    log_level = args.log_level or config.get('logging', {}).get('level', 'INFO')
    log_file = args.log_file or config.get('logging', {}).get('log_file')
    setup_logging(log_level, log_file)

    logger = logging.getLogger(__name__)

    # Check if interactive mode
    if args.interactive:
        logger.info("Starting LLCAR in interactive console mode")
        from src.console import InteractiveConsole
        console = InteractiveConsole(config=config)
        return console.run()

    # Check if GUI mode
    if args.gui:
        logger.info("Starting LLCAR in GUI mode")
        from gui import main as gui_main
        gui_main()
        return 0

    # Check if video or audio is provided
    if not args.video and not args.audio:
        parser.print_help()
        print("\nError: Either --video, --audio, --interactive, or --gui must be specified")
        return 1

    logger.info("Starting LLCAR Video Processing Pipeline")

    # Determine parameters (CLI args override config)
    language = args.language or config.get('language', 'en')
    model_variant = args.model_variant or config.get('model_variant', 'default')
    device = args.device or config.get('device', 'auto')
    output_dir = args.output_dir or config.get('output', {}).get('directory', './output')

    # HuggingFace token
    hf_token = args.hf_token or config.get('hf_token') or os.getenv('HF_TOKEN')

    if not hf_token:
        logger.error(
            "HuggingFace token is required for speaker diarization. "
            "Set HF_TOKEN environment variable, use --hf-token argument, "
            "or add it to config.yaml"
        )
        sys.exit(1)

    # Diarization parameters
    num_speakers = args.num_speakers or config.get('diarization', {}).get('num_speakers')

    # Output formats
    if args.formats:
        save_formats = args.formats
    else:
        save_formats = config.get('output', {}).get('formats', ['json', 'txt'])

    # Keyword extraction parameters
    extract_keywords = not args.no_keywords and config.get('keywords', {}).get('enabled', True)
    keyword_method = args.keyword_method or config.get('keywords', {}).get('method', 'tfidf')
    top_keywords = args.top_keywords or config.get('keywords', {}).get('top_n', 10)

    # Audio processing parameters
    enable_noise_reduction = config.get('audio', {}).get('noise_reduction', True)

    try:
        # Initialize pipeline
        logger.info(f"Initializing pipeline with language={language}, model={model_variant}, device={device}")
        if enable_noise_reduction:
            logger.info("Audio noise reduction: ENABLED")
        pipeline = VideoPipeline(
            language=language,
            model_variant=model_variant,
            hf_token=hf_token,
            device=device,
            output_dir=output_dir,
            enable_noise_reduction=enable_noise_reduction
        )

        # Process input
        if args.video:
            logger.info(f"Processing video: {args.video}")
            results = pipeline.process_video(
                video_path=args.video,
                num_speakers=num_speakers,
                extract_keywords=extract_keywords,
                keyword_method=keyword_method,
                top_keywords=top_keywords,
                save_formats=save_formats
            )
        else:
            logger.info(f"Processing audio: {args.audio}")
            results = pipeline.process_audio(
                audio_path=args.audio,
                num_speakers=num_speakers,
                extract_keywords=extract_keywords,
                keyword_method=keyword_method,
                top_keywords=top_keywords,
                save_formats=save_formats
            )

        # Print summary
        print("\n" + "=" * 70)
        print("PROCESSING COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"Total processing time: {results['total_processing_time']:.2f} seconds")
        print(f"Number of segments: {results['steps'].get('transcription', {}).get('num_segments', 0)}")
        print(f"Number of speakers: {results['steps'].get('diarization', {}).get('num_speakers', 0)}")

        if extract_keywords:
            print(f"Keywords extracted: {len(results.get('keywords', []))}")

        print("\nOutput files:")
        for format_type, file_path in results.get('output_files', {}).items():
            print(f"  - {format_type.upper()}: {file_path}")

        print("=" * 70)

        return 0

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        print("\n" + "=" * 70)
        print("PROCESSING FAILED")
        print("=" * 70)
        print(f"Error: {e}")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
