# LLCAR - Troubleshooting Guide

Решение распространенных проблем при сборке и использовании LLCAR.

## Проблемы при сборке (Build Issues)

### Ошибка: "Не удается найти файл LICENSE при build exe"

**Проблема:** При запуске `python build_exe.py` или `pyinstaller llcar.spec` возникает ошибка о том, что не удается найти файл LICENSE.

**Причины:**
1. Вы запускаете команду не из корневой директории проекта
2. Файл LICENSE отсутствует или был удален
3. Проблемы с правами доступа к файлу

**Решение:**

1. **Убедитесь, что вы находитесь в корневой директории проекта:**
   ```bash
   cd /path/to/LLCAR
   ls LICENSE  # Должен показать файл
   ```

2. **Проверьте наличие всех необходимых файлов:**

   Запустите улучшенный скрипт сборки, который автоматически проверит все файлы:
   ```bash
   python build_exe.py
   ```

   Скрипт проверит наличие:
   - `main.py`
   - `llcar.spec`
   - `config.yaml`
   - `.env.example`
   - `README.md`
   - `LICENSE`

   Если какой-то файл отсутствует, вы увидите сообщение:
   ```
   ✗ LICENSE NOT FOUND
   ERROR: Some required files are missing!
   ```

3. **Если файл LICENSE отсутствует:**

   Создайте файл LICENSE в корневой директории проекта:
   ```bash
   cat > LICENSE << 'EOF'
   MIT License

   Copyright (c) 2026 LLCAR Team

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in all
   copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
   SOFTWARE.
   EOF
   ```

4. **Проверьте права доступа:**
   ```bash
   # Linux/macOS
   ls -la LICENSE
   chmod 644 LICENSE  # Если нужно исправить права

   # Windows (PowerShell)
   Get-Acl LICENSE
   ```

**Технические детали исправления:**

В версии с исправлением:
- `llcar.spec` теперь использует абсолютные пути через `SPECPATH`
- `build_exe.py` проверяет наличие всех файлов перед началом сборки
- Улучшены сообщения об ошибках для быстрой диагностики

### Ошибка: "PyInstaller not found"

**Решение:**
```bash
pip install pyinstaller
# или
pip install -r requirements-build.txt
```

### Ошибка: "FFmpeg not found"

**Решение:**

**Windows:**
1. Скачайте FFmpeg: https://ffmpeg.org/download.html
2. Распакуйте архив
3. Добавьте путь к `ffmpeg.exe` в переменную PATH
4. Перезапустите терминал

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### Ошибка при сборке установщика с Inno Setup

**Проблема:** Inno Setup не может найти файлы при компиляции `installer.iss`

**Решение:**

1. **Сначала соберите исполняемый файл:**
   ```bash
   python build_exe.py
   ```
   Это создаст директорию `dist/llcar/` со всеми необходимыми файлами.

2. **Убедитесь, что вы открываете installer.iss из корня проекта:**
   - Откройте Inno Setup Compiler
   - File → Open → выберите `installer.iss` в корне проекта
   - Build → Compile

3. **Проверьте структуру проекта:**
   ```
   LLCAR/
   ├── dist/
   │   └── llcar/          ← Должна быть создана build_exe.py
   ├── installer.iss       ← Должен быть в корне
   ├── LICENSE             ← Должен быть в корне
   ├── README.md           ← Должен быть в корне
   └── ...
   ```

## Проблемы при запуске

### Ошибка: "HuggingFace token required"

**Решение:**
1. Получите токен: https://huggingface.co/settings/tokens
2. Создайте файл `.env`:
   ```bash
   echo "HF_TOKEN=your_token_here" > .env
   ```

### Ошибка: "CUDA out of memory"

**Решение:**
```bash
# Используйте CPU вместо GPU
python main.py --video video.mp4 --device cpu
```

### Низкое качество диаризации

**Решение:**
```bash
# Укажите точное количество спикеров
python main.py --video video.mp4 --num-speakers 2
```

## Порядок правильной сборки

**Шаг 1: Установка зависимостей**
```bash
pip install -r requirements.txt
pip install -r requirements-build.txt
```

**Шаг 2: Проверка окружения**
```bash
# Проверьте, что все файлы на месте
ls -la LICENSE README.md config.yaml

# Проверьте PyInstaller
pyinstaller --version

# Проверьте FFmpeg
ffmpeg -version
```

**Шаг 3: Сборка исполняемого файла**
```bash
# Запустите из корня проекта
python build_exe.py
```

**Шаг 4: Тестирование исполняемого файла**
```bash
cd dist/llcar
./llcar.bat --help
```

**Шаг 5: Создание установщика (опционально)**
```bash
# Установите Inno Setup
# Откройте installer.iss в Inno Setup Compiler
# Нажмите Build → Compile
```

## Получение помощи

Если проблема не решена:

1. **Проверьте логи сборки** на наличие конкретных ошибок
2. **Создайте issue** на GitHub: https://github.com/llcarn8n/LLCAR/issues
3. **Включите в отчет:**
   - Версию Python (`python --version`)
   - Версию PyInstaller (`pyinstaller --version`)
   - Операционную систему
   - Полный текст ошибки
   - Вывод команды `ls -la` в корне проекта

## Часто задаваемые вопросы (FAQ)

**Q: Можно ли собрать на Linux/macOS?**
A: Да, но PyInstaller создает исполняемые файлы только для текущей платформы. Для Windows нужна сборка на Windows.

**Q: Сколько времени занимает сборка?**
A: Обычно 5-15 минут в зависимости от скорости компьютера.

**Q: Какой размер итогового установщика?**
A: Примерно 100-500 MB в зависимости от включенных зависимостей.

**Q: Нужен ли GPU для сборки?**
A: Нет, GPU нужен только для работы приложения, не для сборки.
