#!/usr/bin/env python3
"""
LLCAR Interactive Console - Demo/Example Script

This script demonstrates the interactive console functionality without requiring
actual video processing. It shows the key features and capabilities.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.console import InteractiveConsole


def demo_console_features():
    """Demonstrate console features."""
    print("=" * 70)
    print("LLCAR Interactive Console - Feature Demonstration")
    print("=" * 70)
    print()

    # Create console instance
    config = {
        'language': 'en',
        'model_variant': 'default',
        'device': 'auto',
        'output': {
            'directory': './output',
            'formats': ['json', 'txt', 'csv']
        },
        'keywords': {
            'enabled': True,
            'method': 'tfidf',
            'top_n': 10
        },
        'postprocessing': {
            'remove_fillers': True,
            'remove_profanity': True
        },
        'audio': {
            'sample_rate': 16000,
            'channels': 1
        }
    }

    console = InteractiveConsole(config=config)

    print("✅ Console initialized successfully!\n")

    # Demonstrate features
    print("📋 Console Features:")
    print("-" * 70)

    features = [
        ("Interactive Menu", "User-friendly menu-driven interface"),
        ("File Browser", "Browse and select video/audio files"),
        ("Single File Processing", "Process one video or audio file"),
        ("Batch Processing", "Process multiple files at once"),
        ("History Tracking", "Track all processing operations"),
        ("Settings Management", "Configure parameters interactively"),
        ("Configuration Display", "View current settings"),
        ("Help System", "Built-in documentation and help"),
        ("Export History", "Save processing history to JSON"),
    ]

    for idx, (feature, description) in enumerate(features, 1):
        print(f"{idx}. {feature:25s} - {description}")

    print()

    # Demonstrate configuration
    print("⚙️  Current Configuration:")
    print("-" * 70)
    print(f"Language:          {config['language']}")
    print(f"Model variant:     {config['model_variant']}")
    print(f"Device:            {config['device']}")
    print(f"Output directory:  {config['output']['directory']}")
    print(f"Output formats:    {', '.join(config['output']['formats'])}")
    print(f"Keywords enabled:  {config['keywords']['enabled']}")
    print(f"Keyword method:    {config['keywords']['method']}")
    print()

    # Demonstrate history structure
    print("📜 History Structure Example:")
    print("-" * 70)

    sample_history = [
        {
            'timestamp': '2026-02-05T20:00:00',
            'type': 'video',
            'file': '/path/to/interview.mp4',
            'language': 'en',
            'status': 'completed',
            'processing_time': 45.23,
            'output_files': {
                'json': '/output/interview_report.json',
                'txt': '/output/interview_transcript.txt',
                'csv': '/output/interview_segments.csv'
            }
        },
        {
            'timestamp': '2026-02-05T20:10:00',
            'type': 'audio',
            'file': '/path/to/podcast.wav',
            'language': 'ru',
            'status': 'completed',
            'processing_time': 120.45,
            'batch': True
        }
    ]

    console.history = sample_history

    for idx, entry in enumerate(console.history, 1):
        status_icon = "✅" if entry['status'] == 'completed' else "❌"
        print(f"\n{idx}. {status_icon} {entry['type'].upper()}")
        print(f"   Time: {entry['timestamp']}")
        print(f"   File: {Path(entry['file']).name}")
        print(f"   Language: {entry['language']}")
        if entry['status'] == 'completed':
            print(f"   Duration: {entry.get('processing_time', 0):.2f}s")
            if 'batch' in entry:
                print(f"   Batch: {entry['batch']}")

    print()

    # Demonstrate supported formats
    print("📖 Supported File Formats:")
    print("-" * 70)
    print("Video formats:")
    print("  • MP4, AVI, MKV, MOV, WebM")
    print()
    print("Audio formats:")
    print("  • WAV, MP3, FLAC, OGG, M4A")
    print()

    # Demonstrate supported languages
    print("🌍 Supported Languages:")
    print("-" * 70)
    print("  • English (en) - WhisperX, Whisper large-v3")
    print("  • Russian (ru) - bond005/whisper-podlodka-turbo")
    print("  • Chinese (zh) - Whisper large-v3")
    print()

    # Usage examples
    print("💡 Usage Examples:")
    print("-" * 70)
    print()
    print("1. Launch interactive console:")
    print("   python main.py --interactive")
    print()
    print("2. Using the launcher:")
    print("   python console.py")
    print()
    print("3. Via Make:")
    print("   make console")
    print()
    print("4. Process single video (CLI):")
    print("   python main.py --video input/video.mp4 --language en")
    print()
    print("5. Batch process directory:")
    print("   Select option 3 in interactive console")
    print()

    print("=" * 70)
    print("📚 For more information:")
    print("  • README.md - Full documentation")
    print("  • CONSOLE.md - Interactive console guide")
    print("  • QUICKSTART.md - Quick start guide")
    print("=" * 70)
    print()
    print("✅ Demo completed successfully!")
    print()


if __name__ == "__main__":
    demo_console_features()
