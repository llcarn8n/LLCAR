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

    STEPS = [
        "Audio Extraction",
        "Speaker Diarization",
        "Transcription",
        "Post-processing",
        "Output Generation",
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("LLCAR - Video Processing Pipeline")
        self.root.geometry("960x760")
        self.root.minsize(800, 600)

        # Variables
        self.input_file = tk.StringVar()
        self.output_dir = tk.StringVar(value="./output")
        self.language = tk.StringVar(value="en")
        self.model_variant = tk.StringVar(value="default")
        self.num_speakers = tk.StringVar(value="auto")
        self.hf_token = tk.StringVar()
        self.device = tk.StringVar(value="auto")
        self.extract_keywords = tk.BooleanVar(value=True)
        self.keyword_method = tk.StringVar(value="tfidf")
        self.format_json = tk.BooleanVar(value=True)
        self.format_txt = tk.BooleanVar(value=True)
        self.format_csv = tk.BooleanVar(value=False)
        self.format_plain = tk.BooleanVar(value=False)

        # Processing state
        self.is_processing = False
        self.pipeline = None
        self.log_queue = queue.Queue()
        self.current_step = 0

        # Load config and token
        self.load_config()

        # Create UI
        self.create_widgets()

        # Start log updater
        self.update_log()

        # Drag-and-drop support (works on Windows with tkinterdnd2 or via manual bind)
        self._setup_drop_target()

    def load_config(self):
        """Load configuration from config.yaml"""
        try:
            config_path = Path("config.yaml")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)

                self.language.set(config.get('language', 'en'))
                self.model_variant.set(config.get('model_variant', 'default'))
                self.device.set(config.get('device', 'auto'))

                output_config = config.get('output', {})
                self.output_dir.set(output_config.get('directory', './output'))

                keywords_cfg = config.get('keywords', {})
                self.extract_keywords.set(keywords_cfg.get('enabled', True))
                self.keyword_method.set(keywords_cfg.get('method', 'tfidf'))

                token = os.getenv('HF_TOKEN') or config.get('hf_token', '')
                if token:
                    self.hf_token.set(token)

        except Exception as e:
            self.log(f"Warning: Could not load config: {e}")

    def _setup_drop_target(self):
        """Setup drag-and-drop. Uses tkinterdnd2 if available, otherwise no-op."""
        try:
            from tkinterdnd2 import DND_FILES
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self._on_drop)
        except ImportError:
            pass  # tkinterdnd2 not available, skip drag-and-drop

    def _on_drop(self, event):
        """Handle drag-and-drop file."""
        path = event.data.strip('{}')
        if path:
            self.input_file.set(path)
            self.log(f"File dropped: {path}")

    def create_widgets(self):
        """Create all UI widgets"""

        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)  # Log area grows

        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 5))
        ttk.Label(title_frame, text="LLCAR",
                  font=('Arial', 18, 'bold')).pack(side=tk.LEFT)
        ttk.Label(title_frame, text="  Video Processing Pipeline",
                  font=('Arial', 12)).pack(side=tk.LEFT, pady=(4, 0))

        # ── File Selection ───────────────────────────────────────────
        file_frame = ttk.LabelFrame(main_frame, text="Input / Output", padding="8")
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=4)
        file_frame.columnconfigure(1, weight=1)

        ttk.Label(file_frame, text="File:").grid(row=0, column=0, sticky=tk.W)
        input_entry = ttk.Entry(file_frame, textvariable=self.input_file, width=60)
        input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_input).grid(
            row=0, column=2)

        ttk.Label(file_frame, text="Output:").grid(row=1, column=0, sticky=tk.W, pady=(4, 0))
        ttk.Entry(file_frame, textvariable=self.output_dir, width=60).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=(4, 0))
        ttk.Button(file_frame, text="Browse...", command=self.browse_output).grid(
            row=1, column=2, pady=(4, 0))

        # ── Settings ─────────────────────────────────────────────────
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="8")
        settings_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=4)
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(3, weight=1)
        settings_frame.columnconfigure(5, weight=1)

        # Row 1
        ttk.Label(settings_frame, text="Language:").grid(row=0, column=0, sticky=tk.W)
        lang_combo = ttk.Combobox(settings_frame, textvariable=self.language,
                                  values=['en', 'ru', 'zh'], state='readonly', width=8)
        lang_combo.grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(settings_frame, text="Model:").grid(row=0, column=2, sticky=tk.W, padx=(8, 0))
        model_combo = ttk.Combobox(settings_frame, textvariable=self.model_variant,
                                   values=['default', 'alternative', 'turbo', 'whisperx'],
                                   state='readonly', width=12)
        model_combo.grid(row=0, column=3, sticky=tk.W, padx=5)

        ttk.Label(settings_frame, text="Device:").grid(row=0, column=4, sticky=tk.W, padx=(8, 0))
        device_combo = ttk.Combobox(settings_frame, textvariable=self.device,
                                    values=['auto', 'cuda', 'cpu'], state='readonly', width=8)
        device_combo.grid(row=0, column=5, sticky=tk.W, padx=5)

        # Row 2
        ttk.Label(settings_frame, text="Speakers:").grid(row=1, column=0, sticky=tk.W, pady=(4, 0))
        speakers_combo = ttk.Combobox(settings_frame, textvariable=self.num_speakers,
                                      values=['auto', '1', '2', '3', '4', '5'], width=8)
        speakers_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=(4, 0))

        ttk.Checkbutton(settings_frame, text="Keywords",
                        variable=self.extract_keywords).grid(
            row=1, column=2, columnspan=2, sticky=tk.W, padx=(8, 0), pady=(4, 0))

        ttk.Label(settings_frame, text="Method:").grid(row=1, column=4, sticky=tk.W, padx=(8, 0), pady=(4, 0))
        kw_combo = ttk.Combobox(settings_frame, textvariable=self.keyword_method,
                                values=['tfidf', 'textrank'], state='readonly', width=10)
        kw_combo.grid(row=1, column=5, sticky=tk.W, padx=5, pady=(4, 0))

        # Row 3
        ttk.Label(settings_frame, text="HF Token:").grid(row=2, column=0, sticky=tk.W, pady=(4, 0))
        ttk.Entry(settings_frame, textvariable=self.hf_token, show="*", width=50).grid(
            row=2, column=1, columnspan=5, sticky=(tk.W, tk.E), padx=5, pady=(4, 0))

        # ── Output Formats ───────────────────────────────────────────
        formats_frame = ttk.LabelFrame(main_frame, text="Output Formats", padding="8")
        formats_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=4)

        ttk.Checkbutton(formats_frame, text="JSON (full report)", variable=self.format_json).grid(
            row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(formats_frame, text="TXT (readable transcript)", variable=self.format_txt).grid(
            row=0, column=1, sticky=tk.W, padx=20)
        ttk.Checkbutton(formats_frame, text="CSV (table)", variable=self.format_csv).grid(
            row=0, column=2, sticky=tk.W)
        ttk.Checkbutton(formats_frame, text="Plain (text only)", variable=self.format_plain).grid(
            row=0, column=3, sticky=tk.W, padx=20)

        # ── Control Buttons ──────────────────────────────────────────
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=4, column=0, columnspan=2, pady=8)

        self.process_btn = ttk.Button(controls_frame, text="  Process File  ",
                                      command=self.start_processing)
        self.process_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = ttk.Button(controls_frame, text=" Stop ",
                                   command=self.stop_processing, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=5)

        ttk.Button(controls_frame, text=" Clear Log ",
                   command=self.clear_log).grid(row=0, column=2, padx=5)

        # ── Pipeline Step Indicators ─────────────────────────────────
        steps_frame = ttk.Frame(main_frame)
        steps_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 4))

        self.step_labels = []
        for i, step_name in enumerate(self.STEPS):
            lbl = ttk.Label(steps_frame, text=f"  {i+1}. {step_name}  ",
                            foreground="gray")
            lbl.grid(row=0, column=i, padx=2)
            self.step_labels.append(lbl)

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate', maximum=len(self.STEPS))
        self.progress.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 4))

        # ── Log / Results Notebook ───────────────────────────────────
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=4)

        # Log tab
        log_tab = ttk.Frame(notebook)
        notebook.add(log_tab, text="  Log  ")
        log_tab.columnconfigure(0, weight=1)
        log_tab.rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_tab, height=12, wrap=tk.WORD,
                                                  font=('Consolas', 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Results tab
        results_tab = ttk.Frame(notebook)
        notebook.add(results_tab, text="  Results  ")
        results_tab.columnconfigure(0, weight=1)
        results_tab.rowconfigure(0, weight=1)

        self.results_text = scrolledtext.ScrolledText(results_tab, height=12, wrap=tk.WORD,
                                                      font=('Consolas', 9))
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # ── Status Bar ───────────────────────────────────────────────
        self.status_var = tk.StringVar(value="Ready. Select a video or audio file to begin.")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var,
                               relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(4, 0))

    def browse_input(self):
        """Browse for input video/audio file"""
        filetypes = [
            ("Video files", "*.mp4 *.m4v *.avi *.mov *.mkv *.wmv *.flv *.webm *.mpg *.mpeg"),
            ("Audio files", "*.wav *.mp3 *.flac *.ogg *.m4a *.wma *.aac *.opus"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Select Video or Audio File",
                                              filetypes=filetypes)
        if filename:
            self.input_file.set(filename)
            self.log(f"Selected: {filename}")

    def browse_output(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)

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

                # Detect pipeline step progress from log messages
                msg_lower = message.lower()
                if "extracting audio" in msg_lower:
                    self._highlight_step(0)
                elif "diarization" in msg_lower and "performing" in msg_lower:
                    self._highlight_step(1)
                elif "transcribing" in msg_lower:
                    self._highlight_step(2)
                elif "post-processing" in msg_lower:
                    self._highlight_step(3)
                elif "generating output" in msg_lower:
                    self._highlight_step(4)
        except queue.Empty:
            pass

        self.root.after(100, self.update_log)

    def _highlight_step(self, step_index: int):
        """Highlight a pipeline step as active."""
        for i, lbl in enumerate(self.step_labels):
            if i < step_index:
                lbl.configure(foreground="green")
            elif i == step_index:
                lbl.configure(foreground="blue", font=('TkDefaultFont', 9, 'bold'))
            else:
                lbl.configure(foreground="gray", font=('TkDefaultFont', 9))
        self.progress['value'] = step_index + 1

    def _reset_steps(self):
        """Reset step indicators."""
        for lbl in self.step_labels:
            lbl.configure(foreground="gray", font=('TkDefaultFont', 9))
        self.progress['value'] = 0

    def clear_log(self):
        """Clear log text"""
        self.log_text.delete(1.0, tk.END)

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
                "HuggingFace token is not set.\n"
                "Speaker diarization requires a token.\n\n"
                "Continue anyway? (Processing may fail)"
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

        self.is_processing = True
        self.process_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self._reset_steps()
        self.status_var.set("Processing...")
        self.results_text.delete(1.0, tk.END)

        thread = threading.Thread(target=self.process_file, daemon=True)
        thread.start()

    def stop_processing(self):
        """Stop processing"""
        self.is_processing = False
        self.log("Stop requested (processing may continue until current step finishes)...")

    def process_file(self):
        """Process the video/audio file"""
        try:
            self.log("=" * 60)
            self.log("Starting LLCAR Processing Pipeline")
            self.log("=" * 60)

            # Get parameters
            input_path = self.input_file.get()
            output_dir = self.output_dir.get()
            language = self.language.get()
            model_var = self.model_variant.get()
            device = self.device.get()
            hf_token = self.hf_token.get()

            num_speakers_str = self.num_speakers.get()
            num_speakers = None if num_speakers_str == "auto" else int(num_speakers_str)

            formats = []
            if self.format_json.get():
                formats.append('json')
            if self.format_txt.get():
                formats.append('txt')
            if self.format_csv.get():
                formats.append('csv')
            if self.format_plain.get():
                formats.append('plain')
            if not formats:
                formats = ['json', 'txt']

            kw_method = self.keyword_method.get()

            self.log(f"Input:    {input_path}")
            self.log(f"Output:   {output_dir}")
            self.log(f"Language: {language}  Model: {model_var}  Device: {device}")
            self.log(f"Speakers: {num_speakers_str}  Formats: {', '.join(formats)}")
            self.log("")

            # Initialize pipeline
            self.log("Initializing pipeline...")
            self.pipeline = VideoPipeline(
                language=language,
                model_variant=model_var,
                hf_token=hf_token,
                device=device,
                output_dir=output_dir
            )

            # Determine if input is video or audio
            input_ext = Path(input_path).suffix.lower()
            audio_exts = ['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.wma', '.aac', '.opus']
            is_audio = input_ext in audio_exts

            if is_audio:
                self.log("Processing audio file...")
                results = self.pipeline.process_audio(
                    audio_path=input_path,
                    num_speakers=num_speakers,
                    extract_keywords=self.extract_keywords.get(),
                    keyword_method=kw_method,
                    save_formats=formats
                )
            else:
                self.log("Processing video file...")
                results = self.pipeline.process_video(
                    video_path=input_path,
                    num_speakers=num_speakers,
                    extract_keywords=self.extract_keywords.get(),
                    keyword_method=kw_method,
                    save_formats=formats
                )

            if not self.is_processing:
                self.log("Processing was stopped by user")
                return

            # Mark all steps complete
            for i in range(len(self.STEPS)):
                self.root.after(0, lambda idx=i: self.step_labels[idx].configure(
                    foreground="green", font=('TkDefaultFont', 9)))
            self.root.after(0, lambda: self.progress.configure(value=len(self.STEPS)))

            # Log results
            self.log("")
            self.log("=" * 60)
            self.log("PROCESSING COMPLETED SUCCESSFULLY!")
            self.log("=" * 60)
            self.log(f"Total time: {results.get('total_processing_time', 0):.2f} seconds")

            stats = results.get('steps', {})
            if 'transcription' in stats:
                self.log(f"Segments: {stats['transcription'].get('num_segments', 0)}")
            if 'diarization' in stats:
                self.log(f"Speakers: {stats['diarization'].get('num_speakers', 0)}")

            if self.extract_keywords.get():
                keywords = results.get('keywords', [])
                self.log(f"Keywords: {len(keywords)}")

            self.log("")
            self.log("Output files:")
            for fmt, fpath in results.get('output_files', {}).items():
                self.log(f"  {fmt.upper()}: {fpath}")

            # Populate results tab with transcript preview
            self._show_results_preview(results)

            self.root.after(0, lambda: messagebox.showinfo(
                "Success",
                f"Processing completed!\n\n"
                f"Time: {results.get('total_processing_time', 0):.1f}s\n"
                f"Output: {output_dir}"
            ))

        except Exception as e:
            self.log("")
            self.log("=" * 60)
            self.log(f"PROCESSING FAILED: {e}")
            self.log("=" * 60)

            self.root.after(0, lambda: messagebox.showerror(
                "Error", f"Processing failed:\n\n{e}"
            ))

        finally:
            self.is_processing = False
            self.root.after(0, lambda: self.process_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.status_var.set("Ready"))

    def _show_results_preview(self, results):
        """Show transcript preview in the Results tab."""
        def _update():
            self.results_text.delete(1.0, tk.END)

            segments = results.get('segments', [])
            if not segments:
                self.results_text.insert(tk.END, "(No segments found)")
                return

            self.results_text.insert(tk.END, f"=== Transcript ({len(segments)} segments) ===\n\n")

            for seg in segments:
                speaker = seg.get('speaker', '?')
                start = seg.get('start', 0)
                end = seg.get('end', 0)
                text = seg.get('text', '')

                h1, m1, s1 = int(start // 3600), int((start % 3600) // 60), int(start % 60)
                h2, m2, s2 = int(end // 3600), int((end % 3600) // 60), int(end % 60)

                self.results_text.insert(
                    tk.END,
                    f"[{h1:02d}:{m1:02d}:{s1:02d} - {h2:02d}:{m2:02d}:{s2:02d}] "
                    f"{speaker}: {text}\n\n"
                )

            # Keywords
            keywords = results.get('keywords', [])
            if keywords:
                self.results_text.insert(tk.END, "\n=== Keywords ===\n\n")
                for kw in keywords:
                    score = kw.get('score')
                    score_str = f" ({score:.3f})" if score is not None else ""
                    self.results_text.insert(tk.END, f"  - {kw['keyword']}{score_str}\n")

            self.results_text.see("1.0")

        self.root.after(0, _update)


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
