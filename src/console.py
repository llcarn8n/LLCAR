"""
Interactive Console Interface for LLCAR Video Processing Pipeline

Provides a user-friendly menu-driven interface for processing video and audio files.
"""

import os
import sys
import logging
import platform
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# ANSI color codes (supported on Windows 10+ and all modern terminals)
_BOLD = "\033[1m"
_DIM = "\033[2m"
_GREEN = "\033[92m"
_YELLOW = "\033[93m"
_RED = "\033[91m"
_CYAN = "\033[96m"
_BLUE = "\033[94m"
_RESET = "\033[0m"


class InteractiveConsole:
    """
    Interactive console interface for LLCAR pipeline.

    Features:
    - Menu-driven interface
    - File browser and batch processing
    - Real-time progress display
    - Session history
    - Settings management
    """

    def __init__(self, pipeline=None, config: Dict[str, Any] = None):
        """
        Initialize interactive console.

        Args:
            pipeline: VideoPipeline instance (optional, can be created later)
            config: Configuration dictionary
        """
        self.pipeline = pipeline
        self.config = config or {}
        self.history = []
        self.running = True

    def clear_screen(self):
        """Clear the console screen using ANSI escape codes."""
        print("\033[2J\033[H", end="", flush=True)

    def print_header(self):
        """Print the application header with system info."""
        print()
        print(f"{_BOLD}{_CYAN}" + "=" * 70 + _RESET)
        print(f"{_BOLD}{_CYAN}"
              "    __    __   ______   ___    ____\n"
              "   / /   / /  / ____/  /   |  / __ \\\n"
              "  / /   / /  / /      / /| | / /_/ /\n"
              " / /___/ /_ / /___   / ___ |/ _, _/\n"
              "/_____/____/\\____/  /_/  |_/_/ |_|"
              f"{_RESET}")
        print(f"{_DIM}  Video & Audio Processing Pipeline v1.0.0{_RESET}")
        print(f"{_CYAN}" + "=" * 70 + _RESET)

        # System info line
        has_token = bool(self.config.get('hf_token') or os.getenv('HF_TOKEN'))
        token_status = f"{_GREEN}OK{_RESET}" if has_token else f"{_RED}not set{_RESET}"
        device = self.config.get('device', 'auto')
        lang = self.config.get('language', 'en')
        print(f"  {_DIM}OS:{_RESET} {platform.system()} {platform.machine()}"
              f"  {_DIM}Lang:{_RESET} {lang}"
              f"  {_DIM}Device:{_RESET} {device}"
              f"  {_DIM}HF Token:{_RESET} {token_status}")

    def print_menu(self):
        """Print main menu."""
        W = 66  # inner width
        print()
        print(f"  {_BOLD}┌─ Main Menu ─" + "─" * (W - 14) + f"┐{_RESET}")
        items = [
            ("1", "Process single video file",  ""),
            ("2", "Process single audio file",   ""),
            ("3", "Batch process multiple files", ""),
            ("4", "Quick process (drag & drop)",  f"{_GREEN}NEW{_RESET}"),
            ("5", "View processing history",      ""),
            ("6", "Configure settings",           ""),
            ("7", "Show current configuration",   ""),
            ("8", "Help & Documentation",         ""),
            ("0", "Exit",                         ""),
        ]
        for num, label, badge in items:
            badge_text = f" [{badge}]" if badge else ""
            # Calculate visible length (without ANSI codes)
            visible_len = len(f"  {num}. {label}") + (len(badge_text) - (len(badge) - len(badge.replace('\033', ''))) if badge else 0)
            # Just pad with spaces to roughly align
            line = f"  {_BOLD}{num}.{_RESET} {label}{badge_text}"
            print(f"  │{line:<{W + 20}}│")
        print(f"  {_BOLD}└" + "─" * W + f"┘{_RESET}")

    def get_input(self, prompt: str, default: str = None) -> str:
        """
        Get user input with optional default value.

        Args:
            prompt: Input prompt
            default: Default value

        Returns:
            User input or default
        """
        if default:
            full_prompt = f"{prompt} [{default}]: "
        else:
            full_prompt = f"{prompt}: "

        value = input(full_prompt).strip()
        return value if value else default

    def get_yes_no(self, prompt: str, default: bool = False) -> bool:
        """
        Get yes/no input from user.

        Args:
            prompt: Question prompt
            default: Default value

        Returns:
            True for yes, False for no
        """
        default_str = "Y/n" if default else "y/N"
        response = self.get_input(f"{prompt} ({default_str})",
                                  "y" if default else "n").lower()
        return response in ['y', 'yes', 'да', 'д']

    def browse_files(self, file_type: str = "video") -> Optional[str]:
        """
        Browse and select a file.

        Args:
            file_type: Type of file to browse ('video' or 'audio')

        Returns:
            Selected file path or None
        """
        if file_type == "video":
            extensions = ['.mp4', '.m4v', '.avi', '.mkv', '.mov', '.webm', '.wmv', '.flv', '.mpg', '.mpeg']
        else:
            extensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.wma', '.aac', '.opus']

        print(f"\n📁 Browsing for {file_type} files...")

        # Check input directory
        input_dir = Path("./input")
        if input_dir.exists():
            files = []
            for ext in extensions:
                files.extend(input_dir.glob(f"*{ext}"))

            if files:
                print(f"\nFound {len(files)} file(s) in ./input directory:")
                for idx, file in enumerate(files, 1):
                    file_size = file.stat().st_size / (1024 * 1024)  # MB
                    print(f"  {idx}. {file.name} ({file_size:.2f} MB)")

                choice = self.get_input("\nSelect file number or enter custom path", "1")

                try:
                    if choice.isdigit() and 1 <= int(choice) <= len(files):
                        return str(files[int(choice) - 1])
                except ValueError:
                    pass

                # Custom path
                if choice and Path(choice).exists():
                    return choice

        # Manual path entry
        path = self.get_input(f"\nEnter {file_type} file path")
        if path and Path(path).exists():
            return path
        elif path:
            print(f"❌ Error: File not found: {path}")

        return None

    def _ensure_pipeline(self, language: str) -> bool:
        """
        Ensure the pipeline is initialized. Creates it if needed.

        Args:
            language: Language code for the pipeline

        Returns:
            True if pipeline is ready, False on error
        """
        if self.pipeline:
            return True

        from .pipeline import VideoPipeline
        hf_token = self.config.get('hf_token') or os.getenv('HF_TOKEN')
        if not hf_token:
            print("\n❌ Error: HuggingFace token not configured!")
            print("Please set HF_TOKEN environment variable or configure in settings.")
            input("\nPress Enter to continue...")
            return False

        print("\n⏳ Initializing pipeline...")
        try:
            self.pipeline = VideoPipeline(
                language=language,
                model_variant=self.config.get('model_variant', 'default'),
                hf_token=hf_token,
                device=self.config.get('device', 'auto'),
                output_dir=self.config.get('output', {}).get('directory', './output')
            )
            return True
        except Exception as e:
            print(f"\n❌ Error initializing pipeline: {e}")
            input("\nPress Enter to continue...")
            return False

    def _get_processing_options(self):
        """
        Collect common processing options from user.

        Returns:
            Tuple of (language, num_speakers, extract_keywords, keyword_method,
                      top_keywords, save_formats)
        """
        print("\n⚙️  Processing Options:")

        language = self.get_input("Language (en/ru/zh)",
                                  self.config.get('language', 'en'))

        num_speakers_str = self.get_input("Number of speakers (leave empty for auto-detection)", "")
        num_speakers = int(num_speakers_str) if num_speakers_str and num_speakers_str.isdigit() else None

        extract_keywords = self.get_yes_no("Extract keywords?", True)

        keyword_method = "tfidf"
        top_keywords = 10
        if extract_keywords:
            keyword_method = self.get_input("Keyword method (tfidf/textrank)", "tfidf")
            top_keywords_str = self.get_input("Number of top keywords", "10")
            top_keywords = int(top_keywords_str) if top_keywords_str.isdigit() else 10

        print("\nOutput formats: json, txt, csv, plain")
        formats_input = self.get_input("Select formats (comma-separated)", "json,txt")
        save_formats = [f.strip() for f in formats_input.split(',')]

        return language, num_speakers, extract_keywords, keyword_method, top_keywords, save_formats

    def _print_processing_summary(self, file_path, language, num_speakers,
                                  extract_keywords, keyword_method, top_keywords,
                                  save_formats):
        """Print a summary of the processing options before starting."""
        print("\n" + "─" * 70)
        print("📋 Processing Summary:")
        print(f"  File: {file_path}")
        print(f"  Language: {language}")
        print(f"  Speakers: {num_speakers or 'auto-detect'}")
        print(f"  Keywords: {extract_keywords}")
        if extract_keywords:
            print(f"  Keyword method: {keyword_method}")
            print(f"  Top keywords: {top_keywords}")
        print(f"  Output formats: {', '.join(save_formats)}")
        print("─" * 70)

    def _print_results(self, results, extract_keywords):
        """Print processing results."""
        print("\n" + "=" * 70)
        print("✅ PROCESSING COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"⏱️  Total time: {results['total_processing_time']:.2f} seconds")
        print(f"📝 Segments: {results['steps'].get('transcription', {}).get('num_segments', 0)}")
        print(f"👥 Speakers: {results['steps'].get('diarization', {}).get('num_speakers', 0)}")

        if extract_keywords:
            print(f"🔑 Keywords: {len(results.get('keywords', []))}")

        print("\n📄 Output files:")
        for format_type, file_path in results.get('output_files', {}).items():
            print(f"  • {format_type.upper()}: {file_path}")

        print("=" * 70)

    def _process_single_file(self, file_type: str):
        """
        Process a single video or audio file.

        Args:
            file_type: 'video' or 'audio'
        """
        label = "📹 Process Single Video File" if file_type == "video" else "🎵 Process Single Audio File"
        print("\n" + "─" * 70)
        print(label)
        print("─" * 70)

        # Get file path
        file_path = self.browse_files(file_type)
        if not file_path:
            print("❌ No file selected. Returning to main menu.")
            input("\nPress Enter to continue...")
            return

        # Get processing options
        language, num_speakers, extract_keywords, keyword_method, top_keywords, save_formats = \
            self._get_processing_options()

        # Confirm
        self._print_processing_summary(file_path, language, num_speakers,
                                       extract_keywords, keyword_method,
                                       top_keywords, save_formats)

        if not self.get_yes_no("\nProceed with processing?", True):
            print("❌ Processing cancelled.")
            input("\nPress Enter to continue...")
            return

        # Initialize pipeline if needed
        if not self._ensure_pipeline(language):
            return

        # Process file
        print(f"\n🚀 Starting {file_type} processing...")
        print("This may take a while depending on file size and hardware.\n")

        try:
            if file_type == "video":
                results = self.pipeline.process_video(
                    video_path=file_path,
                    num_speakers=num_speakers,
                    extract_keywords=extract_keywords,
                    keyword_method=keyword_method,
                    top_keywords=top_keywords,
                    save_formats=save_formats
                )
            else:
                results = self.pipeline.process_audio(
                    audio_path=file_path,
                    num_speakers=num_speakers,
                    extract_keywords=extract_keywords,
                    keyword_method=keyword_method,
                    top_keywords=top_keywords,
                    save_formats=save_formats
                )

            self._print_results(results, extract_keywords)

            self.history.append({
                'timestamp': datetime.now().isoformat(),
                'type': file_type,
                'file': file_path,
                'language': language,
                'status': 'completed',
                'processing_time': results['total_processing_time'],
                'output_files': results.get('output_files', {})
            })

        except Exception as e:
            print("\n" + "=" * 70)
            print("❌ PROCESSING FAILED")
            print("=" * 70)
            print(f"Error: {e}")
            print("=" * 70)

            self.history.append({
                'timestamp': datetime.now().isoformat(),
                'type': file_type,
                'file': file_path,
                'language': language,
                'status': 'failed',
                'error': str(e)
            })

        input("\nPress Enter to continue...")

    def process_single_video(self):
        """Process a single video file."""
        self._process_single_file("video")

    def process_single_audio(self):
        """Process a single audio file."""
        self._process_single_file("audio")

    def batch_process(self):
        """Batch process multiple files."""
        print("\n" + "─" * 70)
        print("📦 Batch Process Multiple Files")
        print("─" * 70)

        print("\nThis feature allows you to process multiple video/audio files.")
        print("All files will be processed with the same settings.")

        # Get directory
        directory = self.get_input("\nEnter directory path", "./input")
        dir_path = Path(directory)

        if not dir_path.exists():
            print(f"❌ Error: Directory not found: {directory}")
            input("\nPress Enter to continue...")
            return

        # Find files
        video_extensions = ['.mp4', '.m4v', '.avi', '.mkv', '.mov', '.webm', '.wmv', '.flv', '.mpg', '.mpeg']
        audio_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.wma', '.aac', '.opus']

        all_files = []
        for ext in video_extensions + audio_extensions:
            all_files.extend(dir_path.glob(f"*{ext}"))

        if not all_files:
            print(f"❌ No video or audio files found in: {directory}")
            input("\nPress Enter to continue...")
            return

        print(f"\n✅ Found {len(all_files)} file(s):")
        for idx, file in enumerate(all_files, 1):
            file_size = file.stat().st_size / (1024 * 1024)
            print(f"  {idx}. {file.name} ({file_size:.2f} MB)")

        if not self.get_yes_no(f"\nProcess all {len(all_files)} files?", True):
            print("❌ Batch processing cancelled.")
            input("\nPress Enter to continue...")
            return

        # Get common settings
        print("\n⚙️  Common Processing Settings:")
        language = self.get_input("Language (en/ru/zh)",
                                  self.config.get('language', 'en'))
        extract_keywords = self.get_yes_no("Extract keywords?", True)

        keyword_method = "tfidf"
        if extract_keywords:
            keyword_method = self.get_input("Keyword method (tfidf/textrank)", "tfidf")

        formats_input = self.get_input("Output formats (comma-separated, options: json,txt,csv,plain)", "json,txt")
        save_formats = [f.strip() for f in formats_input.split(',')]

        # Initialize pipeline if needed
        if not self._ensure_pipeline(language):
            return

        # Process files
        print(f"\n🚀 Starting batch processing of {len(all_files)} files...")

        successful = 0
        failed = 0

        for idx, file_path in enumerate(all_files, 1):
            print(f"\n[{idx}/{len(all_files)}] Processing: {file_path.name}")

            is_video = file_path.suffix.lower() in video_extensions

            try:
                if is_video:
                    results = self.pipeline.process_video(
                        video_path=str(file_path),
                        extract_keywords=extract_keywords,
                        keyword_method=keyword_method,
                        save_formats=save_formats
                    )
                else:
                    results = self.pipeline.process_audio(
                        audio_path=str(file_path),
                        extract_keywords=extract_keywords,
                        keyword_method=keyword_method,
                        save_formats=save_formats
                    )

                print(f"✅ Completed in {results['total_processing_time']:.2f}s")
                successful += 1

                self.history.append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'video' if is_video else 'audio',
                    'file': str(file_path),
                    'language': language,
                    'status': 'completed',
                    'processing_time': results['total_processing_time'],
                    'batch': True
                })

            except Exception as e:
                print(f"❌ Failed: {e}")
                failed += 1

                self.history.append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'video' if is_video else 'audio',
                    'file': str(file_path),
                    'language': language,
                    'status': 'failed',
                    'error': str(e),
                    'batch': True
                })

        # Summary
        print("\n" + "=" * 70)
        print("📊 BATCH PROCESSING SUMMARY")
        print("=" * 70)
        print(f"✅ Successful: {successful}/{len(all_files)}")
        print(f"❌ Failed: {failed}/{len(all_files)}")
        print("=" * 70)

        input("\nPress Enter to continue...")

    def view_history(self):
        """View processing history."""
        print("\n" + "─" * 70)
        print("📜 Processing History")
        print("─" * 70)

        if not self.history:
            print("\nNo processing history available.")
            input("\nPress Enter to continue...")
            return

        print(f"\nTotal entries: {len(self.history)}")
        print("\nRecent entries (newest first):")

        for idx, entry in enumerate(reversed(self.history[-10:]), 1):
            status_icon = "✅" if entry['status'] == 'completed' else "❌"
            print(f"\n{idx}. {status_icon} {entry['type'].upper()}")
            print(f"   Time: {entry['timestamp']}")
            print(f"   File: {Path(entry['file']).name}")
            print(f"   Language: {entry['language']}")

            if entry['status'] == 'completed':
                print(f"   Duration: {entry.get('processing_time', 0):.2f}s")
                if 'output_files' in entry:
                    print(f"   Outputs: {len(entry['output_files'])} file(s)")
            else:
                print(f"   Error: {entry.get('error', 'Unknown')}")

        # Export option
        if self.get_yes_no("\nExport history to JSON?", False):
            history_file = Path("./output/processing_history.json")
            history_file.parent.mkdir(exist_ok=True)

            with open(history_file, 'w') as f:
                json.dump(self.history, f, indent=2)

            print(f"✅ History exported to: {history_file}")

        input("\nPress Enter to continue...")

    def configure_settings(self):
        """Configure application settings."""
        print("\n" + "─" * 70)
        print("⚙️  Configure Settings")
        print("─" * 70)

        print("\nCurrent settings:")
        print(f"  Language: {self.config.get('language', 'en')}")
        print(f"  Model variant: {self.config.get('model_variant', 'default')}")
        print(f"  Device: {self.config.get('device', 'auto')}")
        print(f"  Output directory: {self.config.get('output', {}).get('directory', './output')}")

        if not self.get_yes_no("\nModify settings?", False):
            input("\nPress Enter to continue...")
            return

        # Update settings
        print("\n📝 Enter new values (or press Enter to keep current):")

        new_language = self.get_input(
            "Language (en/ru/zh)",
            self.config.get('language', 'en')
        )
        if new_language:
            self.config['language'] = new_language

        new_model = self.get_input(
            "Model variant",
            self.config.get('model_variant', 'default')
        )
        if new_model:
            self.config['model_variant'] = new_model

        new_device = self.get_input(
            "Device (auto/cuda/cpu)",
            self.config.get('device', 'auto')
        )
        if new_device:
            self.config['device'] = new_device

        new_output = self.get_input(
            "Output directory",
            self.config.get('output', {}).get('directory', './output')
        )
        if new_output:
            if 'output' not in self.config:
                self.config['output'] = {}
            self.config['output']['directory'] = new_output

        # HuggingFace token
        if self.get_yes_no("\nUpdate HuggingFace token?", False):
            new_token = self.get_input("HuggingFace token")
            if new_token:
                self.config['hf_token'] = new_token

        print("\n✅ Settings updated successfully!")
        print("Note: Pipeline will be reinitialized on next processing.")

        # Reset pipeline to force reinitialization
        self.pipeline = None

        input("\nPress Enter to continue...")

    def show_configuration(self):
        """Display current configuration."""
        print("\n" + "─" * 70)
        print("📋 Current Configuration")
        print("─" * 70)

        print("\n🌍 Language Settings:")
        print(f"  Language: {self.config.get('language', 'en')}")
        print(f"  Model variant: {self.config.get('model_variant', 'default')}")

        print("\n💻 Device Settings:")
        print(f"  Device: {self.config.get('device', 'auto')}")

        print("\n📁 Output Settings:")
        output_cfg = self.config.get('output', {})
        print(f"  Directory: {output_cfg.get('directory', './output')}")
        print(f"  Formats: {', '.join(output_cfg.get('formats', ['json', 'txt']))}")

        print("\n🔑 Keyword Extraction:")
        keywords_cfg = self.config.get('keywords', {})
        print(f"  Enabled: {keywords_cfg.get('enabled', True)}")
        print(f"  Method: {keywords_cfg.get('method', 'tfidf')}")
        print(f"  Top N: {keywords_cfg.get('top_n', 10)}")

        print("\n🔧 Post-processing:")
        postproc_cfg = self.config.get('postprocessing', {})
        print(f"  Remove fillers: {postproc_cfg.get('remove_fillers', True)}")
        print(f"  Remove profanity: {postproc_cfg.get('remove_profanity', True)}")

        print("\n🎵 Audio Settings:")
        audio_cfg = self.config.get('audio', {})
        print(f"  Sample rate: {audio_cfg.get('sample_rate', 16000)} Hz")
        print(f"  Channels: {audio_cfg.get('channels', 1)}")

        print("\n🔐 Authentication:")
        has_token = bool(self.config.get('hf_token') or os.getenv('HF_TOKEN'))
        print(f"  HuggingFace token: {'✅ Configured' if has_token else '❌ Not configured'}")

        input("\nPress Enter to continue...")

    def quick_process(self):
        """Quick process — enter a file path and go with sensible defaults."""
        print(f"\n{_BOLD}Quick Process{_RESET}")
        print("Enter the path to a video or audio file (or drag & drop it here).\n")

        path_input = self.get_input("File path")
        if not path_input:
            print(f"{_RED}No path provided.{_RESET}")
            input("\nPress Enter to continue...")
            return

        # Strip quotes that Windows adds when drag-and-dropping
        path_input = path_input.strip('"').strip("'")
        file_path = Path(path_input)

        if not file_path.exists():
            print(f"{_RED}File not found: {file_path}{_RESET}")
            input("\nPress Enter to continue...")
            return

        video_exts = {'.mp4', '.m4v', '.avi', '.mkv', '.mov', '.webm', '.wmv', '.flv', '.mpg', '.mpeg'}
        audio_exts = {'.wav', '.mp3', '.flac', '.ogg', '.m4a', '.wma', '.aac', '.opus'}
        ext = file_path.suffix.lower()

        if ext in video_exts:
            file_type = "video"
        elif ext in audio_exts:
            file_type = "audio"
        else:
            print(f"{_YELLOW}Unknown extension '{ext}'. Trying as video...{_RESET}")
            file_type = "video"

        language = self.config.get('language', 'en')
        print(f"\n  File:     {file_path.name} ({file_path.stat().st_size / 1048576:.1f} MB)")
        print(f"  Type:     {file_type}")
        print(f"  Language: {language}")
        print(f"  Output:   json, txt\n")

        if not self.get_yes_no("Start processing?", True):
            return

        if not self._ensure_pipeline(language):
            return

        print(f"\n{_CYAN}Processing...{_RESET}\n")

        try:
            if file_type == "video":
                results = self.pipeline.process_video(
                    video_path=str(file_path),
                    save_formats=["json", "txt"]
                )
            else:
                results = self.pipeline.process_audio(
                    audio_path=str(file_path),
                    save_formats=["json", "txt"]
                )
            self._print_results(results, extract_keywords=True)

            self.history.append({
                'timestamp': datetime.now().isoformat(),
                'type': file_type,
                'file': str(file_path),
                'language': language,
                'status': 'completed',
                'processing_time': results['total_processing_time'],
                'output_files': results.get('output_files', {})
            })
        except Exception as e:
            print(f"\n{_RED}Processing failed: {e}{_RESET}")

        input("\nPress Enter to continue...")

    def show_help(self):
        """Display help and documentation."""
        print("\n" + "─" * 70)
        print("📚 Help & Documentation")
        print("─" * 70)

        print("\n🎯 Quick Start:")
        print("  1. Place your video/audio files in the ./input directory")
        print("  2. Select option 1 or 2 from the main menu")
        print("  3. Follow the prompts to configure processing")
        print("  4. Results will be saved in the ./output directory")

        print("\n📖 Supported Formats:")
        print("  Video: MP4, AVI, MKV, MOV, WebM")
        print("  Audio: WAV, MP3, FLAC, OGG, M4A")

        print("\n🌍 Supported Languages:")
        print("  en - English (WhisperX, Whisper large-v3)")
        print("  ru - Russian (bond005/whisper-podlodka-turbo)")
        print("  zh - Chinese (Whisper large-v3)")

        print("\n⚙️  Processing Options:")
        print("  • Number of speakers: Auto-detect or specify (2, 3, etc.)")
        print("  • Keyword extraction: TF-IDF or TextRank methods")
        print("  • Output formats: JSON (detailed), TXT (readable), CSV (tabular), Plain (text only)")
        print("    - Plain format: Pure text without timestamps or speaker labels")

        print("\n💡 Tips:")
        print("  • For best results, use clean audio with minimal background noise")
        print("  • Specify number of speakers if known for better diarization")
        print("  • Use GPU (CUDA) for faster processing of large files")
        print("  • Check processing history to track your work")

        print("\n🔗 Resources:")
        print("  • README.md - Full documentation")
        print("  • QUICKSTART.md - Quick start guide")
        print("  • MODELS.md - Model comparison and benchmarks")
        print("  • GitHub: https://github.com/llcarn8n/LLCAR")

        input("\nPress Enter to continue...")

    def run(self):
        """Run the interactive console."""
        # Enable ANSI colors on Windows 10+
        if sys.platform == 'win32':
            os.system('')  # triggers VT100 processing

        while self.running:
            self.clear_screen()
            self.print_header()
            self.print_menu()

            choice = self.get_input(f"\n  {_BOLD}>{_RESET} Select option", "1")

            if choice == "1":
                self.process_single_video()
            elif choice == "2":
                self.process_single_audio()
            elif choice == "3":
                self.batch_process()
            elif choice == "4":
                self.quick_process()
            elif choice == "5":
                self.view_history()
            elif choice == "6":
                self.configure_settings()
            elif choice == "7":
                self.show_configuration()
            elif choice == "8":
                self.show_help()
            elif choice in ("0", "q", "exit", "quit"):
                print(f"\n{_CYAN}Thank you for using LLCAR! Goodbye.{_RESET}\n")
                self.running = False
            else:
                print(f"\n{_RED}Invalid option: {choice}{_RESET}")
                input("\nPress Enter to continue...")

        return 0
