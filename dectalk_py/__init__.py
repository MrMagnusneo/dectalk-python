"""Pure Python DECtalk-style speech synthesis.

This package is an independent Python implementation that preserves a useful
subset of DECtalk's public surface: SAY-like command line behavior, inline
commands, and a small TextToSpeech* compatibility layer.
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
from .parser import DectalkParser, SynthState
from .synth import DectalkSynthesizer
from .voices import VoiceProfile, voice_names

__all__ = [
    "AudioBuffer",
    "DectalkParser",
    "DectalkSynthesizer",
    "MMSYSERR_NOERROR",
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

__version__ = "0.1.0"

