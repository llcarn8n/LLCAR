# LLCAR Code Review

## Summary

Comprehensive code review of the LLCAR project — a video/audio processing pipeline
with speaker diarization, transcription, and keyword extraction.

Overall the project has a clean modular architecture and is well-structured.
Below are the issues found, grouped by severity.

---

## CRITICAL — Bugs and potential runtime errors

### 1. Mutable default argument in `process_video` / `process_audio`

**Files:** `src/pipeline.py:78`, `src/pipeline.py:239`

```python
save_formats: List[str] = None
```

This is not a bug per se (it's `None`, not `[]`), but the `keyword_method`
parameter in `process_single_video` / `process_single_audio` in `src/console.py`
can be passed as `None` when `extract_keywords=False` (lines 177, 317). The
pipeline then receives `keyword_method=None`, though `None` is never evaluated
because `extract_keywords` is False. This path is safe but fragile — if the
logic changes, it will break.

### 2. Profanity regex is overly broad and will censor normal Russian words

**File:** `src/postprocessing.py:49`

```python
PROFANITY_PATTERN = re.compile(
    r'\b\w*[бпхё][ляуеёаоыэяию]*[тдцксзжшщчх][ьъ]?\w*\b', re.IGNORECASE
)
```

This pattern matches many legitimate Russian words like "быстро", "просто",
"потому", "прост", "пусть", "помощь", "блеск", "плюс", etc. It will
aggressively censor ordinary speech. This should be replaced with a curated
word list or a dedicated library (e.g., `russian-bad-words`).

### 3. `_remove_fillers` breaks multi-word filler phrases

**File:** `src/postprocessing.py:107-111`

```python
def _remove_fillers(self, text: str) -> str:
    words = text.split()
    cleaned_words = [w for w in words if w.lower() not in self.fillers]
    return ' '.join(cleaned_words)
```

Multi-word fillers like `"как бы"`, `"в общем"`, `"то есть"`, `"sort of"`,
`"you know"`, `"i mean"` will **never** be removed because `text.split()`
splits by individual words, so `"как"` and `"бы"` are checked individually
against `"как бы"`, which will never match. This is a functional bug.

### 4. TF-IDF on a single document is meaningless

**File:** `src/postprocessing.py:191-193`

```python
combined_text = ' '.join(texts)
tfidf_matrix = vectorizer.fit_transform([combined_text])
```

TF-IDF is designed to work with multiple documents. When all text is joined into
a single document and `fit_transform` is called with `[combined_text]`,
the IDF component becomes trivial (log(1/1) = 0 for all terms, adjusted only by
smoothing). The result is essentially term frequency, not TF-IDF. To get
meaningful results, each segment should be passed as a separate document.

### 5. `_process_hf_result` loses timestamps when they are `None`

**File:** `src/transcription.py:198-199`

```python
"start": chunk["timestamp"][0] if chunk["timestamp"][0] else 0.0,
"end": chunk["timestamp"][1] if chunk["timestamp"][1] else 0.0,
```

If `chunk["timestamp"]` is `None` (which happens for some HuggingFace models),
this will raise `TypeError: 'NoneType' object is not subscriptable`. Need to
check `chunk["timestamp"]` itself first.

### 6. Whisper model name parsing is fragile

**File:** `src/transcription.py:99-100`

```python
elif self.model_name.startswith("openai/whisper"):
    model_size = self.model_name.split("-")[-1]
```

For `"openai/whisper-large-v3"`, `split("-")[-1]` yields `"v3"`, not
`"large-v3"`. Whisper's `load_model` expects `"large-v3"`, not `"v3"`. This
would fail at runtime.

---

## HIGH — Security and reliability concerns

### 7. Shell injection via `os.system` in `clear_screen`

**File:** `src/console.py:45`

```python
os.system('cls' if os.name == 'nt' else 'clear')
```

While currently safe (hardcoded strings), using `os.system` is generally
discouraged. Should use `subprocess.run(['clear'])` or print ANSI escape
codes (`\033[2J\033[H`) instead.

### 8. HF token can be passed via CLI `--hf-token` argument

**File:** `main.py:178-180`

Tokens passed as CLI arguments are visible in process listings (`ps aux`) and
shell history. The `--hf-token` argument should either be removed (relying only
on env vars / config file) or the documentation should warn about this risk.

### 9. `audio_extraction.py` writes extracted WAV next to source video

**File:** `src/audio_extraction.py:46`

```python
output_path = video_path.with_suffix('.wav')
```

If the source video is on a read-only filesystem (e.g., mounted volume in
Docker), this will fail. The default should write to a temp directory or the
configured output directory.

### 10. No cleanup of extracted temporary audio files

**File:** `src/pipeline.py:112`

After `process_video` completes, the extracted `.wav` file is never deleted.
For large videos this can consume significant disk space. Should use
`tempfile.NamedTemporaryFile` or clean up in a `finally` block.

---

## MEDIUM — Code quality and correctness

### 11. Massive code duplication between `process_video` and `process_audio`

**File:** `src/pipeline.py`

`process_video` (lines 71-230) and `process_audio` (lines 232-378) share ~80%
identical code. They differ only in the first step (audio extraction). This
should be refactored into a shared `_process_pipeline` method.

### 12. Console code duplication between `process_single_video` and `process_single_audio`

**File:** `src/console.py`

`process_single_video` (lines 153-290) and `process_single_audio` (lines
292-428) are nearly identical — ~130 lines of copy-pasted code. Should be
extracted into a shared method.

### 13. Pipeline initialization inside console is repeated 3 times

**File:** `src/console.py:208-229`, `src/console.py:346-367`, `src/console.py:498-512`

The pipeline initialization block (checking HF token, creating VideoPipeline)
is copy-pasted in `process_single_video`, `process_single_audio`, and
`batch_process`. Should be a shared `_ensure_pipeline` method.

### 14. `total_duration` calculation in summary report is incorrect

**File:** `src/output.py:211-212`

```python
if "end" in segments[-1]:
    report["statistics"]["total_duration"] = segments[-1]["end"]
```

This assumes segments are sorted and the last segment's end is the total
duration. If segments are not sorted (which is not guaranteed) or if there are
gaps, this is wrong. It should compute `max(s["end"] for s in segments)`.

### 15. CSV field ordering is non-deterministic

**File:** `src/output.py:88-92`

```python
fieldnames = set()
for segment in segments:
    fieldnames.update(segment.keys())
fieldnames = sorted(list(fieldnames))
```

Using a `set` then `sorted` produces alphabetical order, so "end" comes before
"speaker" and "start" before "text". The output would be more useful with an
explicit field order like `["start", "end", "speaker", "text", "original_text"]`.

### 16. `get_speaker_statistics` could use `defaultdict`

**File:** `src/diarization.py:118-126`

```python
stats = {}
for segment in segments:
    speaker = segment["speaker"]
    duration = segment["end"] - segment["start"]
    if speaker not in stats:
        stats[speaker] = 0.0
    stats[speaker] += duration
```

Using `collections.defaultdict(float)` would simplify this.

### 17. Version is defined in two places

`src/__init__.py` has `__version__ = "1.0.0"` and `setup.py` has
`version="1.0.0"`. These can diverge. `setup.py` should read the version from
`src/__init__.py`.

### 18. `nltk.download` runs at module import time

**File:** `src/postprocessing.py:16-24`

```python
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
```

This runs on **every import** of the postprocessing module, including during
tests. It adds latency and requires network access. This should be done once
during installation (e.g., in `install.sh`, which already does this).

---

## LOW — Minor issues and improvements

### 19. Tests don't use `pytest` or `unittest` properly

**File:** `test_pipeline.py`

Tests are ad-hoc scripts that print output and return boolean. They don't
use `pytest` assertions, making CI integration harder. The `setup.py` lists
`pytest` as a dev dependency, but `Makefile` runs `python3 test_pipeline.py`
instead. `test_console.py` uses `unittest` properly but the other test files
don't.

### 20. `console.py` launcher modifies `sys.argv` globally

**File:** `console.py:18`

```python
sys.argv.append("--interactive")
```

This modifies the global argv, which can cause issues if the module is imported
rather than run directly.

### 21. `gui.py` modifies `sys.path` at module level

**File:** `gui.py:22`

```python
sys.path.insert(0, str(Path(__file__).parent))
```

This is fragile. The project should be properly installed (`pip install -e .`)
so that `src` is importable without path manipulation.

### 22. `docker-compose.yml` uses deprecated `version` field

**File:** `docker-compose.yml:1`

```yaml
version: '3.8'
```

The `version` field is deprecated in modern Docker Compose. It can be removed.

### 23. GitHub Actions uses deprecated `actions/upload-release-asset@v1`

**File:** `.github/workflows/build-release.yml:54,65`

This action is deprecated and archived. Should migrate to
`softprops/action-gh-release` or use `gh release upload` in a script step.

### 24. No `.gitignore` for common Python artifacts

The project should have a `.gitignore` that excludes `__pycache__/`, `*.pyc`,
`.env`, `venv/`, `dist/`, `build/`, `*.egg-info/`, `output/`, etc.

### 25. `requirements.txt` has `whisperx>=3.1.1` but code warns it's not available

**File:** `src/transcription.py:92-95`

The WhisperX model variant logs a warning saying "WhisperX requires separate
installation" and falls back to standard Whisper. But `whisperx` is listed in
`requirements.txt`. Either integrate WhisperX properly or remove it from
requirements and keep it only in `setup.py` extras.

---

## Architecture suggestions

1. **Add a `ProcessingConfig` dataclass** to replace the many keyword arguments
   being passed through the pipeline, console, and GUI. This would reduce
   parameter duplication and make the API cleaner.

2. **Add progress callbacks** to the pipeline so the GUI and console can show
   real-time step progress instead of relying on log messages.

3. **Add input validation** for language codes and model variants at the
   pipeline level, not just in the transcriber.

4. **Consider using `tempfile`** for intermediate audio files to avoid polluting
   the source directory and to ensure cleanup.

5. **Add a `py.typed` marker** and type stubs if you plan to distribute this as
   a library.
