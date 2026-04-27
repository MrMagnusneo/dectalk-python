from __future__ import annotations

from contextlib import contextmanager
from ctypes import CDLL, POINTER, byref, c_char_p, c_int, c_long, c_uint, c_uint32, c_void_p
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import sys
import threading

from .audio import AudioBuffer
from .voices import speaker_id


class DectalkNativeError(RuntimeError):
    pass


WAVE_MAPPER = c_uint(-1).value
DO_NOT_USE_AUDIO_DEVICE = 0x80000000
WAVE_FORMAT_1M16 = 0x00000004
TTS_FORCE = 1
VOLUME_MAIN = 1
LOG_TEXT_NATIVE = 0x0001
LOG_PHONEMES_NATIVE = 0x0002
LOG_SYLLABLES_NATIVE = 0x0010

_CWD_LOCK = threading.RLock()


@dataclass(frozen=True)
class NativeBundle:
    root: Path
    library: Path
    runtime_dir: Path


class NativeDectalkBackend:
    """ctypes wrapper around the original DECtalk engine."""

    sample_rate = 11025

    def __init__(self, bundle_dir: str | Path | None = None, *, auto_build: bool = True):
        self.bundle = find_native_bundle(bundle_dir, auto_build=auto_build)
        self.lib = CDLL(str(self.bundle.library))
        self._configure_api()

    def synthesize(
        self,
        text: str,
        *,
        voice: str = "paul",
        rate: int = 180,
        volume: int = 100,
        dictionary_paths: list[Path] | None = None,
        log_path: Path | None = None,
        log_mode: str | int | None = None,
    ) -> AudioBuffer:
        if not text:
            return AudioBuffer(self.sample_rate)

        with TemporaryDirectory(prefix="dectalk-native-") as tmp:
            wave_path = Path(tmp) / "speech.wav"
            with _native_runtime_cwd(self.bundle.runtime_dir):
                handle = self._startup()
                try:
                    self._check(self.lib.TextToSpeechSetSpeaker(handle, speaker_id(voice)), "TextToSpeechSetSpeaker")
                    self._check(self.lib.TextToSpeechSetRate(handle, max(75, min(600, int(rate)))), "TextToSpeechSetRate")
                    self._check(
                        self.lib.TextToSpeechSetVolume(handle, VOLUME_MAIN, max(0, min(100, int(volume)))),
                        "TextToSpeechSetVolume",
                    )
                    for path in dictionary_paths or []:
                        self._check(
                            self.lib.TextToSpeechLoadUserDictionary(handle, _path_bytes(path)),
                            "TextToSpeechLoadUserDictionary",
                        )
                    log_only = log_path is not None
                    if log_only:
                        self._check(
                            self.lib.TextToSpeechOpenLogFile(handle, _path_bytes(log_path), _native_log_mode(log_mode)),
                            "TextToSpeechOpenLogFile",
                        )
                    else:
                        self._check(
                            self.lib.TextToSpeechOpenWaveOutFile(handle, _path_bytes(wave_path), WAVE_FORMAT_1M16),
                            "TextToSpeechOpenWaveOutFile",
                        )
                    self._check(self.lib.TextToSpeechSpeak(handle, _text_bytes(text), TTS_FORCE), "TextToSpeechSpeak")
                    self._check(self.lib.TextToSpeechSync(handle), "TextToSpeechSync")
                    if log_only:
                        self._check(self.lib.TextToSpeechCloseLogFile(handle), "TextToSpeechCloseLogFile")
                    else:
                        self._check(self.lib.TextToSpeechCloseWaveOutFile(handle), "TextToSpeechCloseWaveOutFile")
                finally:
                    self.lib.TextToSpeechShutdown(handle)
            if log_path is not None:
                return AudioBuffer(self.sample_rate)
            return AudioBuffer.read_wav(wave_path)

    def _startup(self) -> c_void_p:
        handle = c_void_p()
        status = self.lib.TextToSpeechStartup(byref(handle), WAVE_MAPPER, DO_NOT_USE_AUDIO_DEVICE, None, 0)
        self._check(status, "TextToSpeechStartup")
        if not handle.value:
            raise DectalkNativeError("TextToSpeechStartup returned an empty handle")
        return handle

    def _configure_api(self) -> None:
        self.lib.TextToSpeechStartup.argtypes = [POINTER(c_void_p), c_uint, c_uint32, c_void_p, c_long]
        self.lib.TextToSpeechStartup.restype = c_uint
        self.lib.TextToSpeechShutdown.argtypes = [c_void_p]
        self.lib.TextToSpeechShutdown.restype = c_uint
        self.lib.TextToSpeechSpeak.argtypes = [c_void_p, c_char_p, c_uint32]
        self.lib.TextToSpeechSpeak.restype = c_uint
        self.lib.TextToSpeechSync.argtypes = [c_void_p]
        self.lib.TextToSpeechSync.restype = c_uint
        self.lib.TextToSpeechSetSpeaker.argtypes = [c_void_p, c_int]
        self.lib.TextToSpeechSetSpeaker.restype = c_uint
        self.lib.TextToSpeechSetRate.argtypes = [c_void_p, c_uint32]
        self.lib.TextToSpeechSetRate.restype = c_uint
        self.lib.TextToSpeechSetVolume.argtypes = [c_void_p, c_int, c_int]
        self.lib.TextToSpeechSetVolume.restype = c_uint
        self.lib.TextToSpeechOpenWaveOutFile.argtypes = [c_void_p, c_char_p, c_uint32]
        self.lib.TextToSpeechOpenWaveOutFile.restype = c_uint
        self.lib.TextToSpeechCloseWaveOutFile.argtypes = [c_void_p]
        self.lib.TextToSpeechCloseWaveOutFile.restype = c_uint
        self.lib.TextToSpeechOpenLogFile.argtypes = [c_void_p, c_char_p, c_uint32]
        self.lib.TextToSpeechOpenLogFile.restype = c_uint
        self.lib.TextToSpeechCloseLogFile.argtypes = [c_void_p]
        self.lib.TextToSpeechCloseLogFile.restype = c_uint
        self.lib.TextToSpeechLoadUserDictionary.argtypes = [c_void_p, c_char_p]
        self.lib.TextToSpeechLoadUserDictionary.restype = c_uint

    def _check(self, status: int, function_name: str) -> None:
        if status != 0:
            raise DectalkNativeError(f"{function_name} failed with DECtalk status {status}")


def find_native_bundle(bundle_dir: str | Path | None = None, *, auto_build: bool = True) -> NativeBundle:
    candidates = []
    if bundle_dir is not None:
        candidates.append(Path(bundle_dir))
    env_root = os.environ.get("DECTALK_NATIVE_ROOT")
    if env_root:
        candidates.append(Path(env_root))
    candidates.append(native_bundle_dir())
    candidates.append(Path("/tmp/dectalk-cmake-build/bin"))

    for candidate in candidates:
        bundle = _bundle_from_root(candidate)
        if bundle is not None:
            return bundle

    if auto_build:
        from .build_backend import build_backend

        return _bundle_from_root(build_backend()) or _raise_missing_bundle()
    return _raise_missing_bundle()


def native_library_name() -> str:
    if sys.platform == "darwin":
        return "libdectalk.dylib"
    if sys.platform == "win32":
        return "dectalk.dll"
    return "libdectalk.so"


def native_bundle_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "dectalk" / "native_bin"  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent / "native_bin"


def _bundle_from_root(root: Path) -> NativeBundle | None:
    root = root.expanduser().resolve()
    lib_name = native_library_name()
    library_candidates = [
        root / lib_name,
        root / "lib" / lib_name,
        root.parent / "lib" / lib_name if root.name == "bin" else root / "bin" / lib_name,
    ]
    runtime_candidates = [
        root,
        root / "bin",
        root.parent / "bin" if root.name == "lib" else root,
    ]
    library = next((path for path in library_candidates if path.exists()), None)
    runtime_dir = next(
        (
            path
            for path in runtime_candidates
            if (path / "DECtalk.conf").exists() and (path / "dic" / "dtalk_us.dic").exists()
        ),
        None,
    )
    if library is None or runtime_dir is None:
        return None
    return NativeBundle(root=root, library=library, runtime_dir=runtime_dir)


def _raise_missing_bundle() -> NativeBundle:
    raise DectalkNativeError(
        "native DECtalk backend is missing. Run `python -m dectalk.build_backend` "
        "from dectalk-python, or set DECTALK_NATIVE_ROOT to a built DECtalk bundle."
    )


@contextmanager
def _native_runtime_cwd(runtime_dir: Path):
    with _CWD_LOCK:
        old_cwd = Path.cwd()
        os.chdir(runtime_dir)
        try:
            yield
        finally:
            os.chdir(old_cwd)


def _path_bytes(path: str | Path) -> bytes:
    return os.fsencode(Path(path))


def _text_bytes(text: str) -> bytes:
    return text.encode("windows-1252", errors="replace")


def _native_log_mode(mode: str | int | None) -> int:
    if isinstance(mode, int):
        return mode
    if mode == "phonemes":
        return LOG_PHONEMES_NATIVE
    if mode == "syllables":
        return LOG_SYLLABLES_NATIVE
    return LOG_TEXT_NATIVE
