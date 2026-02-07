# Быстрая сборка пакетов LLCAR

**Создано:** 2026-02-07

## Как собрать готовый установщик

Теперь вы можете легко создать готовые пакеты для распространения!

### Способ 1: Портативные пакеты (Рекомендуется)

Работает на любой платформе (Linux, macOS, Windows):

```bash
# Сборка пакета для текущей платформы
python build_package.py

# Или через Make
make package
```

### Способ 2: Пакеты для всех платформ сразу

```bash
# Создает пакеты для Linux, macOS и Windows
python build_package.py --all

# Или через Make
make package-all
```

## Что получится?

После сборки в папке `dist/` вы найдете:

- **Linux:** `llcar-1.0.0-linux.tar.gz` (≈100 KB)
- **macOS:** `llcar-1.0.0-macos.tar.gz` (≈100 KB)
- **Windows:** `LLCAR-1.0.0-windows-portable.zip` (≈120 KB)

## Что внутри пакетов?

Каждый пакет содержит:
- ✅ Весь исходный код
- ✅ Скрипты установки (`install.sh` / `install.bat`)
- ✅ Лаунчеры для консоли и GUI
- ✅ Всю документацию
- ✅ Примеры конфигурации
- ✅ Файл INSTALL.txt с инструкциями

## Как пользователи будут устанавливать?

### Linux/macOS:

```bash
tar -xzf llcar-1.0.0-linux.tar.gz
cd llcar-1.0.0
./install.sh
./llcar-console.sh
```

### Windows:

```cmd
REM Распаковать ZIP в любую папку
install.bat
llcar-console.bat
```

## Преимущества этого подхода

- ✅ Работает на любой платформе
- ✅ Не требует Windows для сборки
- ✅ Очень маленький размер (≈100 KB)
- ✅ Пользователи получают исходный код
- ✅ Легко обновлять через Git
- ✅ Включены все скрипты и документация

## Для Windows .exe установщика

Если вам нужен именно .exe установщик для Windows:

1. Используйте Windows компьютер
2. Установите PyInstaller и Inno Setup
3. Запустите: `python build_exe.py`

См. подробности в [BUILD.md](BUILD.md)

## Публикация релиза на GitHub

1. Создайте tag:
   ```bash
   git tag -a v1.0.0 -m "Release 1.0.0"
   git push origin v1.0.0
   ```

2. Соберите пакеты:
   ```bash
   python build_package.py --all
   ```

3. Создайте релиз на GitHub и загрузите файлы из `dist/`

## Дополнительная информация

- **Полная документация:** [PACKAGE_BUILD_GUIDE.md](PACKAGE_BUILD_GUIDE.md)
- **Windows .exe:** [BUILD.md](BUILD.md)
- **Процесс релиза:** [RELEASE_GUIDE.md](RELEASE_GUIDE.md)

---

**LLCAR Team**
