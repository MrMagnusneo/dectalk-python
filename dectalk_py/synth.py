from __future__ import annotations

from array import array
from dataclasses import replace
import math
import random

from .audio import AudioBuffer, MAX_I16, clamp_i16, fade_value, sine_samples
from .g2p import Phone, VOWELS, arpabet_to_phones, text_to_phones
from .parser import PauseSegment, Segment, SpeechSegment, SynthState, ToneSegment
from .voices import VoiceProfile, get_voice


VOWEL_FORMANTS: dict[str, tuple[float, float, float]] = {
    "IY": (300, 2300, 3000),
    "IH": (390, 1990, 2550),
    "EH": (530, 1850, 2500),
    "AE": (660, 1720, 2410),
    "AA": (730, 1090, 2440),
    "AO": (570, 840, 2410),
    "AH": (640, 1190, 2390),
    "AX": (500, 1500, 2500),
    "ER": (490, 1350, 1690),
    "EY": (420, 2100, 2600),
    "AY": (620, 1200, 2550),
    "OW": (500, 900, 2600),
    "AW": (700, 1100, 2500),
    "OY": (570, 1600, 2500),
    "UH": (440, 1020, 2240),
    "UW": (350, 900, 2200),
}

FRICATIVES = {"F", "S", "SH", "TH", "HH"}
VOICED_FRICATIVES = {"V", "Z", "ZH", "DH"}
STOPS = {"P", "T", "K", "B", "D", "G", "CH", "JH"}
NASALS = {"M", "N", "NG"}
LIQUIDS = {"L", "R", "W", "Y"}


class DectalkSynthesizer:
    """Small formant/noise synthesizer with DECtalk-like controls."""

    def __init__(self, sample_rate: int = 22050, seed: int = 42):
        self.sample_rate = sample_rate
        self.random = random.Random(seed)
        self._phone_index = 0

    def synthesize(
        self,
        text: str,
        state: SynthState | None = None,
        dictionary: dict[str, list[Phone]] | None = None,
    ) -> AudioBuffer:
        from .parser import DectalkParser

        parser = DectalkParser(state or SynthState())
        return self.render(parser.parse(text), dictionary=dictionary)

    def render(
        self,
        segments: list[Segment],
        dictionary: dict[str, list[Phone]] | None = None,
    ) -> AudioBuffer:
        out = AudioBuffer(self.sample_rate)
        for segment in segments:
            if isinstance(segment, SpeechSegment):
                phones = (
                    arpabet_to_phones(segment.text)
                    if segment.phonemes
                    else text_to_phones(segment.text, segment.state, dictionary)
                )
                self._render_phones(out, phones, segment.state)
            elif isinstance(segment, ToneSegment):
                amp = (segment.volume / 99.0) * 0.48
                out.extend(sine_samples(segment.frequencies, segment.duration_ms, self.sample_rate, amp))
            elif isinstance(segment, PauseSegment):
                out.add_silence(segment.duration_ms)
        return out.normalize()

    def _render_phones(self, out: AudioBuffer, phones: list[Phone], state: SynthState) -> None:
        voice = self._voice_for_state(state)
        for phone in phones:
            symbol = phone.symbol
            if symbol == "SIL":
                out.add_silence(self._pause_duration(phone, state, voice))
            elif symbol in VOWELS:
                out.extend(self._vowel(symbol, phone, state, voice))
            elif symbol in FRICATIVES or symbol in VOICED_FRICATIVES:
                out.extend(self._fricative(symbol, phone, state, voice))
            elif symbol in STOPS:
                out.extend(self._stop(symbol, phone, state, voice))
            elif symbol in NASALS:
                out.extend(self._nasal(symbol, phone, state, voice))
            elif symbol in LIQUIDS:
                out.extend(self._liquid(symbol, phone, state, voice))
            self._phone_index += 1

    def _voice_for_state(self, state: SynthState) -> VoiceProfile:
        voice = get_voice(state.voice_name)
        design = state.design
        pitch = voice.base_pitch
        pitch_range = voice.pitch_range
        breath = voice.breath
        formant_scale = voice.formant_scale

        if "average_pitch" in design and float(design["average_pitch"]) > 0:
            pitch = float(design["average_pitch"])
        if "pitch_range" in design and float(design["pitch_range"]) >= 0:
            pitch_range = float(design["pitch_range"])
        if "breath" in design:
            breath = min(0.45, max(0.0, float(design["breath"])))
        if design.get("sex") == "f":
            pitch *= 1.35
            formant_scale *= 1.12
        elif design.get("sex") == "m":
            pitch *= 0.82
            formant_scale *= 0.94

        return replace(voice, base_pitch=pitch, pitch_range=pitch_range, breath=breath, formant_scale=formant_scale)

    def _duration_scale(self, state: SynthState, voice: VoiceProfile) -> float:
        rate_scale = 200.0 / max(75.0, min(600.0, float(state.rate)))
        return max(0.28, min(2.2, rate_scale / voice.speed))

    def _volume(self, state: SynthState, voice: VoiceProfile) -> float:
        return (state.volume / 99.0) * voice.amplitude

    def _pause_duration(self, phone: Phone, state: SynthState, voice: VoiceProfile) -> float:
        base = phone.duration_ms if phone.duration_ms is not None else 80
        return max(10.0, base * min(1.35, self._duration_scale(state, voice)))

    def _base_duration(self, symbol: str, state: SynthState, voice: VoiceProfile) -> int:
        scale = self._duration_scale(state, voice)
        if symbol in VOWELS:
            base = 92
        elif symbol in FRICATIVES or symbol in VOICED_FRICATIVES:
            base = 62
        elif symbol in NASALS or symbol in LIQUIDS:
            base = 72
        else:
            base = 48
        return int(max(18, base * scale))

    def _pitch(self, phone: Phone, state: SynthState, voice: VoiceProfile) -> float:
        wobble = math.sin(self._phone_index * 0.73) * voice.pitch_range * 0.18
        stress = (phone.stress - 1.0) * voice.pitch_range
        return max(55.0, voice.base_pitch + wobble + stress)

    def _vowel(self, symbol: str, phone: Phone, state: SynthState, voice: VoiceProfile) -> array:
        duration = self._base_duration(symbol, state, voice)
        count = max(1, int(self.sample_rate * duration / 1000.0))
        fade = max(1, int(self.sample_rate * 0.012))
        f0 = self._pitch(phone, state, voice)
        f1, f2, f3 = (freq * voice.formant_scale for freq in VOWEL_FORMANTS[symbol])
        volume = self._volume(state, voice)
        breath = voice.breath + (0.18 if voice.whisper else 0.0)
        out = array("h")
        phase_jitter = self.random.random() * math.pi

        for index in range(count):
            t = index / self.sample_rate
            env = fade_value(index, count, fade)
            contour = 1.0 + 0.006 * math.sin(2.0 * math.pi * 5.1 * t)
            voiced = 0.0
            if not voice.whisper:
                voiced += 0.58 * math.sin(2.0 * math.pi * f0 * contour * t)
                voiced += 0.22 * math.sin(2.0 * math.pi * min(f1, self.sample_rate / 2 - 100) * t)
                voiced += 0.15 * math.sin(2.0 * math.pi * min(f2, self.sample_rate / 2 - 100) * t + 0.4)
                voiced += 0.08 * math.sin(2.0 * math.pi * min(f3, self.sample_rate / 2 - 100) * t + phase_jitter)
            hiss = self.random.uniform(-1.0, 1.0) * breath
            rough = voice.roughness * math.sin(2.0 * math.pi * (f0 * 0.52) * t)
            out.append(clamp_i16((voiced + hiss + rough) * volume * MAX_I16 * 0.36 * env))
        return out

    def _fricative(self, symbol: str, phone: Phone, state: SynthState, voice: VoiceProfile) -> array:
        duration = self._base_duration(symbol, state, voice)
        count = max(1, int(self.sample_rate * duration / 1000.0))
        fade = max(1, int(self.sample_rate * 0.006))
        volume = self._volume(state, voice)
        out = array("h")
        voiced = symbol in VOICED_FRICATIVES
        f0 = self._pitch(phone, state, voice)
        last = 0.0
        for index in range(count):
            t = index / self.sample_rate
            noise = self.random.uniform(-1.0, 1.0)
            high = noise - last * 0.55
            last = noise
            tone = 0.28 * math.sin(2.0 * math.pi * f0 * t) if voiced and not voice.whisper else 0.0
            if symbol in {"SH", "ZH", "CH", "JH"}:
                high *= 0.72
            env = fade_value(index, count, fade)
            out.append(clamp_i16((high * 0.62 + tone) * volume * MAX_I16 * 0.34 * env))
        return out

    def _stop(self, symbol: str, phone: Phone, state: SynthState, voice: VoiceProfile) -> array:
        duration = self._base_duration(symbol, state, voice)
        silence_ms = duration * (0.34 if symbol in {"P", "T", "K"} else 0.22)
        burst_ms = max(18, duration - silence_ms)
        out = array("h", [0] * int(self.sample_rate * silence_ms / 1000.0))
        burst_symbol = "SH" if symbol in {"CH", "JH"} else "S"
        out.extend(self._fricative(burst_symbol, phone, state, voice)[: int(self.sample_rate * burst_ms / 1000.0)])
        if symbol in {"B", "D", "G", "JH"} and not voice.whisper:
            out.extend(sine_samples(self._pitch(phone, state, voice) * 0.75, 16, self.sample_rate, self._volume(state, voice) * 0.16))
        return out

    def _nasal(self, symbol: str, phone: Phone, state: SynthState, voice: VoiceProfile) -> array:
        duration = self._base_duration(symbol, state, voice)
        count = max(1, int(self.sample_rate * duration / 1000.0))
        fade = max(1, int(self.sample_rate * 0.010))
        f0 = self._pitch(phone, state, voice)
        nasal = {"M": 260.0, "N": 320.0, "NG": 420.0}[symbol] * voice.formant_scale
        volume = self._volume(state, voice)
        out = array("h")
        for index in range(count):
            t = index / self.sample_rate
            env = fade_value(index, count, fade)
            value = 0.62 * math.sin(2.0 * math.pi * f0 * t) + 0.22 * math.sin(2.0 * math.pi * nasal * t)
            value += self.random.uniform(-1.0, 1.0) * voice.breath * 0.45
            out.append(clamp_i16(value * volume * MAX_I16 * 0.27 * env))
        return out

    def _liquid(self, symbol: str, phone: Phone, state: SynthState, voice: VoiceProfile) -> array:
        duration = self._base_duration(symbol, state, voice)
        count = max(1, int(self.sample_rate * duration / 1000.0))
        fade = max(1, int(self.sample_rate * 0.010))
        f0 = self._pitch(phone, state, voice)
        resonance = {"L": 900.0, "R": 1250.0, "W": 620.0, "Y": 2100.0}[symbol] * voice.formant_scale
        volume = self._volume(state, voice)
        out = array("h")
        for index in range(count):
            t = index / self.sample_rate
            env = fade_value(index, count, fade)
            value = 0.48 * math.sin(2.0 * math.pi * f0 * t)
            value += 0.22 * math.sin(2.0 * math.pi * min(resonance, self.sample_rate / 2 - 100) * t)
            value += self.random.uniform(-1.0, 1.0) * voice.breath * 0.35
            out.append(clamp_i16(value * volume * MAX_I16 * 0.30 * env))
        return out

