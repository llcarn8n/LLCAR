# LLCAR - Часто задаваемые вопросы (FAQ)

## Вопросы о файлах и директориях

### Куда по умолчанию сохраняются файлы транскрипции?

**Ответ:** Файлы транскрипции сохраняются в директорию **`./output`** (относительно текущей рабочей директории).

#### Детали:

1. **Расположение по умолчанию:** `./output/`
   - Эта директория создается автоматически при первом запуске, если её не существует
   - Путь относительный к директории, из которой вы запускаете программу

2. **Типы создаваемых файлов:**
   - `transcription_YYYYMMDD_HHMMSS.json` - полный отчет в формате JSON
   - `transcription_YYYYMMDD_HHMMSS.csv` - таблица сегментов в CSV
   - `transcription_YYYYMMDD_HHMMSS.txt` - читаемый текст с метками времени

3. **Пример структуры:**
   ```
   LLCAR/
   ├── main.py
   ├── config.yaml
   └── output/              ← Сюда сохраняются результаты
       ├── transcription_20260206_143025.json
       ├── transcription_20260206_143025.csv
       └── transcription_20260206_143025.txt
   ```

#### Как изменить директорию вывода?

**Способ 1: Через аргумент командной строки**
```bash
python main.py --video video.mp4 --output-dir /path/to/custom/output
```

**Способ 2: Через config.yaml**
```yaml
output:
  directory: "/path/to/custom/output"  # Абсолютный путь
  # или
  directory: "./my_results"            # Относительный путь
  formats:
    - "json"
    - "txt"
    - "csv"
```

**Способ 3: Программно (из Python кода)**
```python
from src.pipeline import VideoPipeline

pipeline = VideoPipeline(
    language="ru",
    output_dir="/path/to/custom/output"
)
```

#### Примеры использования:

```bash
# По умолчанию - сохранит в ./output/
python main.py --video video.mp4

# Пользовательская директория
python main.py --video video.mp4 --output-dir /home/user/transcriptions

# Относительная директория
python main.py --video video.mp4 --output-dir ./results/today
```

#### Что делать, если директория не существует?

Программа **автоматически создаст** директорию вывода, если она не существует. Никаких дополнительных действий не требуется.

---

## Вопросы об установке

### Как установить LLCAR?

См. подробное руководство: [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)

**Быстрый способ:**
```bash
git clone https://github.com/llcarn8n/LLCAR.git
cd LLCAR
./install.sh  # Linux/macOS
```

### Pip зависает при установке зависимостей. Что делать?

См. [QUICK_FIX_INSTALLATION.md](QUICK_FIX_INSTALLATION.md) или [TROUBLESHOOTING.md](TROUBLESHOOTING.md#ошибка-зависание-при-установке-зависимостей-pip-install--r-requirementstxt)

**Быстрое решение:**
```bash
# Прервите процесс (Ctrl+C) и используйте поэтапную установку
pip install torch torchaudio
pip install openai-whisper==20231117 faster-whisper==1.0.0
pip install -r requirements-recommended.txt
```

### Где взять HuggingFace токен?

1. Зарегистрируйтесь на [HuggingFace](https://huggingface.co/)
2. Перейдите в [Settings → Tokens](https://huggingface.co/settings/tokens)
3. Создайте новый токен с правами `read`
4. Добавьте в `.env` файл:
   ```bash
   echo "HF_TOKEN=hf_ваш_токен" > .env
   ```

---

## Вопросы об использовании

### Какие форматы видео поддерживаются?

LLCAR поддерживает все форматы, которые поддерживает FFmpeg:
- MP4, AVI, MOV, MKV, WMV
- WebM, FLV, MPEG
- И многие другие

### Можно ли обработать только аудио файл?

Да! Используйте параметр `--audio`:
```bash
python main.py --audio /path/to/audio.wav --language ru
```

Поддерживаемые аудио форматы: WAV, MP3, FLAC, OGG, M4A и другие.

### Как указать количество спикеров?

```bash
python main.py --video video.mp4 --num-speakers 2
```

Если не указать, программа автоматически определит количество спикеров.

### Как выбрать формат вывода?

**Через командную строку:**
```bash
# Только JSON
python main.py --video video.mp4 --formats json

# JSON и TXT
python main.py --video video.mp4 --formats json txt

# Все форматы
python main.py --video video.mp4 --formats json txt csv
```

**Через config.yaml:**
```yaml
output:
  formats:
    - "json"  # Полный отчет
    - "txt"   # Читаемый текст
    - "csv"   # Таблица для Excel
```

### Как выбрать язык транскрипции?

```bash
# Английский
python main.py --video video.mp4 --language en

# Русский
python main.py --video video.mp4 --language ru

# Китайский
python main.py --video video.mp4 --language zh
```

Поддерживаемые языки: `en` (English), `ru` (Russian), `zh` (Chinese)

### Можно ли использовать интерактивный режим?

Да! Интерактивная консоль - рекомендуемый способ работы:

```bash
python main.py --interactive
# или
python console.py
```

См. подробности в [CONSOLE.md](CONSOLE.md)

---

## Вопросы о производительности

### Нужна ли GPU для работы?

**Нет, но рекомендуется** для более быстрой обработки.

- **С GPU (CUDA):** обработка ~5-10x быстрее реального времени
- **Только CPU:** обработка ~1x реального времени (медленнее)

**Для использования CPU:**
```bash
python main.py --video video.mp4 --device cpu
```

### Сколько времени займет обработка видео?

Зависит от:
- Длительности видео
- Наличия GPU
- Выбранной модели

**Примерная скорость:**
- С GPU: 5-минутное видео → ~1 минута обработки
- Без GPU: 5-минутное видео → ~5-7 минут обработки

### Программа использует слишком много памяти. Что делать?

1. **Используйте CPU вместо GPU:**
   ```bash
   python main.py --video video.mp4 --device cpu
   ```

2. **Обрабатывайте более короткие видео** (разбейте длинное видео на части)

3. **Закройте другие приложения** перед обработкой

---

## Вопросы о форматах вывода

### Что содержится в JSON файле?

JSON файл содержит полный отчет:
- **metadata:** информация о видео, языке, времени обработки
- **statistics:** общая статистика (количество сегментов, длительность, слов)
- **speaker_statistics:** время говорения каждого спикера
- **keywords:** извлеченные ключевые слова
- **segments:** все сегменты транскрипции с метками времени и спикерами

Пример структуры см. в [README.md](README.md#json)

### Что содержится в CSV файле?

CSV файл содержит таблицу всех сегментов:
```csv
speaker,start,end,text,original_text
SPEAKER_00,0.5,3.2,Текст после обработки,Исходный текст
SPEAKER_01,3.5,7.8,Другой текст,Другой текст
```

Удобно для анализа в Excel, Google Sheets или Pandas.

### Что содержится в TXT файле?

TXT файл содержит читаемый текст с временными метками:
```
[00:00:00 - 00:00:03] SPEAKER_00: Текст первого спикера

[00:00:03 - 00:00:07] SPEAKER_01: Текст второго спикера
```

Удобно для чтения и проверки транскрипции.

---

## Вопросы о моделях

### Какая модель используется по умолчанию?

Зависит от языка:
- **Английский (en):** WhisperX на базе openai/whisper-large-v3
- **Русский (ru):** bond005/whisper-podlodka-turbo
- **Китайский (zh):** Whisper large-v3

См. подробное сравнение в [MODELS.md](MODELS.md)

### Как переключить модель?

```bash
# Для русского языка
python main.py --video video.mp4 --language ru --model-variant default      # bond005/whisper-podlodka-turbo
python main.py --video video.mp4 --language ru --model-variant alternative  # antony66/whisper-large-v3-russian
python main.py --video video.mp4 --language ru --model-variant turbo        # dvislobokov/whisper-large-v3-turbo-russian
```

### Где хранятся модели?

Модели автоматически загружаются и кэшируются в директории:
- `./models/` - локальный кэш
- `~/.cache/huggingface/` - глобальный кэш HuggingFace

---

## Вопросы о сборке установщика

### Как собрать Windows установщик?

См. подробное руководство: [BUILD.md](BUILD.md)

**Быстрый способ:**
```bash
pip install -r requirements-build.txt
python build_exe.py
```

Затем используйте Inno Setup для создания установщика из `installer.iss`.

### Ошибка "Не удается найти файл LICENSE при build exe"

См. [TROUBLESHOOTING.md](TROUBLESHOOTING.md#ошибка-не-удается-найти-файл-license-при-build-exe) или [LICENSE_BUILD_FIX.md](LICENSE_BUILD_FIX.md)

**Решение:**
- Убедитесь, что запускаете `build_exe.py` из корневой директории проекта
- Проверьте наличие файла LICENSE в корне проекта

---

## Вопросы о конфигурации

### Где находится файл конфигурации?

Файл конфигурации: `config.yaml` в корне проекта.

### Как изменить настройки по умолчанию?

Отредактируйте `config.yaml`:

```yaml
# Язык по умолчанию
language: "ru"

# Директория вывода
output:
  directory: "./my_output"
  formats:
    - "json"
    - "txt"

# Устройство (auto, cuda, cpu)
device: "auto"

# Извлечение ключевых слов
keywords:
  enabled: true
  method: "tfidf"
  top_n: 15
```

### Можно ли использовать несколько конфигураций?

Да! Создайте несколько YAML файлов и выбирайте нужный:

```bash
python main.py --video video.mp4 --config config_ru.yaml
python main.py --video video.mp4 --config config_en.yaml
```

---

## Получение помощи

### Где найти дополнительную документацию?

- [README.md](README.md) - общая документация
- [QUICKSTART.md](QUICKSTART.md) - быстрый старт
- [CONSOLE.md](CONSOLE.md) - интерактивная консоль
- [MODELS.md](MODELS.md) - сравнение моделей
- [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) - установка
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - решение проблем
- [BUILD.md](BUILD.md) - сборка установщика

### Как сообщить об ошибке?

1. Проверьте [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Поищите существующие issues на [GitHub](https://github.com/llcarn8n/LLCAR/issues)
3. Создайте новый issue с описанием проблемы:
   - Версия Python
   - Операционная система
   - Полный текст ошибки
   - Шаги для воспроизведения

### Где задать вопрос?

- GitHub Issues: https://github.com/llcarn8n/LLCAR/issues
- GitHub Discussions: https://github.com/llcarn8n/LLCAR/discussions
