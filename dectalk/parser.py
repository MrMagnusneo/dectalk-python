from __future__ import annotations

from dataclasses import dataclass, field
import re
import shlex

from .voices import resolve_voice


def _clamp(value: int, lower: int, upper: int) -> int:
    return max(lower, min(upper, value))


@dataclass
class SynthState:
    voice_name: str = "paul"
    rate: int = 180
    volume: int = 100
    phoneme_mode: bool = False
    phoneme_silent: bool = False
    say_mode: str = "clause"
    spell_mode: bool = False
    math_mode: bool = False
    email_mode: bool = False
    design: dict[str, float | str] = field(default_factory=dict)

    def copy(self) -> "SynthState":
        return SynthState(
            voice_name=self.voice_name,
            rate=self.rate,
            volume=self.volume,
            phoneme_mode=self.phoneme_mode,
            phoneme_silent=self.phoneme_silent,
            say_mode=self.say_mode,
            spell_mode=self.spell_mode,
            math_mode=self.math_mode,
            email_mode=self.email_mode,
            design=dict(self.design),
        )


@dataclass(frozen=True)
class SpeechSegment:
    text: str
    state: SynthState
    phonemes: bool = False


@dataclass(frozen=True)
class ToneSegment:
    frequencies: tuple[float, ...]
    duration_ms: int
    volume: int


@dataclass(frozen=True)
class PauseSegment:
    duration_ms: int


Segment = SpeechSegment | ToneSegment | PauseSegment


DTMF: dict[str, tuple[float, float]] = {
    "1": (697.0, 1209.0),
    "2": (697.0, 1336.0),
    "3": (697.0, 1477.0),
    "4": (770.0, 1209.0),
    "5": (770.0, 1336.0),
    "6": (770.0, 1477.0),
    "7": (852.0, 1209.0),
    "8": (852.0, 1336.0),
    "9": (852.0, 1477.0),
    "0": (941.0, 1336.0),
    "*": (941.0, 1209.0),
    "#": (941.0, 1477.0),
}


class DectalkParser:
    """Parser for DECtalk-style inline commands.

    Supported commands are intentionally small and practical: voice selection,
    rate, volume, tone, dial, phoneme mode, say/mode switches, and a subset of
    design-voice pitch controls.
    """

    def __init__(self, state: SynthState | None = None):
        self.state = state or SynthState()

    def parse(self, text: str, state: SynthState | None = None) -> list[Segment]:
        if state is not None:
            self.state = state

        segments: list[Segment] = []
        buffer: list[str] = []
        index = 0

        def flush(phonemes: bool = False) -> None:
            if not buffer:
                return
            chunk = "".join(buffer)
            buffer.clear()
            if chunk:
                segments.append(SpeechSegment(chunk, self.state.copy(), phonemes=phonemes))

        while index < len(text):
            if text.startswith("[:", index):
                close = text.find("]", index + 2)
                if close < 0:
                    buffer.append(text[index:])
                    break
                flush()
                command = text[index + 2 : close].strip()
                segments.extend(self._apply_command(command))
                index = close + 1
                continue

            if self.state.phoneme_mode and text[index] == "[":
                close = text.find("]", index + 1)
                if close < 0:
                    buffer.append(text[index:])
                    break
                flush()
                phoneme_text = text[index + 1 : close]
                if not self.state.phoneme_silent:
                    segments.append(SpeechSegment(phoneme_text, self.state.copy(), phonemes=True))
                index = close + 1
                continue

            buffer.append(text[index])
            index += 1

        flush()
        return segments

    def _apply_command(self, command: str) -> list[Segment]:
        events: list[Segment] = []
        if not command:
            return events

        raw_tokens = self._split_command(command)
        if not raw_tokens:
            return events

        index = 0
        while index < len(raw_tokens):
            token = raw_tokens[index].lstrip(":").lower()
            if not token:
                index += 1
                continue

            if token.startswith("n") and len(token) == 2:
                self._set_voice(token)
                index += 1
                continue

            if token == "name" and index + 1 < len(raw_tokens):
                self._set_voice(raw_tokens[index + 1])
                index += 2
                continue

            if token == "rate" and index + 1 < len(raw_tokens):
                self.state.rate = _clamp(_safe_int(raw_tokens[index + 1], self.state.rate), 75, 600)
                index += 2
                continue

            if token == "volume":
                index = self._apply_volume(raw_tokens, index + 1)
                continue

            if token == "tone":
                event, index = self._tone(raw_tokens, index + 1)
                if event:
                    events.append(event)
                continue

            if token == "dial":
                events.extend(self._dial(" ".join(raw_tokens[index + 1 :])))
                break

            if token == "phoneme":
                index = self._apply_phoneme(raw_tokens, index + 1)
                continue

            if token == "say" and index + 1 < len(raw_tokens):
                mode = raw_tokens[index + 1].lower()
                if mode in {"letter", "word", "clause"}:
                    self.state.say_mode = mode
                    self.state.spell_mode = mode == "letter"
                index += 2
                continue

            if token == "mode" and index + 2 < len(raw_tokens):
                self._apply_mode(raw_tokens[index + 1], raw_tokens[index + 2])
                index += 3
                continue

            if token == "dv":
                index = self._apply_design_voice(raw_tokens, index + 1)
                continue

            index += 1
        return events

    def _split_command(self, command: str) -> list[str]:
        try:
            return shlex.split(command)
        except ValueError:
            return re.findall(r'"[^"]*"|\S+', command)

    def _set_voice(self, name: str) -> None:
        try:
            self.state.voice_name = resolve_voice(name)
        except ValueError:
            return

    def _apply_volume(self, tokens: list[str], index: int) -> int:
        if index >= len(tokens):
            return index
        action = tokens[index].lower()
        if action == "set" and index + 1 < len(tokens):
            self.state.volume = _clamp(_safe_int(tokens[index + 1], self.state.volume), 0, 100)
            return index + 2
        if action == "up" and index + 1 < len(tokens):
            self.state.volume = _clamp(self.state.volume + _safe_int(tokens[index + 1], 0), 0, 100)
            return index + 2
        if action == "down" and index + 1 < len(tokens):
            self.state.volume = _clamp(self.state.volume - _safe_int(tokens[index + 1], 0), 0, 100)
            return index + 2
        if action.isdigit():
            self.state.volume = _clamp(_safe_int(action, self.state.volume), 0, 100)
            return index + 1
        return index + 1

    def _tone(self, tokens: list[str], index: int) -> tuple[ToneSegment | None, int]:
        if index >= len(tokens):
            return None, index
        first = tokens[index].strip()
        comma_parts = [part for part in re.split(r",+", first) if part]
        frequency = max(20, _safe_int(comma_parts[0] if comma_parts else first, 440))
        duration = 250
        next_index = index + 1
        if len(comma_parts) > 1:
            duration = _clamp(_safe_int(comma_parts[1], duration), 10, 10000)
        elif next_index < len(tokens):
            duration = _clamp(_safe_int(tokens[next_index].strip(","), duration), 10, 10000)
            next_index += 1
        return ToneSegment((float(frequency),), duration, self.state.volume), next_index

    def _dial(self, dial_string: str) -> list[Segment]:
        text = dial_string.strip().strip('"')
        events: list[Segment] = []
        for char in text:
            if char in DTMF:
                events.append(ToneSegment(DTMF[char], 85, self.state.volume))
                events.append(PauseSegment(45))
            elif char in {",", ";"}:
                events.append(PauseSegment(300))
            elif char in {"-", " ", "(", ")"}:
                events.append(PauseSegment(70))
        return events

    def _apply_phoneme(self, tokens: list[str], index: int) -> int:
        trailing = [token.lower() for token in tokens[index:]]
        if not trailing:
            self.state.phoneme_mode = True
            return index
        if "silent" in trailing:
            silent_index = trailing.index("silent")
            if silent_index + 1 < len(trailing):
                self.state.phoneme_silent = trailing[silent_index + 1] == "on"
            return len(tokens)
        if "off" in trailing:
            self.state.phoneme_mode = False
            self.state.phoneme_silent = False
            return len(tokens)
        if "on" in trailing:
            self.state.phoneme_mode = True
            return len(tokens)
        return len(tokens)

    def _apply_mode(self, name: str, value: str) -> None:
        enabled = value.lower() == "on"
        mode = name.lower()
        if mode == "spell":
            self.state.spell_mode = enabled
            self.state.say_mode = "letter" if enabled else "clause"
        elif mode == "math":
            self.state.math_mode = enabled
        elif mode == "email":
            self.state.email_mode = enabled

    def _apply_design_voice(self, tokens: list[str], index: int) -> int:
        while index < len(tokens):
            key = tokens[index].lower()
            if key == "save":
                self.state.design["save"] = "1"
                index += 1
                continue
            if key in {"ap", "average", "pitch"} and index + 1 < len(tokens):
                self.state.design["average_pitch"] = float(_safe_int(tokens[index + 1], 0))
                index += 2
                continue
            if key in {"pr", "range"} and index + 1 < len(tokens):
                self.state.design["pitch_range"] = float(_safe_int(tokens[index + 1], 0))
                index += 2
                continue
            if key in {"sx", "sex"} and index + 1 < len(tokens):
                self.state.design["sex"] = tokens[index + 1].lower()
                index += 2
                continue
            if key in {"br", "breathiness"} and index + 1 < len(tokens):
                self.state.design["breath"] = float(_safe_int(tokens[index + 1], 0)) / 100.0
                index += 2
                continue
            break
        return index


def _safe_int(value: str, default: int) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default
