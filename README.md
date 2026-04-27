# dectalk-python

## Contents
- [Русский](#русский)
- [English](#english)

## Русский

### О проекте
`dectalk-python` - Python CLI и API для оригинального движка DECtalk. Речь рендерится через native `libdectalk.so`, собранный из исходников DECtalk.

Оригинальный репозиторий DECtalk: https://github.com/dectalk/dectalk/

Оригинальный архив исходников DECtalk в этой рабочей области находится рядом: `/home/x13/VScodeProjects/tts/original/dectalk`.

### Структура
- `dectalk/` - Python-пакет, CLI и API.
- `dectalk/build_backend.py` - сборка оригинального DECtalk из `original/dectalk`.
- `dectalk/native_bin/` - локальные runtime-файлы DECtalk после сборки.
- `dectalk-python.spec` - spec-файл PyInstaller.

### Возможности
- Синтез речи оригинальным DECtalk в WAV `11025 Hz`, `16-bit mono`.
- Ввод текста через аргументы командной строки или stdin.
- SAY-like параметры: `-w`, `-pre`, `-post`, `-d`, `-lt`, `-lp`, `-ls`.
- Inline-команды DECtalk: `[:name]`, `[:nX]`, `[:rate]`, `[:volume]`, `[:tone]`, `[:dial]`, `[:phoneme]`, `[:say]`, `[:mode]`.
- Оригинальные DECtalk-голоса, включая шепотный `Wendy` через `[:nw]`.
- Python API через `TextToSpeech`.
- Сборка одного исполняемого файла для текущей ОС.

### Запуск из исходников
Требования:
- Python 3.10+
- `git`, `cmake`, `tar` и C-компилятор для первой сборки native backend.

```bash
cd /home/x13/VScodeProjects/tts/dectalk-python
python -m dectalk -w hello.wav "Hello from DECtalk Python."
```

Backend собирается автоматически при первом запуске, если runtime-файлы еще не созданы. Принудительная сборка:

```bash
python -m dectalk.build_backend
```

CLI после установки пакета:

```bash
dectalk-python -w hello.wav "Hello from DECtalk Python."
```

### Примеры голосов
| Голос | Inline-команда | Пример |
| --- | --- | --- |
| Paul | `[:np]` | `python -m dectalk -w paul.wav "[:np] Hello from Paul."` |
| Harry | `[:nh]` | `python -m dectalk -w harry.wav "[:nh] Hello from Harry."` |
| Frank | `[:nf]` | `python -m dectalk -w frank.wav "[:nf] Hello from Frank."` |
| Dennis | `[:nd]` | `python -m dectalk -w dennis.wav "[:nd] Hello from Dennis."` |
| Betty | `[:nb]` | `python -m dectalk -w betty.wav "[:nb] Hello from Betty."` |
| Ursula | `[:nu]` | `python -m dectalk -w ursula.wav "[:nu] Hello from Ursula."` |
| Wendy | `[:nw]` | `python -m dectalk -w wendy.wav "[:nw] Whisper voice example."` |
| Rita | `[:nr]` | `python -m dectalk -w rita.wav "[:nr] Hello from Rita."` |
| Kit | `[:nk]` | `python -m dectalk -w kit.wav "[:nk] Hello from Kit."` |
| Val | `[:nv]` | `python -m dectalk -w val.wav "[:nv] Hello from Val."` |

### Python API
```python
from dectalk import TextToSpeech

engine = TextToSpeech()
audio = engine.synthesize("[:np] Hello, world!")
wav_bytes = audio.to_wav_bytes()
```

### Сборка исполняемого файла
PyInstaller собирает бинарник под текущую ОС:
- Linux: `dist/dectalk-python`
- Windows: `dist\dectalk-python.exe`

Сначала подготовьте native backend. На Linux это можно сделать командой:

```bash
python -m dectalk.build_backend
```

На Windows automatic native DECtalk build пока не реализован в `dectalk.build_backend`. Перед сборкой положите Windows runtime-файлы DECtalk в `dectalk\native_bin`: `dectalk.dll`, `DECtalk.conf`, `dic\dtalk_us.dic`.

Команда PyInstaller-сборки одинаковая для Linux и Windows:

```bash
python -m pip install pyinstaller
python -m PyInstaller --clean dectalk-python.spec
```

На Windows можно заменить `python` на `py`, если так настроен Python Launcher.

### Проверка
```bash
python -m unittest
python -m dectalk -w /tmp/dectalk-python-test.wav "Smoke test"
```

## English

### About
`dectalk-python` is a Python CLI and API for the original DECtalk engine. Speech is rendered through native `libdectalk.so` built from the DECtalk sources.

Original DECtalk repository: https://github.com/dectalk/dectalk/

The original DECtalk source archive in this workspace is next to it: `/home/x13/VScodeProjects/tts/original/dectalk`.

### Layout
- `dectalk/` - Python package, CLI, and API.
- `dectalk/build_backend.py` - builds original DECtalk from `original/dectalk`.
- `dectalk/native_bin/` - local DECtalk runtime files after the build.
- `dectalk-python.spec` - PyInstaller spec file.

### Features
- Original DECtalk speech synthesis to `11025 Hz`, `16-bit mono` WAV.
- Text input through command-line arguments or stdin.
- SAY-like options: `-w`, `-pre`, `-post`, `-d`, `-lt`, `-lp`, `-ls`.
- DECtalk inline commands: `[:name]`, `[:nX]`, `[:rate]`, `[:volume]`, `[:tone]`, `[:dial]`, `[:phoneme]`, `[:say]`, `[:mode]`.
- Original DECtalk voices, including whispering `Wendy` through `[:nw]`.
- Python API through `TextToSpeech`.
- Single-file executable builds for the current OS.

### Run From Source
Requirements:
- Python 3.10+
- `git`, `cmake`, `tar`, and a C compiler for the first native backend build.

```bash
cd /home/x13/VScodeProjects/tts/dectalk-python
python -m dectalk -w hello.wav "Hello from DECtalk Python."
```

The backend is built automatically on first run if the runtime files do not exist. To force a rebuild:

```bash
python -m dectalk.build_backend
```

Installed CLI:

```bash
dectalk-python -w hello.wav "Hello from DECtalk Python."
```

### Voice Examples
| Voice | Inline command | Example |
| --- | --- | --- |
| Paul | `[:np]` | `python -m dectalk -w paul.wav "[:np] Hello from Paul."` |
| Harry | `[:nh]` | `python -m dectalk -w harry.wav "[:nh] Hello from Harry."` |
| Frank | `[:nf]` | `python -m dectalk -w frank.wav "[:nf] Hello from Frank."` |
| Dennis | `[:nd]` | `python -m dectalk -w dennis.wav "[:nd] Hello from Dennis."` |
| Betty | `[:nb]` | `python -m dectalk -w betty.wav "[:nb] Hello from Betty."` |
| Ursula | `[:nu]` | `python -m dectalk -w ursula.wav "[:nu] Hello from Ursula."` |
| Wendy | `[:nw]` | `python -m dectalk -w wendy.wav "[:nw] Whisper voice example."` |
| Rita | `[:nr]` | `python -m dectalk -w rita.wav "[:nr] Hello from Rita."` |
| Kit | `[:nk]` | `python -m dectalk -w kit.wav "[:nk] Hello from Kit."` |
| Val | `[:nv]` | `python -m dectalk -w val.wav "[:nv] Hello from Val."` |

### Python API
```python
from dectalk import TextToSpeech

engine = TextToSpeech()
audio = engine.synthesize("[:np] Hello, world!")
wav_bytes = audio.to_wav_bytes()
```

### Build Executable
PyInstaller builds for the current OS:
- Linux: `dist/dectalk-python`
- Windows: `dist\dectalk-python.exe`

Prepare the native backend first. On Linux, run:

```bash
python -m dectalk.build_backend
```

Automatic native DECtalk build on Windows is not implemented in `dectalk.build_backend` yet. Before packaging, place the Windows DECtalk runtime files in `dectalk\native_bin`: `dectalk.dll`, `DECtalk.conf`, `dic\dtalk_us.dic`.

The PyInstaller build command is the same on Linux and Windows:

```bash
python -m pip install pyinstaller
python -m PyInstaller --clean dectalk-python.spec
```

On Windows, replace `python` with `py` if that is how Python Launcher is configured.

### Checks
```bash
python -m unittest
python -m dectalk -w /tmp/dectalk-python-test.wav "Smoke test"
```
