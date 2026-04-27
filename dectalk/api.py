from __future__ import annotations

from pathlib import Path

from .audio import AudioBuffer
from .parser import DectalkParser, SynthState
from .native import NativeDectalkBackend
from .voices import resolve_voice


MMSYSERR_NOERROR = 0
MMSYSERR_ERROR = 1
TTS_NORMAL = 0
TTS_FORCE = 1
LOG_TEXT = "text"
LOG_PHONEMES = "phonemes"
LOG_SYLLABLES = "syllables"
VERSION = "DECtalk Python 0.2.0 (native DECtalk backend)"


class TextToSpeech:
    def __init__(self, *, backend: NativeDectalkBackend | None = None):
        self.state = SynthState()
        self.parser = DectalkParser(self.state)
        self.backend = backend or NativeDectalkBackend()
        self.dictionary_paths: list[Path] = []
        self._wave_path: Path | None = None
        self._wave_buffer: AudioBuffer | None = None
        self._last_audio = AudioBuffer(self.backend.sample_rate)
        self._log_path: Path | None = None
        self._log_mode = LOG_TEXT

    @property
    def last_audio(self) -> AudioBuffer:
        return self._last_audio.copy()

    def synthesize(self, text: str) -> AudioBuffer:
        voice = self.state.voice_name
        rate = self.state.rate
        volume = self.state.volume
        self.parser.parse(text)
        return self.backend.synthesize(
            text,
            voice=voice,
            rate=rate,
            volume=volume,
            dictionary_paths=self.dictionary_paths,
            log_path=self._log_path,
            log_mode=self._log_mode,
        )

    def speak(self, text: str, flags: int = TTS_NORMAL) -> int:
        audio = self.synthesize(text or "")
        self._last_audio = audio
        if self._wave_buffer is not None:
            self._wave_buffer.extend(audio.samples)
        return MMSYSERR_NOERROR

    def open_wave_out_file(self, path: str | Path) -> int:
        self.sync()
        self._wave_path = Path(path)
        self._wave_buffer = AudioBuffer(self.backend.sample_rate)
        return MMSYSERR_NOERROR

    def close_wave_out_file(self) -> int:
        if self._wave_path is not None and self._wave_buffer is not None:
            self._wave_buffer.write_wav(self._wave_path)
        self._wave_path = None
        self._wave_buffer = None
        return MMSYSERR_NOERROR

    def open_log_file(self, path: str | Path, mode: str = LOG_TEXT) -> int:
        self.close_log_file()
        self._log_path = Path(path)
        self._log_mode = mode
        return MMSYSERR_NOERROR

    def close_log_file(self) -> int:
        self._log_path = None
        return MMSYSERR_NOERROR

    def load_user_dictionary(self, path: str | Path) -> int:
        dictionary_path = Path(path)
        if dictionary_path not in self.dictionary_paths:
            self.dictionary_paths.append(dictionary_path)
        return MMSYSERR_NOERROR

    def unload_user_dictionary(self) -> int:
        self.dictionary_paths.clear()
        return MMSYSERR_NOERROR

    def reset(self, reset_state: bool = True) -> int:
        self._last_audio = AudioBuffer(self.backend.sample_rate)
        if self._wave_buffer is not None:
            self._wave_buffer = AudioBuffer(self.backend.sample_rate)
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
        self.state.volume = max(0, min(100, int(volume)))
        return MMSYSERR_NOERROR


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
