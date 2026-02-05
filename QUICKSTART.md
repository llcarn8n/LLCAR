# LLCAR Quick Start Guide

Быстрый старт для LLCAR Video Processing Pipeline

## Установка за 3 шага

### 1. Клонирование репозитория

```bash
git clone https://github.com/llcarn8n/LLCAR.git
cd LLCAR
```

### 2. Автоматическая установка

```bash
chmod +x install.sh
./install.sh
```

Скрипт автоматически:
- Проверит версию Python (требуется 3.8+)
- Создаст виртуальное окружение
- Установит все зависимости
- Скачает необходимые данные NLTK
- Создаст директории
- Запустит тесты

### 3. Настройка токена HuggingFace

Отредактируйте `.env` и добавьте ваш токен:

```bash
# Получите токен на https://huggingface.co/settings/tokens
echo "HF_TOKEN=ваш_токен_здесь" > .env
```

## Быстрый запуск

### Активация окружения

```bash
source venv/bin/activate
```

### Обработка видео

```bash
# Базовый пример
python main.py --video input/video.mp4

# С указанием языка
python main.py --video input/video.mp4 --language ru

# С указанием количества спикеров
python main.py --video input/video.mp4 --language en --num-speakers 2

# Полный пример
python main.py \
  --video input/interview.mp4 \
  --language ru \
  --num-speakers 2 \
  --formats json txt csv \
  --keyword-method tfidf \
  --top-keywords 15
```

## Docker (альтернативный способ)

### Сборка образа

```bash
docker build -t llcar .
```

### Запуск

```bash
# Создайте директории для входных/выходных файлов
mkdir -p input output

# Запуск с docker-compose
docker-compose run llcar --video /app/input/video.mp4 --language en

# Или напрямую с docker
docker run -it \
  -e HF_TOKEN=ваш_токен \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  llcar --video /app/input/video.mp4
```

## Тестирование

Запустите тесты компонентов:

```bash
python test_pipeline.py
```

## Примеры использования

### Английский язык

```bash
python main.py \
  --video input/english_interview.mp4 \
  --language en \
  --model-variant default \
  --formats json txt
```

### Русский язык

```bash
python main.py \
  --video input/russian_podcast.mp4 \
  --language ru \
  --model-variant default \
  --formats json txt csv
```

### Китайский язык

```bash
python main.py \
  --video input/chinese_meeting.mp4 \
  --language zh \
  --formats json txt
```

### Только аудио

```bash
python main.py \
  --audio input/audio.wav \
  --language en
```

## Структура проекта

```
LLCAR/
├── input/          # Поместите сюда входные видео/аудио
├── output/         # Здесь будут результаты
├── models/         # Кэш моделей (создается автоматически)
├── src/            # Исходный код
├── main.py         # Главный скрипт
├── config.yaml     # Конфигурация
└── .env            # Переменные окружения (создайте из .env.example)
```

## Форматы вывода

После обработки в директории `output/` появятся файлы:

- `video_report.json` - Полный отчет с метаданными
- `video_segments.csv` - Таблица сегментов
- `video_transcript.txt` - Читаемый транскрипт

## Решение проблем

### Ошибка "HF_TOKEN required"

Убедитесь, что токен добавлен в `.env`:

```bash
cat .env
# Должно быть: HF_TOKEN=hf_...
```

### Ошибка "FFmpeg not found"

Установите FFmpeg:

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

### Ошибка памяти GPU

Используйте CPU:

```bash
python main.py --video video.mp4 --device cpu
```

## Дополнительная информация

- [README.md](README.md) - Полная документация
- [MODELS.md](MODELS.md) - Сравнение моделей
- [examples.py](examples.py) - Примеры использования из кода

## Поддержка

Если возникли проблемы:

1. Проверьте логи
2. Запустите тесты: `python test_pipeline.py`
3. Откройте Issue на GitHub
