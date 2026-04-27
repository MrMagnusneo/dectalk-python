# dectalk-python

## Contents
- [Русский](#русский)
- [English](#english)

## Русский

### О проекте
`dectalk-python` - Python-обвязка оригинального движка DECtalk. Речь теперь рендерится через native `libdectalk.so`, собранный из исходников DECtalk, а не через прежний упрощенный Python-синтезатор.

Оригинальный репозиторий DECtalk: https://github.com/dectalk/dectalk/

Оригинальный архив исходников DECtalk в этой рабочей области находится рядом: `/home/x13/VScodeProjects/tts/original/dectalk`.

### Структура
- `dectalk/` - Python-пакет, CLI, parser, API-обвязка и native backend.
- `dectalk/build_backend.py` - сборка оригинального DECtalk из `original/dectalk`.
- `dectalk/native_bin/` - локальные runtime-файлы DECtalk после сборки.
- `tests/` - unittest-проверки парсера, G2P и WAV-вывода.
- `dectalk-python.spec` - spec-файл PyInstaller.

### Возможности
- Синтез речи оригинальным DECtalk в WAV `11025 Hz`, `16-bit mono`.
- Ввод текста через аргументы командной строки или stdin.
- SAY-like параметры: `-w`, `-pre`, `-post`, `-d`, `-lt`, `-lp`, `-ls`.
- Inline-команды DECtalk: `[:name]`, `[:nX]`, `[:rate]`, `[:volume]`, `[:tone]`, `[:dial]`, `[:phoneme]`, `[:say]`, `[:mode]`.
- Оригинальные DECtalk-голоса, включая шепотный `Wendy` через `[:nw]`.
- Старый Python-синтезатор удален: в пакете остался только native DECtalk backend.

### Запуск из исходников
Требования:
- Python 3.10+
- `git`, `cmake`, `tar` и C-компилятор для первой сборки native backend.

Собрать native backend вручную:

```bash
cd /home/x13/VScodeProjects/tts/dectalk-python
python -m dectalk.build_backend
```

Если backend еще не собран, `TextToSpeech` попробует собрать его автоматически при первом запуске.

```bash
cd /home/x13/VScodeProjects/tts/dectalk-python
python -m dectalk -w hello.wav "Hello from DECtalk Python."
```

CLI после установки пакета:

```bash
dectalk-python -w hello.wav "Hello from DECtalk Python."
```

Примеры всех голосов:

| Голос | Inline-команда | Описание | Пример |
| --- | --- | --- | --- |
| Paul | `[:np]` | Основной мужской голос | `python -m dectalk -w paul.wav "[:np] Hello from Paul."` |
| Harry | `[:nh]` | Насыщенный мужской голос | `python -m dectalk -w harry.wav "[:nh] Hello from Harry."` |
| Frank | `[:nf]` | Возрастной мужской голос | `python -m dectalk -w frank.wav "[:nf] Hello from Frank."` |
| Dennis | `[:nd]` | Носовой мужской голос | `python -m dectalk -w dennis.wav "[:nd] Hello from Dennis."` |
| Betty | `[:nb]` | Насыщенный женский голос | `python -m dectalk -w betty.wav "[:nb] Hello from Betty."` |
| Ursula | `[:nu]` | Возрастной женский голос | `python -m dectalk -w ursula.wav "[:nu] Hello from Ursula."` |
| Wendy | `[:nw]` | Шепотный женский голос | `python -m dectalk -w wendy.wav "[:nw] Whisper voice example."` |
| Rita | `[:nr]` | Женский голос | `python -m dectalk -w rita.wav "[:nr] Hello from Rita."` |
| Kit | `[:nk]` | Детский голос | `python -m dectalk -w kit.wav "[:nk] Hello from Kit."` |
| Val | `[:nv]` | Настраиваемый пользовательский голос | `python -m dectalk -w val.wav "[:nv] Hello from Val."` |

### Пользовательские словари
Native backend использует оригинальный DECtalk-словарь `dtalk_us.dic`. CLI принимает `-d` как путь к native DECtalk user dictionary file; старый Python-формат `word=ARPABET PHONES` удален вместе с Python-синтезатором.

### Сборка исполняемого файла
PyInstaller собирает бинарник под текущую ОС:
- Linux: `dist/dectalk-python`
- Windows: `dist\dectalk-python.exe`

```bash
python -m pip install pyinstaller
python -m PyInstaller --clean dectalk-python.spec
```

### Проверка
```bash
python -m unittest
python -m dectalk -w /tmp/dectalk-python-test.wav "Smoke test"
```

## English

### About
`dectalk-python` is a Python binding for the original DECtalk engine. Speech is now rendered through native `libdectalk.so` built from the DECtalk sources, not through the previous simplified Python synthesizer.

Original DECtalk repository: https://github.com/dectalk/dectalk/

The original DECtalk source archive in this workspace is next to it: `/home/x13/VScodeProjects/tts/original/dectalk`.

### Layout
- `dectalk/` - Python package, CLI, parser, API layer, and native backend.
- `dectalk/build_backend.py` - builds original DECtalk from `original/dectalk`.
- `dectalk/native_bin/` - local DECtalk runtime files after the build.
- `tests/` - unittest coverage for parser, G2P, and WAV output.
- `dectalk-python.spec` - PyInstaller spec file.

### Features
- Original DECtalk speech synthesis to `11025 Hz`, `16-bit mono` WAV.
- Text input through command-line arguments or stdin.
- SAY-like options: `-w`, `-pre`, `-post`, `-d`, `-lt`, `-lp`, `-ls`.
- DECtalk inline commands: `[:name]`, `[:nX]`, `[:rate]`, `[:volume]`, `[:tone]`, `[:dial]`, `[:phoneme]`, `[:say]`, `[:mode]`.
- Original DECtalk voices, including whispering `Wendy` through `[:nw]`.
- The old Python synthesizer has been removed: the package now keeps only the native DECtalk backend.

### Run From Source
Requirements:
- Python 3.10+
- `git`, `cmake`, `tar`, and a C compiler for the first native backend build.

Build the native backend manually:

```bash
cd /home/x13/VScodeProjects/tts/dectalk-python
python -m dectalk.build_backend
```

If the backend has not been built yet, `TextToSpeech` will try to build it automatically on first use.

```bash
cd /home/x13/VScodeProjects/tts/dectalk-python
python -m dectalk -w hello.wav "Hello from DECtalk Python."
```

Installed CLI:

```bash
dectalk-python -w hello.wav "Hello from DECtalk Python."
```

All voice examples:

| Voice | Inline command | Description | Example |
| --- | --- | --- | --- |
| Paul | `[:np]` | Default male voice | `python -m dectalk -w paul.wav "[:np] Hello from Paul."` |
| Harry | `[:nh]` | Full male voice | `python -m dectalk -w harry.wav "[:nh] Hello from Harry."` |
| Frank | `[:nf]` | Aged male voice | `python -m dectalk -w frank.wav "[:nf] Hello from Frank."` |
| Dennis | `[:nd]` | Nasal male voice | `python -m dectalk -w dennis.wav "[:nd] Hello from Dennis."` |
| Betty | `[:nb]` | Full female voice | `python -m dectalk -w betty.wav "[:nb] Hello from Betty."` |
| Ursula | `[:nu]` | Aged female voice | `python -m dectalk -w ursula.wav "[:nu] Hello from Ursula."` |
| Wendy | `[:nw]` | Whispering female voice | `python -m dectalk -w wendy.wav "[:nw] Whisper voice example."` |
| Rita | `[:nr]` | Female voice | `python -m dectalk -w rita.wav "[:nr] Hello from Rita."` |
| Kit | `[:nk]` | Child voice | `python -m dectalk -w kit.wav "[:nk] Hello from Kit."` |
| Val | `[:nv]` | User-designed voice | `python -m dectalk -w val.wav "[:nv] Hello from Val."` |

### User Dictionaries
The native backend uses the original DECtalk `dtalk_us.dic` dictionary. The CLI accepts `-d` as a path to a native DECtalk user dictionary file; the old Python `word=ARPABET PHONES` format was removed with the Python synthesizer.

### Build Executable
PyInstaller builds for the current OS:
- Linux: `dist/dectalk-python`
- Windows: `dist\dectalk-python.exe`

```bash
python -m pip install pyinstaller
python -m PyInstaller --clean dectalk-python.spec
```

### Checks
```bash
python -m unittest
python -m dectalk -w /tmp/dectalk-python-test.wav "Smoke test"
```
