# dectalk-python

## Contents
- [Русский](#русский)
- [English](#english)

## Русский

### О проекте
`dectalk-python` - самостоятельная Python-реализация DECtalk-style синтеза речи. Это не побитовая копия исторических DECtalk-бинарников: проект реализует практичное подмножество SAY-совместимого CLI, inline-команд DECtalk, WAV-вывода, пользовательских словарей и `TextToSpeech*` API-обвязки.

Оригинальный репозиторий DECtalk: https://github.com/dectalk/dectalk/

Оригинальный архив исходников DECtalk в этой рабочей области находится рядом: `/home/x13/VScodeProjects/tts/dectalk`.

### Структура
- `dectalk/` - Python-пакет, CLI, parser, API-обвязка и синтезатор.
- `tests/` - unittest-проверки парсера, G2P и WAV-вывода.
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
Файл словаря:

```text
dectalk=D EH K T AO K
robot=R OW B AA T
```

Запуск:

```bash
python -m dectalk -d dictionary.txt -w out.wav "dectalk robot"
```

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
`dectalk-python` is a standalone Python implementation of DECtalk-style speech synthesis. It is not a bit-exact clone of the historical DECtalk binaries: it implements a practical subset of the SAY-compatible CLI, DECtalk inline commands, WAV output, user dictionaries, and a small `TextToSpeech*` compatibility layer.

Original DECtalk repository: https://github.com/dectalk/dectalk/

The original DECtalk source archive in this workspace is next to it: `/home/x13/VScodeProjects/tts/dectalk`.

### Layout
- `dectalk/` - Python package, CLI, parser, API layer, and synthesizer.
- `tests/` - unittest coverage for parser, G2P, and WAV output.
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
Dictionary file:

```text
dectalk=D EH K T AO K
robot=R OW B AA T
```

Run:

```bash
python -m dectalk -d dictionary.txt -w out.wav "dectalk robot"
```

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
