"""Python bindings for the original DECtalk speech engine.

The public surface keeps the SAY-like CLI and TextToSpeech* compatibility
helpers, while speech is rendered by the native DECtalk engine.
"""

from .api import (
    MMSYSERR_NOERROR,
    TTS_FORCE,
    TTS_NORMAL,
    TextToSpeech,
    TextToSpeechCloseLogFile,
    TextToSpeechCloseWaveOutFile,
    TextToSpeechGetRate,
    TextToSpeechGetSpeaker,
    TextToSpeechLoadUserDictionary,
    TextToSpeechOpenLogFile,
    TextToSpeechOpenWaveOutFile,
    TextToSpeechReset,
    TextToSpeechSetRate,
    TextToSpeechSetSpeaker,
    TextToSpeechSetVolume,
    TextToSpeechShutdown,
    TextToSpeechSpeak,
    TextToSpeechStartup,
    TextToSpeechSync,
    TextToSpeechUnloadUserDictionary,
    TextToSpeechVersion,
)
from .audio import AudioBuffer
from .native import DectalkNativeError, NativeDectalkBackend
from .parser import DectalkParser, SynthState
from .voices import VoiceProfile, voice_names

__all__ = [
    "AudioBuffer",
    "DectalkParser",
    "DectalkNativeError",
    "MMSYSERR_NOERROR",
    "NativeDectalkBackend",
    "SynthState",
    "TTS_FORCE",
    "TTS_NORMAL",
    "TextToSpeech",
    "TextToSpeechCloseLogFile",
    "TextToSpeechCloseWaveOutFile",
    "TextToSpeechGetRate",
    "TextToSpeechGetSpeaker",
    "TextToSpeechLoadUserDictionary",
    "TextToSpeechOpenLogFile",
    "TextToSpeechOpenWaveOutFile",
    "TextToSpeechReset",
    "TextToSpeechSetRate",
    "TextToSpeechSetSpeaker",
    "TextToSpeechSetVolume",
    "TextToSpeechShutdown",
    "TextToSpeechSpeak",
    "TextToSpeechStartup",
    "TextToSpeechSync",
    "TextToSpeechUnloadUserDictionary",
    "TextToSpeechVersion",
    "VoiceProfile",
    "voice_names",
]

__version__ = "0.2.0"
