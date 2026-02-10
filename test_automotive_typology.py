#!/usr/bin/env python3
"""
Test Automotive Typology Module
Basic tests to verify automotive entity detection and classification.
"""

import sys
import logging
from src.automotive_typology import AutomotiveTypologyAnalyzer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_basic_detection():
    """Test basic vehicle type and manufacturer detection."""
    print("\n" + "=" * 70)
    print("TEST 1: Basic Vehicle Detection (English)")
    print("=" * 70)

    analyzer = AutomotiveTypologyAnalyzer(language="en")

    test_text = "I bought a new Toyota Camry sedan last week. It's a great car!"

    result = analyzer.analyze_text(test_text)

    print(f"Input text: {test_text}")
    print(f"\nDetected entities:")
    print(f"  - Vehicle types: {result['vehicle_types']}")
    print(f"  - Manufacturers: {result['manufacturers']}")
    print(f"  - Models: {result['models']}")
    print(f"  - Total mentions: {result['total_automotive_mentions']}")

    # Assertions
    assert 'sedan' in result['vehicle_types'], "Should detect 'sedan'"
    assert 'toyota' in result['manufacturers'], "Should detect 'toyota'"
    assert 'camry' in result['models'], "Should detect 'camry'"
    assert result['total_automotive_mentions'] >= 3, "Should have at least 3 automotive mentions"

    print("\n✓ Test 1 passed!")


def test_russian_detection():
    """Test Russian language automotive detection."""
    print("\n" + "=" * 70)
    print("TEST 2: Russian Automotive Detection")
    print("=" * 70)

    analyzer = AutomotiveTypologyAnalyzer(language="ru")

    test_text = "Купил новую Ладу Весту, отличный седан за свои деньги. Двигатель работает хорошо."

    result = analyzer.analyze_text(test_text)

    print(f"Input text: {test_text}")
    print(f"\nDetected entities:")
    print(f"  - Vehicle types: {result['vehicle_types']}")
    print(f"  - Manufacturers: {result['manufacturers']}")
    print(f"  - Models: {result['models']}")
    print(f"  - Systems: {result['systems']}")
    print(f"  - Total mentions: {result['total_automotive_mentions']}")

    # Assertions - accept both Cyrillic and Latin versions
    assert 'sedan' in result['vehicle_types'], "Should detect 'sedan' (седан)"
    assert 'лада' in result['manufacturers'] or 'lada' in result['manufacturers'], "Should detect Lada"
    assert 'веста' in result['models'] or 'vesta' in result['models'], "Should detect Vesta"
    assert 'engine' in result['systems'], "Should detect 'engine' (двигатель)"

    print("\n✓ Test 2 passed!")


def test_diagnostic_detection():
    """Test automotive diagnostic terms detection."""
    print("\n" + "=" * 70)
    print("TEST 3: Diagnostic Terms Detection")
    print("=" * 70)

    analyzer = AutomotiveTypologyAnalyzer(language="en")

    test_text = "The engine is overheating and there's an oil leak. I need to schedule a repair and maintenance service."

    result = analyzer.analyze_text(test_text)

    print(f"Input text: {test_text}")
    print(f"\nDetected entities:")
    print(f"  - Systems: {result['systems']}")
    print(f"  - Diagnostic terms: {result['diagnostic_terms']}")
    print(f"  - Total mentions: {result['total_automotive_mentions']}")

    # Assertions
    assert 'engine' in result['systems'], "Should detect 'engine'"
    assert 'overheating' in result['diagnostic_terms'], "Should detect 'overheating'"
    assert 'leak' in result['diagnostic_terms'], "Should detect 'leak'"
    assert 'repair' in result['diagnostic_terms'], "Should detect 'repair'"
    assert 'maintenance' in result['diagnostic_terms'], "Should detect 'maintenance'"

    print("\n✓ Test 3 passed!")


def test_segments_analysis():
    """Test analysis of multiple segments."""
    print("\n" + "=" * 70)
    print("TEST 4: Multi-Segment Analysis")
    print("=" * 70)

    analyzer = AutomotiveTypologyAnalyzer(language="en")

    segments = [
        {
            'speaker': 'SPEAKER_00',
            'start': 0.0,
            'end': 5.0,
            'text': 'I own a Tesla Model 3 electric car.'
        },
        {
            'speaker': 'SPEAKER_01',
            'start': 5.0,
            'end': 10.0,
            'text': 'Nice! How is the battery performance?'
        },
        {
            'speaker': 'SPEAKER_00',
            'start': 10.0,
            'end': 15.0,
            'text': 'The battery is excellent. No issues so far.'
        },
        {
            'speaker': 'SPEAKER_01',
            'start': 15.0,
            'end': 20.0,
            'text': 'What about the weather today?'
        }
    ]

    result = analyzer.analyze_segments(segments)

    print(f"Total segments: {result['summary']['total_segments']}")
    print(f"Automotive segments: {result['summary']['total_automotive_segments']}")
    print(f"\nDetected manufacturers: {result['summary']['manufacturers']}")
    print(f"Detected models: {result['summary']['models']}")
    print(f"Detected vehicle types: {result['summary']['vehicle_types']}")
    print(f"Detected systems: {result['summary']['systems']}")

    # Assertions
    assert result['summary']['total_segments'] == 4, "Should have 4 segments"
    assert result['summary']['total_automotive_segments'] == 3, "Should have 3 automotive segments"
    assert any(m['manufacturer'] == 'tesla' for m in result['summary']['manufacturers']), "Should detect Tesla"
    assert any(m['model'] == 'model 3' for m in result['summary']['models']), "Should detect Model 3"

    print("\n✓ Test 4 passed!")


def test_empty_text():
    """Test handling of empty text."""
    print("\n" + "=" * 70)
    print("TEST 5: Empty Text Handling")
    print("=" * 70)

    analyzer = AutomotiveTypologyAnalyzer(language="en")

    result = analyzer.analyze_text("")

    print(f"Input text: (empty)")
    print(f"Result: {result}")

    # Assertions
    assert result['total_automotive_mentions'] == 0, "Empty text should have 0 mentions"
    assert len(result['vehicle_types']) == 0, "Should have no vehicle types"

    print("\n✓ Test 5 passed!")


def test_non_automotive_text():
    """Test that non-automotive text returns no detections."""
    print("\n" + "=" * 70)
    print("TEST 6: Non-Automotive Text")
    print("=" * 70)

    analyzer = AutomotiveTypologyAnalyzer(language="en")

    test_text = "I love reading books and going to the movies on weekends."

    result = analyzer.analyze_text(test_text)

    print(f"Input text: {test_text}")
    print(f"Result: {result}")

    # Assertions
    assert result['total_automotive_mentions'] == 0, "Non-automotive text should have 0 mentions"
    assert not analyzer.is_automotive_related(test_text), "Should not be classified as automotive-related"

    print("\n✓ Test 6 passed!")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("AUTOMOTIVE TYPOLOGY MODULE - TEST SUITE")
    print("=" * 70)

    try:
        test_basic_detection()
        test_russian_detection()
        test_diagnostic_detection()
        test_segments_analysis()
        test_empty_text()
        test_non_automotive_text()

        print("\n" + "=" * 70)
        print("ALL TESTS PASSED! ✓")
        print("=" * 70)
        return 0

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
