#!/usr/bin/env python3
"""
LLCAR GUI Application
Graphical User Interface for LLCAR Video Processing Pipeline
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import os
import sys
from pathlib import Path
from typing import Optional
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import VideoPipeline


class LLCARGui:
    """GUI Application for LLCAR Video Processing Pipeline"""

    def __init__(self, root):
        self.root = root
        self.root.title("LLCAR - Video Processing Pipeline")
        self.root.geometry("900x700")

        # Variables
        self.input_file = tk.StringVar()
        self.output_dir = tk.StringVar(value="./output")
        self.language = tk.StringVar(value="en")
        self.num_speakers = tk.StringVar(value="auto")
        self.hf_token = tk.StringVar()
        self.device = tk.StringVar(value="auto")
        self.extract_keywords = tk.BooleanVar(value=True)
        self.format_json = tk.BooleanVar(value=True)
        self.format_txt = tk.BooleanVar(value=True)
        self.format_csv = tk.BooleanVar(value=False)

        # Processing state
        self.is_processing = False
        self.pipeline = None
        self.log_queue = queue.Queue()

        # Load config and token
        self.load_config()

        # Create UI
        self.create_widgets()

        # Start log updater
        self.update_log()

    def load_config(self):
        """Load configuration from config.yaml"""
        try:
            config_path = Path("config.yaml")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)

                # Load default values from config
                self.language.set(config.get('language', 'en'))
                self.device.set(config.get('device', 'auto'))

                output_config = config.get('output', {})
                self.output_dir.set(output_config.get('directory', './output'))

                # Load HF token from env or config
                token = os.getenv('HF_TOKEN') or config.get('hf_token', '')
                if token:
                    self.hf_token.set(token)

        except Exception as e:
            self.log(f"Warning: Could not load config: {e}")

    def create_widgets(self):
        """Create all UI widgets"""

        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)  # Log area

        # Title
        title_label = ttk.Label(main_frame, text="LLCAR Video Processing Pipeline",
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # File Selection Frame
        file_frame = ttk.LabelFrame(main_frame, text="Input File", padding="10")
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(1, weight=1)

        ttk.Label(file_frame, text="Video/Audio:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(file_frame, textvariable=self.input_file, width=50).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_input).grid(
            row=0, column=2)

        ttk.Label(file_frame, text="Output Dir:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        ttk.Entry(file_frame, textvariable=self.output_dir, width=50).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=(5, 0))
        ttk.Button(file_frame, text="Browse...", command=self.browse_output).grid(
            row=1, column=2, pady=(5, 0))

        # Settings Frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(3, weight=1)

        # Row 1: Language and Device
        ttk.Label(settings_frame, text="Language:").grid(row=0, column=0, sticky=tk.W)
        language_combo = ttk.Combobox(settings_frame, textvariable=self.language,
                                     values=['en', 'ru', 'zh'], state='readonly', width=15)
        language_combo.grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(settings_frame, text="Device:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        device_combo = ttk.Combobox(settings_frame, textvariable=self.device,
                                    values=['auto', 'cuda', 'cpu'], state='readonly', width=15)
        device_combo.grid(row=0, column=3, sticky=tk.W, padx=5)

        # Row 2: Speakers and Keywords
        ttk.Label(settings_frame, text="Speakers:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        speakers_combo = ttk.Combobox(settings_frame, textvariable=self.num_speakers,
                                     values=['auto', '1', '2', '3', '4', '5'], width=15)
        speakers_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=(5, 0))

        ttk.Checkbutton(settings_frame, text="Extract Keywords",
                       variable=self.extract_keywords).grid(
                           row=1, column=2, columnspan=2, sticky=tk.W, padx=(10, 0), pady=(5, 0))

        # Row 3: HF Token
        ttk.Label(settings_frame, text="HF Token:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        ttk.Entry(settings_frame, textvariable=self.hf_token, show="*", width=40).grid(
            row=2, column=1, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=(5, 0))

        # Output Formats Frame
        formats_frame = ttk.LabelFrame(main_frame, text="Output Formats", padding="10")
        formats_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Checkbutton(formats_frame, text="JSON", variable=self.format_json).grid(
            row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(formats_frame, text="TXT", variable=self.format_txt).grid(
            row=0, column=1, sticky=tk.W, padx=20)
        ttk.Checkbutton(formats_frame, text="CSV", variable=self.format_csv).grid(
            row=0, column=2, sticky=tk.W)

        # Control Buttons Frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=4, column=0, columnspan=2, pady=10)

        self.process_btn = ttk.Button(controls_frame, text="🎬 Process File",
                                      command=self.start_processing, width=20)
        self.process_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = ttk.Button(controls_frame, text="⏹ Stop",
                                   command=self.stop_processing, state=tk.DISABLED, width=15)
        self.stop_btn.grid(row=0, column=1, padx=5)

        ttk.Button(controls_frame, text="🗑️ Clear Log",
                  command=self.clear_log, width=15).grid(row=0, column=2, padx=5)

        # Progress and Log Frame
        log_frame = ttk.LabelFrame(main_frame, text="Processing Log", padding="5")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(1, weight=1)

        # Progress bar
        self.progress = ttk.Progressbar(log_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var,
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))

    def browse_input(self):
        """Browse for input video/audio file"""
        filetypes = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm"),
            ("Audio files", "*.wav *.mp3 *.flac *.ogg *.m4a"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Select Video or Audio File",
                                             filetypes=filetypes)
        if filename:
            self.input_file.set(filename)
            self.log(f"Selected input file: {filename}")

    def browse_output(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)
            self.log(f"Output directory: {directory}")

    def log(self, message: str):
        """Add message to log queue"""
        self.log_queue.put(message)

    def update_log(self):
        """Update log text from queue"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, f"{message}\n")
                self.log_text.see(tk.END)
        except queue.Empty:
            pass

        # Schedule next update
        self.root.after(100, self.update_log)

    def clear_log(self):
        """Clear log text"""
        self.log_text.delete(1.0, tk.END)
        self.log("Log cleared.")

    def validate_inputs(self) -> bool:
        """Validate user inputs before processing"""
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input file!")
            return False

        if not Path(self.input_file.get()).exists():
            messagebox.showerror("Error", "Input file does not exist!")
            return False

        if not self.hf_token.get():
            result = messagebox.askyesno(
                "Warning",
                "HuggingFace token is not set. This is required for speaker diarization.\n\n"
                "Do you want to continue anyway? (Processing may fail)"
            )
            if not result:
                return False

        return True

    def start_processing(self):
        """Start processing in a separate thread"""
        if self.is_processing:
            messagebox.showwarning("Warning", "Processing is already in progress!")
            return

        if not self.validate_inputs():
            return

        # Start processing thread
        self.is_processing = True
        self.process_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress.start()
        self.status_var.set("Processing...")

        thread = threading.Thread(target=self.process_file, daemon=True)
        thread.start()

    def stop_processing(self):
        """Stop processing"""
        self.is_processing = False
        self.log("⚠️ Stop requested (processing may continue until current step finishes)...")

    def process_file(self):
        """Process the video/audio file"""
        try:
            self.log("=" * 70)
            self.log("🚀 Starting LLCAR Processing Pipeline")
            self.log("=" * 70)

            # Get parameters
            input_path = self.input_file.get()
            output_dir = self.output_dir.get()
            language = self.language.get()
            device = self.device.get()
            hf_token = self.hf_token.get()

            # Parse num_speakers
            num_speakers_str = self.num_speakers.get()
            num_speakers = None if num_speakers_str == "auto" else int(num_speakers_str)

            # Get output formats
            formats = []
            if self.format_json.get():
                formats.append('json')
            if self.format_txt.get():
                formats.append('txt')
            if self.format_csv.get():
                formats.append('csv')

            if not formats:
                formats = ['json', 'txt']  # Default

            # Log parameters
            self.log(f"📁 Input: {input_path}")
            self.log(f"📂 Output: {output_dir}")
            self.log(f"🌍 Language: {language}")
            self.log(f"💻 Device: {device}")
            self.log(f"👥 Speakers: {num_speakers_str}")
            self.log(f"📝 Formats: {', '.join(formats)}")
            self.log("")

            # Initialize pipeline
            self.log("⚙️ Initializing pipeline...")
            self.pipeline = VideoPipeline(
                language=language,
                hf_token=hf_token,
                device=device,
                output_dir=output_dir
            )

            # Determine if input is video or audio
            input_ext = Path(input_path).suffix.lower()
            audio_exts = ['.wav', '.mp3', '.flac', '.ogg', '.m4a']
            is_audio = input_ext in audio_exts

            # Process
            if is_audio:
                self.log("🎵 Processing audio file...")
                results = self.pipeline.process_audio(
                    audio_path=input_path,
                    num_speakers=num_speakers,
                    extract_keywords=self.extract_keywords.get(),
                    save_formats=formats
                )
            else:
                self.log("🎬 Processing video file...")
                results = self.pipeline.process_video(
                    video_path=input_path,
                    num_speakers=num_speakers,
                    extract_keywords=self.extract_keywords.get(),
                    save_formats=formats
                )

            if not self.is_processing:
                self.log("⚠️ Processing was stopped by user")
                return

            # Display results
            self.log("")
            self.log("=" * 70)
            self.log("✅ PROCESSING COMPLETED SUCCESSFULLY!")
            self.log("=" * 70)
            self.log(f"⏱️ Total time: {results.get('total_processing_time', 0):.2f} seconds")

            stats = results.get('steps', {})
            if 'transcription' in stats:
                self.log(f"📊 Segments: {stats['transcription'].get('num_segments', 0)}")
            if 'diarization' in stats:
                self.log(f"👥 Speakers: {stats['diarization'].get('num_speakers', 0)}")

            if self.extract_keywords.get():
                keywords = results.get('keywords', [])
                self.log(f"🔑 Keywords: {len(keywords)}")

            self.log("")
            self.log("📁 Output files:")
            for format_type, file_path in results.get('output_files', {}).items():
                self.log(f"  • {format_type.upper()}: {file_path}")

            self.log("=" * 70)

            # Show completion message
            self.root.after(0, lambda: messagebox.showinfo(
                "Success",
                f"Processing completed successfully!\n\n"
                f"Output files saved to:\n{output_dir}"
            ))

        except Exception as e:
            self.log("")
            self.log("=" * 70)
            self.log("❌ PROCESSING FAILED")
            self.log("=" * 70)
            self.log(f"Error: {str(e)}")
            self.log("=" * 70)

            # Show error message
            self.root.after(0, lambda: messagebox.showerror(
                "Error",
                f"Processing failed:\n\n{str(e)}"
            ))

        finally:
            # Reset UI state
            self.is_processing = False
            self.root.after(0, lambda: self.process_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.status_var.set("Ready"))


def main():
    """Main entry point for GUI application"""
    root = tk.Tk()
    app = LLCARGui(root)

    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()


if __name__ == "__main__":
    main()
