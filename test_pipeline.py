#!/usr/bin/env python3
"""
Test script for LLCAR Video Processing Pipeline
Tests individual components without requiring actual video files.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from src.audio_extraction import AudioExtractor
        from src.diarization import SpeakerDiarizer
        from src.transcription import Transcriber
        from src.postprocessing import TextPostProcessor, KeywordExtractor
        from src.output import OutputFormatter
        from src.pipeline import VideoPipeline
        print("✓ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_audio_extractor():
    """Test AudioExtractor initialization."""
    print("\nTesting AudioExtractor...")
    try:
        from src.audio_extraction import AudioExtractor
        extractor = AudioExtractor(sample_rate=16000, channels=1)
        print(f"✓ AudioExtractor initialized with sample_rate={extractor.sample_rate}")
        return True
    except Exception as e:
        print(f"✗ AudioExtractor error: {e}")
        return False


def test_text_processor():
    """Test TextPostProcessor."""
    print("\nTesting TextPostProcessor...")
    try:
        from src.postprocessing import TextPostProcessor

        # Test for different languages
        for lang in ['en', 'ru', 'zh']:
            processor = TextPostProcessor(language=lang)

            # Test text cleaning
            if lang == 'en':
                test_text = "um well like you know this is a test test"
                cleaned = processor.clean_text(test_text)
                print(f"✓ English: '{test_text}' -> '{cleaned}'")
            elif lang == 'ru':
                test_text = "ну вот это это тест тест"
                cleaned = processor.clean_text(test_text)
                print(f"✓ Russian: '{test_text}' -> '{cleaned}'")
            else:
                test_text = "这个 这个 测试 测试"
                cleaned = processor.clean_text(test_text)
                print(f"✓ Chinese: '{test_text}' -> '{cleaned}'")

        return True
    except Exception as e:
        print(f"✗ TextPostProcessor error: {e}")
        return False


def test_keyword_extractor():
    """Test KeywordExtractor."""
    print("\nTesting KeywordExtractor...")
    try:
        from src.postprocessing import KeywordExtractor

        extractor = KeywordExtractor(language='en')

        # Test TF-IDF
        texts = [
            "Machine learning is a subset of artificial intelligence",
            "Deep learning uses neural networks for pattern recognition",
            "Natural language processing helps computers understand human language"
        ]

        keywords = extractor.extract_tfidf_keywords(texts, top_n=5)
        print(f"✓ TF-IDF extracted {len(keywords)} keywords:")
        for kw in keywords[:3]:
            print(f"  - {kw['keyword']}: {kw['score']:.3f}")

        # Test TextRank
        combined_text = " ".join(texts)
        textrank_keywords = extractor.extract_textrank_keywords(combined_text, top_n=5)
        print(f"✓ TextRank extracted {len(textrank_keywords)} keywords:")
        for kw in textrank_keywords[:3]:
            print(f"  - {kw}")

        return True
    except Exception as e:
        print(f"✗ KeywordExtractor error: {e}")
        return False


def test_output_formatter():
    """Test OutputFormatter."""
    print("\nTesting OutputFormatter...")
    try:
        from src.output import OutputFormatter
        import tempfile
        import json

        # Use temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            formatter = OutputFormatter(output_dir=tmpdir)

            # Test data
            test_segments = [
                {
                    "speaker": "SPEAKER_00",
                    "start": 0.0,
                    "end": 3.5,
                    "text": "Hello, this is a test"
                },
                {
                    "speaker": "SPEAKER_01",
                    "start": 3.5,
                    "end": 7.0,
                    "text": "Yes, testing the system"
                }
            ]

            # Test JSON output
            json_path = formatter.save_json({"test": "data"}, "test.json")
            print(f"✓ JSON saved to {json_path}")

            # Test CSV output
            csv_path = formatter.save_csv(test_segments, "test.csv")
            print(f"✓ CSV saved to {csv_path}")

            # Test TXT output
            txt_path = formatter.save_text(test_segments, "test.txt")
            print(f"✓ TXT saved to {txt_path}")

            # Test plain text output
            plain_path = formatter.save_plain_text(test_segments, "test_plain.txt")
            print(f"✓ Plain TXT saved to {plain_path}")

            # Verify plain text content
            with open(plain_path, 'r', encoding='utf-8') as f:
                plain_content = f.read()
            expected_plain = "Hello, this is a test Yes, testing the system"
            if plain_content == expected_plain:
                print(f"✓ Plain text content verified")
            else:
                print(f"⚠ Plain text content: '{plain_content}'")

            # Test summary report
            report = formatter.create_summary_report(
                segments=test_segments,
                keywords=[{"keyword": "test", "score": 0.9}],
                speaker_stats={"SPEAKER_00": 3.5, "SPEAKER_01": 3.5}
            )
            print(f"✓ Summary report created with {report['statistics']['total_segments']} segments")

        return True
    except Exception as e:
        print(f"✗ OutputFormatter error: {e}")
        return False


def test_configuration():
    """Test configuration loading."""
    print("\nTesting configuration...")
    try:
        import yaml
        config_path = Path(__file__).parent / "config.yaml"

        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            print(f"✓ Configuration loaded: language={config.get('language')}")
            return True
        else:
            print("⚠ config.yaml not found (this is okay)")
            return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("LLCAR Video Processing Pipeline - Component Tests")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("AudioExtractor", test_audio_extractor),
        ("TextPostProcessor", test_text_processor),
        ("KeywordExtractor", test_keyword_extractor),
        ("OutputFormatter", test_output_formatter),
        ("Configuration", test_configuration),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Unexpected error in {name}: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
