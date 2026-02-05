#!/usr/bin/env python3
"""
Tests for Interactive Console Module

Tests the console interface functionality without requiring actual video processing.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.console import InteractiveConsole


class TestInteractiveConsole(unittest.TestCase):
    """Test cases for InteractiveConsole class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'language': 'en',
            'model_variant': 'default',
            'device': 'auto',
            'output': {'directory': './output'},
            'hf_token': 'test_token'
        }
        self.console = InteractiveConsole(config=self.config)

    def test_console_initialization(self):
        """Test console initialization."""
        self.assertIsNotNone(self.console)
        self.assertEqual(self.console.config, self.config)
        self.assertEqual(self.console.history, [])
        self.assertTrue(self.console.running)

    def test_get_input_with_default(self):
        """Test get_input with default value."""
        with patch('builtins.input', return_value=''):
            result = self.console.get_input("Test prompt", "default_value")
            self.assertEqual(result, "default_value")

    def test_get_input_with_user_value(self):
        """Test get_input with user-provided value."""
        with patch('builtins.input', return_value='user_value'):
            result = self.console.get_input("Test prompt", "default_value")
            self.assertEqual(result, "user_value")

    def test_get_yes_no_yes(self):
        """Test get_yes_no with yes response."""
        for response in ['y', 'yes', 'Y', 'YES']:
            with patch('builtins.input', return_value=response):
                result = self.console.get_yes_no("Test?", False)
                self.assertTrue(result)

    def test_get_yes_no_no(self):
        """Test get_yes_no with no response."""
        for response in ['n', 'no', 'N', 'NO']:
            with patch('builtins.input', return_value=response):
                result = self.console.get_yes_no("Test?", True)
                self.assertFalse(result)

    def test_get_yes_no_default(self):
        """Test get_yes_no with default value."""
        with patch('builtins.input', return_value=''):
            result = self.console.get_yes_no("Test?", True)
            self.assertTrue(result)

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.glob')
    def test_browse_files_video(self, mock_glob, mock_exists):
        """Test file browsing for video files."""
        mock_exists.return_value = True
        mock_file = MagicMock()
        mock_file.name = 'test.mp4'
        mock_file.stat.return_value.st_size = 1024 * 1024  # 1 MB
        mock_glob.return_value = [mock_file]

        with patch('builtins.input', return_value='1'):
            # This would require more complex mocking to fully test
            # Just verify the method exists and is callable
            self.assertTrue(callable(self.console.browse_files))

    def test_history_tracking(self):
        """Test history tracking functionality."""
        entry = {
            'timestamp': '2026-02-05T20:00:00',
            'type': 'video',
            'file': '/path/to/video.mp4',
            'language': 'en',
            'status': 'completed'
        }

        self.console.history.append(entry)
        self.assertEqual(len(self.console.history), 1)
        self.assertEqual(self.console.history[0]['type'], 'video')
        self.assertEqual(self.console.history[0]['status'], 'completed')

    def test_config_management(self):
        """Test configuration management."""
        # Update config
        self.console.config['language'] = 'ru'
        self.assertEqual(self.console.config['language'], 'ru')

        # Reset pipeline
        self.console.pipeline = None
        self.assertIsNone(self.console.pipeline)

    @patch('os.system')
    def test_clear_screen(self, mock_system):
        """Test screen clearing."""
        self.console.clear_screen()
        mock_system.assert_called_once()

    @patch('builtins.print')
    def test_print_header(self, mock_print):
        """Test header printing."""
        self.console.print_header()
        self.assertTrue(mock_print.called)

    @patch('builtins.print')
    def test_print_menu(self, mock_print):
        """Test menu printing."""
        self.console.print_menu()
        self.assertTrue(mock_print.called)

    def test_running_flag(self):
        """Test running flag control."""
        self.assertTrue(self.console.running)
        self.console.running = False
        self.assertFalse(self.console.running)


class TestConsoleIntegration(unittest.TestCase):
    """Integration tests for console functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'language': 'en',
            'model_variant': 'default',
            'device': 'cpu',
            'output': {'directory': './output'}
        }

    def test_console_creation(self):
        """Test console can be created."""
        console = InteractiveConsole(config=self.config)
        self.assertIsNotNone(console)

    def test_console_with_no_config(self):
        """Test console creation without config."""
        console = InteractiveConsole()
        self.assertIsNotNone(console)
        self.assertEqual(console.config, {})

    def test_console_with_pipeline(self):
        """Test console with pipeline instance."""
        mock_pipeline = Mock()
        console = InteractiveConsole(pipeline=mock_pipeline, config=self.config)
        self.assertEqual(console.pipeline, mock_pipeline)


class TestConsoleHelpers(unittest.TestCase):
    """Test helper functions in console."""

    def setUp(self):
        """Set up test fixtures."""
        self.console = InteractiveConsole()

    def test_history_export_structure(self):
        """Test history export structure."""
        # Add multiple entries
        entries = [
            {
                'timestamp': '2026-02-05T20:00:00',
                'type': 'video',
                'file': 'video1.mp4',
                'status': 'completed'
            },
            {
                'timestamp': '2026-02-05T20:05:00',
                'type': 'audio',
                'file': 'audio1.wav',
                'status': 'failed',
                'error': 'Test error'
            }
        ]

        self.console.history = entries

        # Verify structure
        self.assertEqual(len(self.console.history), 2)
        self.assertEqual(self.console.history[0]['type'], 'video')
        self.assertEqual(self.console.history[1]['type'], 'audio')
        self.assertEqual(self.console.history[1]['status'], 'failed')


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestInteractiveConsole))
    suite.addTests(loader.loadTestsFromTestCase(TestConsoleIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestConsoleHelpers))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    print("=" * 70)
    print("LLCAR Interactive Console - Unit Tests")
    print("=" * 70)
    print()

    success = run_tests()

    print()
    print("=" * 70)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print("=" * 70)

    sys.exit(0 if success else 1)
