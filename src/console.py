"""
Interactive Console Interface for LLCAR Video Processing Pipeline

Provides a user-friendly menu-driven interface for processing video and audio files.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


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
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        """Print the application header."""
        print("\n" + "=" * 70)
        print(" LLCAR - Video & Audio Processing Pipeline")
        print(" Interactive Console Mode")
        print("=" * 70)

    def print_menu(self):
        """Print main menu."""
        print("\n┌─ Main Menu ─────────────────────────────────────────────────────┐")
        print("│ 1. Process single video file                                    │")
        print("│ 2. Process single audio file                                    │")
        print("│ 3. Batch process multiple files                                 │")
        print("│ 4. View processing history                                      │")
        print("│ 5. Configure settings                                           │")
        print("│ 6. Show current configuration                                   │")
        print("│ 7. Help & Documentation                                         │")
        print("│ 8. Exit                                                          │")
        print("└──────────────────────────────────────────────────────────────────┘")

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
            extensions = ['.mp4', '.avi', '.mkv', '.mov', '.webm']
        else:
            extensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a']

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

    def process_single_video(self):
        """Process a single video file."""
        print("\n" + "─" * 70)
        print("📹 Process Single Video File")
        print("─" * 70)

        # Get file path
        video_path = self.browse_files("video")
        if not video_path:
            print("❌ No file selected. Returning to main menu.")
            input("\nPress Enter to continue...")
            return

        # Get processing options
        print("\n⚙️  Processing Options:")

        language = self.get_input("Language (en/ru/zh)",
                                 self.config.get('language', 'en'))

        num_speakers_str = self.get_input("Number of speakers (leave empty for auto-detection)", "")
        num_speakers = int(num_speakers_str) if num_speakers_str.isdigit() else None

        extract_keywords = self.get_yes_no("Extract keywords?", True)

        keyword_method = None
        top_keywords = 10
        if extract_keywords:
            keyword_method = self.get_input("Keyword method (tfidf/textrank)", "tfidf")
            top_keywords_str = self.get_input("Number of top keywords", "10")
            top_keywords = int(top_keywords_str) if top_keywords_str.isdigit() else 10

        # Output formats
        print("\nOutput formats: json, txt, csv")
        formats_input = self.get_input("Select formats (comma-separated)", "json,txt")
        save_formats = [f.strip() for f in formats_input.split(',')]

        # Confirm and process
        print("\n" + "─" * 70)
        print("📋 Processing Summary:")
        print(f"  File: {video_path}")
        print(f"  Language: {language}")
        print(f"  Speakers: {num_speakers or 'auto-detect'}")
        print(f"  Keywords: {extract_keywords}")
        if extract_keywords:
            print(f"  Keyword method: {keyword_method}")
            print(f"  Top keywords: {top_keywords}")
        print(f"  Output formats: {', '.join(save_formats)}")
        print("─" * 70)

        if not self.get_yes_no("\nProceed with processing?", True):
            print("❌ Processing cancelled.")
            input("\nPress Enter to continue...")
            return

        # Initialize pipeline if needed
        if not self.pipeline:
            from .pipeline import VideoPipeline
            hf_token = self.config.get('hf_token') or os.getenv('HF_TOKEN')
            if not hf_token:
                print("\n❌ Error: HuggingFace token not configured!")
                print("Please set HF_TOKEN environment variable or configure in settings.")
                input("\nPress Enter to continue...")
                return

            print("\n⏳ Initializing pipeline...")
            try:
                self.pipeline = VideoPipeline(
                    language=language,
                    model_variant=self.config.get('model_variant', 'default'),
                    hf_token=hf_token,
                    device=self.config.get('device', 'auto'),
                    output_dir=self.config.get('output', {}).get('directory', './output')
                )
            except Exception as e:
                print(f"\n❌ Error initializing pipeline: {e}")
                input("\nPress Enter to continue...")
                return

        # Process video
        print("\n🚀 Starting video processing...")
        print("This may take a while depending on file size and hardware.\n")

        try:
            results = self.pipeline.process_video(
                video_path=video_path,
                num_speakers=num_speakers,
                extract_keywords=extract_keywords,
                keyword_method=keyword_method,
                top_keywords=top_keywords,
                save_formats=save_formats
            )

            # Show results
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

            # Add to history
            self.history.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'video',
                'file': video_path,
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

            # Add to history
            self.history.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'video',
                'file': video_path,
                'language': language,
                'status': 'failed',
                'error': str(e)
            })

        input("\nPress Enter to continue...")

    def process_single_audio(self):
        """Process a single audio file."""
        print("\n" + "─" * 70)
        print("🎵 Process Single Audio File")
        print("─" * 70)

        # Get file path
        audio_path = self.browse_files("audio")
        if not audio_path:
            print("❌ No file selected. Returning to main menu.")
            input("\nPress Enter to continue...")
            return

        # Similar processing flow as video
        print("\n⚙️  Processing Options:")

        language = self.get_input("Language (en/ru/zh)",
                                 self.config.get('language', 'en'))

        num_speakers_str = self.get_input("Number of speakers (leave empty for auto-detection)", "")
        num_speakers = int(num_speakers_str) if num_speakers_str.isdigit() else None

        extract_keywords = self.get_yes_no("Extract keywords?", True)

        keyword_method = None
        top_keywords = 10
        if extract_keywords:
            keyword_method = self.get_input("Keyword method (tfidf/textrank)", "tfidf")
            top_keywords_str = self.get_input("Number of top keywords", "10")
            top_keywords = int(top_keywords_str) if top_keywords_str.isdigit() else 10

        print("\nOutput formats: json, txt, csv")
        formats_input = self.get_input("Select formats (comma-separated)", "json,txt")
        save_formats = [f.strip() for f in formats_input.split(',')]

        # Confirm and process
        print("\n" + "─" * 70)
        print("📋 Processing Summary:")
        print(f"  File: {audio_path}")
        print(f"  Language: {language}")
        print(f"  Speakers: {num_speakers or 'auto-detect'}")
        print(f"  Keywords: {extract_keywords}")
        if extract_keywords:
            print(f"  Keyword method: {keyword_method}")
            print(f"  Top keywords: {top_keywords}")
        print(f"  Output formats: {', '.join(save_formats)}")
        print("─" * 70)

        if not self.get_yes_no("\nProceed with processing?", True):
            print("❌ Processing cancelled.")
            input("\nPress Enter to continue...")
            return

        # Initialize pipeline if needed
        if not self.pipeline:
            from .pipeline import VideoPipeline
            hf_token = self.config.get('hf_token') or os.getenv('HF_TOKEN')
            if not hf_token:
                print("\n❌ Error: HuggingFace token not configured!")
                print("Please set HF_TOKEN environment variable or configure in settings.")
                input("\nPress Enter to continue...")
                return

            print("\n⏳ Initializing pipeline...")
            try:
                self.pipeline = VideoPipeline(
                    language=language,
                    model_variant=self.config.get('model_variant', 'default'),
                    hf_token=hf_token,
                    device=self.config.get('device', 'auto'),
                    output_dir=self.config.get('output', {}).get('directory', './output')
                )
            except Exception as e:
                print(f"\n❌ Error initializing pipeline: {e}")
                input("\nPress Enter to continue...")
                return

        # Process audio
        print("\n🚀 Starting audio processing...")
        print("This may take a while depending on file size and hardware.\n")

        try:
            results = self.pipeline.process_audio(
                audio_path=audio_path,
                num_speakers=num_speakers,
                extract_keywords=extract_keywords,
                keyword_method=keyword_method,
                top_keywords=top_keywords,
                save_formats=save_formats
            )

            # Show results
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

            # Add to history
            self.history.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'audio',
                'file': audio_path,
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

            # Add to history
            self.history.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'audio',
                'file': audio_path,
                'language': language,
                'status': 'failed',
                'error': str(e)
            })

        input("\nPress Enter to continue...")

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
        video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.webm']
        audio_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a']

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

        formats_input = self.get_input("Output formats (comma-separated)", "json,txt")
        save_formats = [f.strip() for f in formats_input.split(',')]

        # Process files
        print(f"\n🚀 Starting batch processing of {len(all_files)} files...")

        successful = 0
        failed = 0

        for idx, file_path in enumerate(all_files, 1):
            print(f"\n[{idx}/{len(all_files)}] Processing: {file_path.name}")

            try:
                # Determine if video or audio
                is_video = file_path.suffix.lower() in video_extensions

                # Initialize pipeline if needed
                if not self.pipeline:
                    from .pipeline import VideoPipeline
                    hf_token = self.config.get('hf_token') or os.getenv('HF_TOKEN')
                    if not hf_token:
                        print("❌ Error: HuggingFace token not configured!")
                        failed += 1
                        continue

                    self.pipeline = VideoPipeline(
                        language=language,
                        model_variant=self.config.get('model_variant', 'default'),
                        hf_token=hf_token,
                        device=self.config.get('device', 'auto'),
                        output_dir=self.config.get('output', {}).get('directory', './output')
                    )

                # Process file
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

                # Add to history
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
        print("  • Output formats: JSON (detailed), TXT (readable), CSV (tabular)")

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
        while self.running:
            self.clear_screen()
            self.print_header()
            self.print_menu()

            choice = self.get_input("\nSelect an option (1-8)", "1")

            if choice == "1":
                self.process_single_video()
            elif choice == "2":
                self.process_single_audio()
            elif choice == "3":
                self.batch_process()
            elif choice == "4":
                self.view_history()
            elif choice == "5":
                self.configure_settings()
            elif choice == "6":
                self.show_configuration()
            elif choice == "7":
                self.show_help()
            elif choice == "8":
                print("\n👋 Thank you for using LLCAR!")
                print("Goodbye!\n")
                self.running = False
            else:
                print(f"\n❌ Invalid option: {choice}")
                input("\nPress Enter to continue...")

        return 0
