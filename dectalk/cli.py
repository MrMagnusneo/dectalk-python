from __future__ import annotations

from pathlib import Path
import sys

from .api import (
    LOG_PHONEMES,
    LOG_SYLLABLES,
    LOG_TEXT,
    TextToSpeech,
    TextToSpeechVersion,
)


HELP = """dectalk-python [options] [text]

Output options:
  -w outFile       Convert text into a wave file.
  -l[t] outFile    Write a text log.
  -lp outFile      Write a phoneme log.
  -ls outFile      Write a syllable log.

Input options:
  -pre text        Text or DECtalk commands passed before normal input.
  -post text       Text or DECtalk commands passed after normal input.
  -d userDict      Load a native DECtalk user dictionary file.
  -v               Print version.
  -h, -?           Show this help.

If text is omitted, stdin is read. If -w is omitted and stdout is a terminal,
the result is written to dectalk.wav in the current directory.
"""


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        options, text_args = parse_args(argv)
    except ValueError as exc:
        print(f"dectalk-python: {exc}", file=sys.stderr)
        return 2

    if options["help"]:
        print(HELP)
        return 0
    if options["version"]:
        print(TextToSpeechVersion())
        return 0

    engine = TextToSpeech()
    if options["dictionary"]:
        engine.load_user_dictionary(options["dictionary"])

    chunks = []
    if options["pre"]:
        chunks.append(options["pre"])
    if text_args:
        chunks.append(" ".join(text_args))
    else:
        chunks.append(sys.stdin.read())
    if options["post"]:
        chunks.append(options["post"])
    text = " ".join(chunk for chunk in chunks if chunk)

    if options["log_path"]:
        engine.open_log_file(options["log_path"], options["log_mode"])
        engine.speak(text)
        engine.close_log_file()
        return 0

    output_path = options["wave_path"]
    if output_path:
        engine.open_wave_out_file(output_path)
        engine.speak(text)
        engine.close_wave_out_file()
        return 0

    audio = engine.synthesize(text)
    if sys.stdout.isatty():
        target = Path("dectalk.wav")
        audio.write_wav(target)
        print(target)
    else:
        sys.stdout.buffer.write(audio.to_wav_bytes())
    return 0


def parse_args(argv: list[str]) -> tuple[dict[str, object], list[str]]:
    options: dict[str, object] = {
        "dictionary": None,
        "help": False,
        "log_mode": LOG_TEXT,
        "log_path": None,
        "post": None,
        "pre": None,
        "version": False,
        "wave_path": None,
    }
    text_args: list[str] = []
    index = 0
    while index < len(argv):
        arg = argv[index]
        if not arg:
            index += 1
            continue
        if arg[0] not in {"-", "/"}:
            text_args = argv[index:]
            break
        if len(arg) > 1 and arg[1] in {"-", "/"}:
            text_args = [arg[1:]] + argv[index + 1 :]
            break

        flag = "-" + arg[1:]
        lower = flag.lower()
        if lower in {"-h", "-?"}:
            options["help"] = True
            index += 1
            continue
        if lower == "-v":
            options["version"] = True
            index += 1
            continue
        if lower == "-w":
            options["wave_path"] = _next_value(argv, index, "-w")
            index += 2
            continue
        if lower.startswith("-l"):
            suffix = lower[2:] or "t"
            if suffix == "p":
                options["log_mode"] = LOG_PHONEMES
            elif suffix == "s":
                options["log_mode"] = LOG_SYLLABLES
            else:
                options["log_mode"] = LOG_TEXT
            options["log_path"] = _next_value(argv, index, flag)
            index += 2
            continue
        if lower == "-d":
            options["dictionary"] = _next_value(argv, index, "-d")
            index += 2
            continue
        if lower == "-pre":
            options["pre"] = _next_value(argv, index, "-pre")
            index += 2
            continue
        if lower == "-post":
            options["post"] = _next_value(argv, index, "-post")
            index += 2
            continue

        text_args = argv[index:]
        break
    return options, text_args


def _next_value(argv: list[str], index: int, flag: str) -> str:
    if index + 1 >= len(argv):
        raise ValueError(f"{flag} requires a value")
    return argv[index + 1]


if __name__ == "__main__":
    raise SystemExit(main())
