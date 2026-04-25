from __future__ import annotations

from pathlib import Path
from typing import TextIO

from .audio import AudioBuffer
from .g2p import Phone, arpabet_to_phones, phones_to_symbols, syllables_from_phones, text_to_phones
from .parser import DectalkParser, SpeechSegment, SynthState
from .synth import DectalkSynthesizer
from .voices import resolve_voice


MMSYSERR_NOERROR = 0
MMSYSERR_ERROR = 1
TTS_NORMAL = 0
TTS_FORCE = 1
LOG_TEXT = "text"
LOG_PHONEMES = "phonemes"
LOG_SYLLABLES = "syllables"
VERSION = "DECtalk Python 0.1.0"


class TextToSpeech:
    def __init__(self, sample_rate: int = 22050):
        self.state = SynthState()
        self.parser = DectalkParser(self.state)
        self.synthesizer = DectalkSynthesizer(sample_rate)
        self.dictionary: dict[str, list[Phone]] = {}
        self._wave_path: Path | None = None
        self._wave_buffer: AudioBuffer | None = None
        self._last_audio = AudioBuffer(sample_rate)
        self._log_file: TextIO | None = None
        self._log_mode = LOG_TEXT

    @property
    def last_audio(self) -> AudioBuffer:
        return self._last_audio.copy()

    def synthesize(self, text: str) -> AudioBuffer:
        segments = self.parser.parse(text)
        self._write_log(segments)
        return self.synthesizer.render(segments, self.dictionary)

    def speak(self, text: str, flags: int = TTS_NORMAL) -> int:
        audio = self.synthesize(text or "")
        self._last_audio = audio
        if self._wave_buffer is not None:
            self._wave_buffer.extend(audio.samples)
        return MMSYSERR_NOERROR

    def open_wave_out_file(self, path: str | Path) -> int:
        self.sync()
        self._wave_path = Path(path)
        self._wave_buffer = AudioBuffer(self.synthesizer.sample_rate)
        return MMSYSERR_NOERROR

    def close_wave_out_file(self) -> int:
        if self._wave_path is not None and self._wave_buffer is not None:
            self._wave_buffer.normalize().write_wav(self._wave_path)
        self._wave_path = None
        self._wave_buffer = None
        return MMSYSERR_NOERROR

    def open_log_file(self, path: str | Path, mode: str = LOG_TEXT) -> int:
        self.close_log_file()
        self._log_file = Path(path).open("w", encoding="utf-8")
        self._log_mode = mode
        return MMSYSERR_NOERROR

    def close_log_file(self) -> int:
        if self._log_file is not None:
            self._log_file.close()
        self._log_file = None
        return MMSYSERR_NOERROR

    def load_user_dictionary(self, path: str | Path) -> int:
        self.dictionary.update(load_user_dictionary(path))
        return MMSYSERR_NOERROR

    def unload_user_dictionary(self) -> int:
        self.dictionary.clear()
        return MMSYSERR_NOERROR

    def reset(self, reset_state: bool = True) -> int:
        self._last_audio = AudioBuffer(self.synthesizer.sample_rate)
        if self._wave_buffer is not None:
            self._wave_buffer = AudioBuffer(self.synthesizer.sample_rate)
        if reset_state:
            self.state = SynthState()
            self.parser.state = self.state
        return MMSYSERR_NOERROR

    def sync(self) -> int:
        return MMSYSERR_NOERROR

    def shutdown(self) -> int:
        self.close_wave_out_file()
        self.close_log_file()
        return MMSYSERR_NOERROR

    def get_rate(self) -> int:
        return self.state.rate

    def set_rate(self, rate: int) -> int:
        self.state.rate = max(75, min(600, int(rate)))
        return MMSYSERR_NOERROR

    def get_speaker(self) -> str:
        return self.state.voice_name

    def set_speaker(self, speaker: str) -> int:
        self.state.voice_name = resolve_voice(speaker)
        return MMSYSERR_NOERROR

    def set_volume(self, volume: int) -> int:
        self.state.volume = max(0, min(99, int(volume)))
        return MMSYSERR_NOERROR

    def _write_log(self, segments: list[object]) -> None:
        if self._log_file is None:
            return
        for segment in segments:
            if not isinstance(segment, SpeechSegment):
                continue
            if self._log_mode == LOG_TEXT:
                self._log_file.write(segment.text)
            elif self._log_mode == LOG_PHONEMES:
                phones = arpabet_to_phones(segment.text) if segment.phonemes else text_to_phones(segment.text, segment.state, self.dictionary)
                self._log_file.write(" ".join(phones_to_symbols(phones)) + "\n")
            elif self._log_mode == LOG_SYLLABLES:
                phones = arpabet_to_phones(segment.text) if segment.phonemes else text_to_phones(segment.text, segment.state, self.dictionary)
                self._log_file.write(" ".join(syllables_from_phones(phones)) + "\n")


def load_user_dictionary(path: str | Path) -> dict[str, list[Phone]]:
    entries: dict[str, list[Phone]] = {}
    for raw in Path(path).read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", ";")):
            continue
        if "=" in line:
            word, pronunciation = line.split("=", 1)
        else:
            parts = line.split(maxsplit=1)
            if len(parts) != 2:
                continue
            word, pronunciation = parts
        phones = arpabet_to_phones(pronunciation)
        if phones:
            entries[word.strip().lower()] = phones
    return entries


def TextToSpeechStartup(*_args, **_kwargs) -> TextToSpeech:
    return TextToSpeech()


def TextToSpeechShutdown(handle: TextToSpeech) -> int:
    return handle.shutdown()


def TextToSpeechSpeak(handle: TextToSpeech, text: str, flags: int = TTS_NORMAL) -> int:
    return handle.speak(text, flags)


def TextToSpeechOpenWaveOutFile(handle: TextToSpeech, path: str, *_args) -> int:
    return handle.open_wave_out_file(path)


def TextToSpeechCloseWaveOutFile(handle: TextToSpeech) -> int:
    return handle.close_wave_out_file()


def TextToSpeechOpenLogFile(handle: TextToSpeech, path: str, mode: str = LOG_TEXT) -> int:
    return handle.open_log_file(path, mode)


def TextToSpeechCloseLogFile(handle: TextToSpeech) -> int:
    return handle.close_log_file()


def TextToSpeechLoadUserDictionary(handle: TextToSpeech, path: str) -> int:
    return handle.load_user_dictionary(path)


def TextToSpeechUnloadUserDictionary(handle: TextToSpeech) -> int:
    return handle.unload_user_dictionary()


def TextToSpeechReset(handle: TextToSpeech, reset_state: bool = True) -> int:
    return handle.reset(reset_state)


def TextToSpeechSync(handle: TextToSpeech) -> int:
    return handle.sync()


def TextToSpeechGetRate(handle: TextToSpeech) -> int:
    return handle.get_rate()


def TextToSpeechSetRate(handle: TextToSpeech, rate: int) -> int:
    return handle.set_rate(rate)


def TextToSpeechGetSpeaker(handle: TextToSpeech) -> str:
    return handle.get_speaker()


def TextToSpeechSetSpeaker(handle: TextToSpeech, speaker: str) -> int:
    return handle.set_speaker(speaker)


def TextToSpeechSetVolume(handle: TextToSpeech, _volume_type: int, volume: int) -> int:
    return handle.set_volume(volume)


def TextToSpeechVersion() -> str:
    return VERSION

