from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VoiceProfile:
    name: str
    code: str
    description: str
    base_pitch: float
    pitch_range: float
    formant_scale: float = 1.0
    breath: float = 0.04
    roughness: float = 0.0
    speed: float = 1.0
    amplitude: float = 0.82
    whisper: bool = False


VOICES: dict[str, VoiceProfile] = {
    "paul": VoiceProfile("paul", "p", "Default male voice", 118.0, 28.0, 1.00, 0.03, 0.01),
    "harry": VoiceProfile("harry", "h", "Full male voice", 92.0, 20.0, 0.92, 0.04, 0.04, 0.92),
    "frank": VoiceProfile("frank", "f", "Aged male voice", 104.0, 16.0, 0.96, 0.11, 0.08, 0.90),
    "dennis": VoiceProfile("dennis", "d", "Nasal male voice", 132.0, 22.0, 1.05, 0.05, 0.02, 1.04),
    "betty": VoiceProfile("betty", "b", "Full female voice", 205.0, 42.0, 1.18, 0.04, 0.0, 1.04),
    "ursula": VoiceProfile("ursula", "u", "Aged female voice", 174.0, 26.0, 1.12, 0.12, 0.07, 0.94),
    "wendy": VoiceProfile("wendy", "w", "Whispering female voice", 210.0, 18.0, 1.20, 0.36, 0.03, 0.96, True),
    "rita": VoiceProfile("rita", "r", "Female voice", 188.0, 36.0, 1.15, 0.06, 0.0, 1.00),
    "kit": VoiceProfile("kit", "k", "Child voice", 255.0, 58.0, 1.33, 0.05, 0.0, 1.10),
    "val": VoiceProfile("val", "v", "User-designed voice", 140.0, 30.0, 1.02, 0.05, 0.01, 1.0),
}


VOICE_ALIASES: dict[str, str] = {}
for key, voice in VOICES.items():
    VOICE_ALIASES[key] = key
    VOICE_ALIASES[voice.code] = key
    VOICE_ALIASES[f"n{voice.code}"] = key
VOICE_ALIASES.update(
    {
        "default": "paul",
        "male": "paul",
        "female": "rita",
        "child": "kit",
    }
)


def resolve_voice(name: str) -> str:
    normalized = name.strip().lower()
    if normalized in VOICE_ALIASES:
        return VOICE_ALIASES[normalized]
    raise ValueError(f"unknown DECtalk voice: {name!r}")


def get_voice(name: str) -> VoiceProfile:
    return VOICES[resolve_voice(name)]


def voice_names() -> list[str]:
    return list(VOICES)

