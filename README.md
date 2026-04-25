# dectalk-python

This is a standalone pure Python DECtalk-style implementation. The Python code
is independent, portable, and has no runtime dependencies outside the standard
library.

It is not a bit-exact clone of the historical DECtalk binaries. It implements a
practical subset: SAY-compatible options, DECtalk inline commands, a small
TextToSpeech-style API, user dictionaries, phoneme logging, and WAV generation.

## Quick Start

```bash
python -m dectalk_py -w hello.wav "[:np] Hello from [:nb] Betty."
python -m dectalk_py -w phone.wav 'Call me [:dial "1,800-555-1212"]'
python -m dectalk_py -lp phones.txt "[:phoneme arpabet speak on][dh ih s]"
```

If `-w` is omitted, the CLI writes a WAV stream to stdout when stdout is piped,
or `dectalk.wav` when stdout is a terminal.

## Supported Inline Commands

- `[:name Paul]`, `[:np]`, `[:nb]`, `[:nh]`, `[:nf]`, `[:nd]`, `[:nu]`,
  `[:nw]`, `[:nr]`, `[:nk]`, `[:nv]`
- `[:rate 75..600]`
- `[:volume set N]`, `[:volume up N]`, `[:volume down N]`
- `[:tone frequency,duration_ms]`
- `[:dial "1,800-555-1212"]`
- `[:phoneme arpabet speak on]...[phones]...[:phoneme off]`
- `[:say letter]`, `[:say word]`, `[:say clause]`
- `[:mode spell on/off]`, `[:mode math on/off]`
- A small subset of `[:dv ...]`: `ap`, `pr`, `br`, and `sx`

## Python API

```python
from dectalk_py import TextToSpeech

tts = TextToSpeech()
tts.open_wave_out_file("out.wav")
tts.speak("[:np] DECtalk style speech in Python.")
tts.close_wave_out_file()
```

The module also exports compatibility functions such as
`TextToSpeechStartup`, `TextToSpeechSpeak`, `TextToSpeechSetRate`, and
`TextToSpeechShutdown`.

## User Dictionaries

Dictionary files are simple text files:

```text
dectalk=D EH K T AO K
robot=R OW B AA T
```

Load them with `-d dictionary.txt` or `TextToSpeech.load_user_dictionary()`.

## Tests

```bash
python -m unittest
```
