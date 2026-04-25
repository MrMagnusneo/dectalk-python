# dectalk-python

## Contents
- [Русский](#русский)
- [English](#english)

## Русский

### О проекте
`dectalk-python` - самостоятельная Python-реализация DECtalk-style синтеза речи. Это не побитовая копия исторических DECtalk-бинарников: проект реализует практичное подмножество SAY-совместимого CLI, inline-команд DECtalk, WAV-вывода, пользовательских словарей и `TextToSpeech*` API-обвязки.

Оригинальный архив исходников DECtalk в этой рабочей области находится рядом: `/home/x13/VScodeProjects/tts/dectalk`.

### Структура
- `dectalk_python/` - Python-пакет, CLI, parser, API-обвязка и синтезатор.
- `tests/` - unittest-проверки парсера, G2P и WAV-вывода.
- `build_executable.py` - сборка одного исполняемого файла через PyInstaller.
- `pyinstaller_entry.py` - точка входа для PyInstaller.
- `dectalk-python.spec` - spec-файл PyInstaller.

### Возможности
- Синтез речи в WAV без внешних runtime-зависимостей.
- Ввод текста через аргументы командной строки или stdin.
- SAY-like параметры: `-w`, `-pre`, `-post`, `-d`, `-lt`, `-lp`, `-ls`.
- Inline-команды DECtalk: `[:name]`, `[:nX]`, `[:rate]`, `[:volume]`, `[:tone]`, `[:dial]`, `[:phoneme]`, `[:say]`, `[:mode]`.
- Несколько DECtalk-style голосов, включая шепотный `Wendy` через `[:nw]`.
- Пользовательские словари в простом формате `word=ARPABET PHONES`.

### Запуск из исходников
Требования:
- Python 3.10+

```bash
cd /home/x13/VScodeProjects/tts/dectalk-python
python -m dectalk_python -w hello.wav "Hello from DECtalk Python."
```

CLI после установки пакета:

```bash
dectalk-python -w hello.wav "Hello from DECtalk Python."
```

Пример с голосом Wendy:

```bash
python -m dectalk_python -w wendy.wav "[:nw] Whisper voice example."
```

### Пользовательские словари
Файл словаря:

```text
dectalk=D EH K T AO K
robot=R OW B AA T
```

Запуск:

```bash
python -m dectalk_python -d dictionary.txt -w out.wav "dectalk robot"
```

### Сборка исполняемого файла
PyInstaller собирает бинарник под текущую ОС:
- Linux: `dist/dectalk-python`
- Windows: `dist\dectalk-python.exe`

```bash
python -m pip install pyinstaller
python build_executable.py
```

То же через spec-файл:

```bash
python -m PyInstaller --clean dectalk-python.spec
```

### Проверка
```bash
python -m unittest
python -m dectalk_python -w /tmp/dectalk-python-test.wav "Smoke test"
```

## English

### About
`dectalk-python` is a standalone Python implementation of DECtalk-style speech synthesis. It is not a bit-exact clone of the historical DECtalk binaries: it implements a practical subset of the SAY-compatible CLI, DECtalk inline commands, WAV output, user dictionaries, and a small `TextToSpeech*` compatibility layer.

The original DECtalk source archive in this workspace is next to it: `/home/x13/VScodeProjects/tts/dectalk`.

### Layout
- `dectalk_python/` - Python package, CLI, parser, API layer, and synthesizer.
- `tests/` - unittest coverage for parser, G2P, and WAV output.
- `build_executable.py` - single-file executable build helper.
- `pyinstaller_entry.py` - PyInstaller entry point.
- `dectalk-python.spec` - PyInstaller spec file.

### Features
- Speech synthesis to WAV with no external runtime dependencies.
- Text input through command-line arguments or stdin.
- SAY-like options: `-w`, `-pre`, `-post`, `-d`, `-lt`, `-lp`, `-ls`.
- DECtalk inline commands: `[:name]`, `[:nX]`, `[:rate]`, `[:volume]`, `[:tone]`, `[:dial]`, `[:phoneme]`, `[:say]`, `[:mode]`.
- Several DECtalk-style voices, including whispering `Wendy` through `[:nw]`.
- User dictionaries with simple `word=ARPABET PHONES` entries.

### Run From Source
Requirements:
- Python 3.10+

```bash
cd /home/x13/VScodeProjects/tts/dectalk-python
python -m dectalk_python -w hello.wav "Hello from DECtalk Python."
```

Installed CLI:

```bash
dectalk-python -w hello.wav "Hello from DECtalk Python."
```

Wendy voice example:

```bash
python -m dectalk_python -w wendy.wav "[:nw] Whisper voice example."
```

### User Dictionaries
Dictionary file:

```text
dectalk=D EH K T AO K
robot=R OW B AA T
```

Run:

```bash
python -m dectalk_python -d dictionary.txt -w out.wav "dectalk robot"
```

### Build Executable
PyInstaller builds for the current OS:
- Linux: `dist/dectalk-python`
- Windows: `dist\dectalk-python.exe`

```bash
python -m pip install pyinstaller
python build_executable.py
```

The spec file can also be used directly:

```bash
python -m PyInstaller --clean dectalk-python.spec
```

### Checks
```bash
python -m unittest
python -m dectalk_python -w /tmp/dectalk-python-test.wav "Smoke test"
```
