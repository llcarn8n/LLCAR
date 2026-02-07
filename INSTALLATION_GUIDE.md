# Руководство по установке LLCAR

**Обновлено:** 2026-02-07

## Проблема: Зависание при установке зависимостей

Если при выполнении `pip install -r requirements.txt` процесс зависает на разрешении зависимостей (dependency resolution), это вызвано конфликтами версий между пакетами Whisper (openai-whisper, faster-whisper, whisperx) и их зависимостями.

### Признаки проблемы:

```
INFO: pip is looking at multiple versions of whisperx to determine which version is compatible with other requirements. This could take a while.
INFO: This is taking longer than usual. You might need to provide the dependency resolver with stricter constraints to reduce runtime.
```

## Решение 1: Поэтапная установка (Рекомендуется)

Установите зависимости в определённом порядке, чтобы избежать конфликтов:

### Шаг 1: Обновите pip и установочные инструменты

```bash
python -m pip install --upgrade pip setuptools wheel
```

### Шаг 2: Установите PyTorch отдельно

**Для Windows с CUDA 12.1:**
```bash
pip install torch==2.5.1+cu121 torchaudio==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121
```

**Для Windows без GPU (CPU only):**
```bash
pip install torch==2.5.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cpu
```

**Для Linux с CUDA 12.1:**
```bash
pip install torch==2.5.1+cu121 torchaudio==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121
```

**Для macOS:**
```bash
pip install torch==2.5.1 torchaudio==2.5.1
```

### Шаг 3: Установите основные зависимости

```bash
pip install numpy==1.26.4 scipy==1.17.0 pandas==2.3.3 pyyaml==6.0.3
```

### Шаг 4: Установите Whisper модели с конкретными версиями

```bash
# Сначала установите openai-whisper
pip install openai-whisper==20231117

# Затем faster-whisper с фиксированной версией
pip install faster-whisper==1.0.0

# WhisperX может вызывать конфликты, поэтому пропустите его на первом этапе
# Вернитесь к нему позже, если необходимо
```

### Шаг 5: Установите остальные зависимости

Создайте временный файл `requirements-minimal.txt`:

```txt
ffmpeg-python>=0.2.0
pydub>=0.25.1
librosa>=0.10.1
soundfile>=0.12.1
pyannote.audio>=3.1.0
speechbrain>=0.5.16
nltk>=3.8.1
spacy>=3.7.2
scikit-learn>=1.3.2
transformers>=4.36.0
python-dotenv>=1.0.0
tqdm>=4.66.1
click>=8.1.7
colorama>=0.4.6
rich>=13.7.0
pandas>=2.1.3
python-docx>=1.1.0
openpyxl>=3.1.2
```

Затем установите:

```bash
pip install -r requirements-minimal.txt
```

### Шаг 6: Установите языковые модели

```bash
# Русская модель для spaCy
python -m spacy download ru_core_news_sm

# NLTK данные
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

## Решение 2: Использование рекомендуемого файла требований

Используйте `requirements-recommended.txt`, который содержит более строгие ограничения версий:

```bash
pip install -r requirements-recommended.txt
```

## Решение 3: Установка без WhisperX (если конфликты продолжаются)

WhisperX часто является источником конфликтов зависимостей. Если он вам не нужен, пропустите его:

### requirements-no-whisperx.txt

```txt
# Базовые зависимости
numpy>=1.26.0
pandas>=2.1.0
pyyaml>=6.0.0

# PyTorch (установите отдельно как в Шаге 2)
# torch>=2.1.0
# torchaudio>=2.1.0

# Whisper без WhisperX
openai-whisper==20231117
faster-whisper==1.0.0
transformers>=4.36.0

# Остальные зависимости
ffmpeg-python>=0.2.0
pydub>=0.25.1
librosa>=0.10.1
soundfile>=0.12.1
pyannote.audio>=3.1.0
nltk>=3.8.1
spacy>=3.7.2
scikit-learn>=1.3.2
python-dotenv>=1.0.0
tqdm>=4.66.1
click>=8.1.7
colorama>=0.4.6
rich>=13.7.0
python-docx>=1.1.0
openpyxl>=3.1.2
```

## Решение 4: Использование виртуального окружения

Всегда используйте виртуальное окружение для избежания конфликтов:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

## Решение 5: Если ничего не помогает - принудительная установка

Если pip застревает на разрешении зависимостей более 10 минут, прервите процесс (Ctrl+C) и попробуйте:

```bash
# Установите с игнорированием зависимостей (осторожно!)
pip install --no-deps openai-whisper==20231117
pip install --no-deps faster-whisper==1.0.0

# Затем установите зависимости вручную
pip install torch torchaudio transformers numpy scipy
pip install ffmpeg-python librosa soundfile
```

## Дополнительные советы

### 1. Очистка кеша pip

```bash
pip cache purge
```

### 2. Использование pip-tools для резолюции

```bash
pip install pip-tools
pip-compile requirements.txt --output-file requirements-locked.txt
pip install -r requirements-locked.txt
```

### 3. Проверка установленных пакетов

После установки проверьте, что все работает:

```python
python -c "import whisper; import pyannote.audio; import torch; print('All imports successful!')"
```

## Известные конфликты версий

| Пакет | Проблемная версия | Рекомендуемая версия | Причина |
|-------|------------------|---------------------|---------|
| ctranslate2 | >= 4.5.0 | 4.0.0 - 4.4.0 | Конфликт с faster-whisper |
| onnxruntime | >= 1.18.0 | 1.14.0 - 1.17.0 | Конфликт с faster-whisper |
| whisperx | >= 3.5.0 | 3.1.1 - 3.4.0 | Множественные конфликты зависимостей |
| numpy | >= 2.0.0 | 1.26.x | Несовместимость с некоторыми ML библиотеками |

## Минимальные требования системы

- **Python**: 3.8 - 3.12 (рекомендуется 3.10 или 3.11)
- **RAM**: Минимум 8 GB (рекомендуется 16 GB)
- **Место на диске**: Минимум 10 GB для всех моделей
- **GPU (опционально)**: NVIDIA GPU с CUDA 12.1 для ускорения

## Проверка установки

После успешной установки запустите:

```bash
python main.py --help
```

Если вы видите справку по командам - установка прошла успешно!

## Получение помощи

Если проблемы сохраняются:

1. Создайте issue на GitHub: https://github.com/llcarn8n/LLCAR/issues
2. Укажите:
   - Версию Python (`python --version`)
   - Операционную систему
   - Полный вывод ошибки
   - Файл requirements.txt, который вы использовали

## Альтернатива: Docker

Если установка слишком сложна, используйте Docker:

```bash
docker build -t llcar .
docker run -it llcar --help
```

Docker автоматически установит все зависимости в изолированной среде.
