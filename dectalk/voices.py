from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VoiceProfile:
    name: str
    code: str
    description: str
    speaker: int


VOICES: dict[str, VoiceProfile] = {
    "paul": VoiceProfile("paul", "p", "Default male voice", 0),
    "betty": VoiceProfile("betty", "b", "Full female voice", 1),
    "harry": VoiceProfile("harry", "h", "Full male voice", 2),
    "frank": VoiceProfile("frank", "f", "Aged male voice", 3),
    "dennis": VoiceProfile("dennis", "d", "Nasal male voice", 4),
    "kit": VoiceProfile("kit", "k", "Child voice", 5),
    "ursula": VoiceProfile("ursula", "u", "Aged female voice", 6),
    "rita": VoiceProfile("rita", "r", "Female voice", 7),
    "wendy": VoiceProfile("wendy", "w", "Whispering female voice", 8),
    "val": VoiceProfile("val", "v", "User-designed voice", 9),
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


def speaker_id(name: str) -> int:
    return get_voice(name).speaker


def voice_names() -> list[str]:
    return list(VOICES)
