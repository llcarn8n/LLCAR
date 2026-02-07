# Быстрое решение проблемы с установкой LLCAR

**Обновлено:** 2026-02-07

## Проблема
При выполнении `pip install -r requirements.txt` процесс зависает на сообщении:
```
INFO: pip is looking at multiple versions of whisperx...
INFO: This is taking longer than usual...
```

## Решение за 5 минут

### Шаг 1: Остановите процесс
Нажмите `Ctrl+C` для остановки зависшего pip

### Шаг 2: Обновите pip
```bash
python -m pip install --upgrade pip setuptools wheel
```

### Шаг 3: Установите PyTorch отдельно

**Windows с GPU (CUDA 12.1):**
```bash
pip install torch==2.5.1+cu121 torchaudio==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121
```

**Windows без GPU (CPU only):**
```bash
pip install torch==2.5.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cpu
```

### Шаг 4: Установите Whisper модели
```bash
pip install openai-whisper==20231117
pip install faster-whisper==1.0.0
```

### Шаг 5: Установите остальные зависимости
```bash
pip install pyannote.audio nltk spacy scikit-learn
pip install ffmpeg-python librosa soundfile
pip install transformers python-dotenv tqdm click colorama rich
pip install pandas python-docx openpyxl
```

### Шаг 6: Установите языковые модели
```bash
python -m spacy download ru_core_news_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Шаг 7: Проверьте установку
```bash
python -c "import whisper; import pyannote.audio; import torch; print('Успешно!')"
python main.py --help
```

## Альтернатива: Используйте готовый файл

Вместо `requirements.txt` используйте `requirements-recommended.txt`:

```bash
pip install -r requirements-recommended.txt
```

Этот файл содержит оптимизированные версии пакетов, которые не вызывают конфликтов.

## Что делать, если не помогло?

1. **Очистите кеш pip:**
   ```bash
   pip cache purge
   ```

2. **Пересоздайте виртуальное окружение:**
   ```bash
   # Windows
   python -m venv venv_new
   venv_new\Scripts\activate

   # Linux/macOS
   python -m venv venv_new
   source venv_new/bin/activate
   ```

3. **Используйте Docker (самый простой способ):**
   ```bash
   docker build -t llcar .
   docker run -it llcar --help
   ```

## Полная документация

- 📖 **Подробное руководство:** [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
- 🔧 **Устранение проблем:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- 🚀 **Быстрый старт:** [QUICKSTART.md](QUICKSTART.md)

## Почему это происходит?

Проблема вызвана конфликтами версий между:
- `whisperx` (требует ctranslate2 < 4.5)
- `faster-whisper` (требует onnxruntime < 1.18)
- `openai-whisper` (требует определенные версии torch)

Pip пытается найти совместимые версии всех пакетов, что может занять очень много времени или вообще зависнуть.

## Минимальные версии для работы

Для базовой работы LLCAR достаточно:
```bash
pip install torch torchaudio
pip install openai-whisper
pip install pyannote.audio
pip install ffmpeg-python librosa
pip install nltk spacy
pip install python-dotenv tqdm click
```

WhisperX и faster-whisper можно установить позже при необходимости.

## Помощь

Если проблема не решена:
- GitHub Issues: https://github.com/llcarn8n/LLCAR/issues
- Укажите версию Python (`python --version`)
- Приложите полный вывод ошибки
