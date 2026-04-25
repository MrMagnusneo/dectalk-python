from __future__ import annotations

from array import array
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
import io
import math
import wave


MAX_I16 = 32767
MIN_I16 = -32768


def clamp_i16(value: float) -> int:
    if value > MAX_I16:
        return MAX_I16
    if value < MIN_I16:
        return MIN_I16
    return int(value)


def fade_value(index: int, total: int, fade: int) -> float:
    if fade <= 0 or total <= 0:
        return 1.0
    if index < fade:
        return index / fade
    if index >= total - fade:
        return max(0.0, (total - index - 1) / fade)
    return 1.0


@dataclass
class AudioBuffer:
    sample_rate: int = 22050
    samples: array = field(default_factory=lambda: array("h"))

    def __len__(self) -> int:
        return len(self.samples)

    @property
    def duration_seconds(self) -> float:
        return len(self.samples) / self.sample_rate

    def append(self, sample: int) -> None:
        self.samples.append(clamp_i16(sample))

    def extend(self, samples: Iterable[int]) -> None:
        self.samples.extend(clamp_i16(sample) for sample in samples)

    def add_silence(self, duration_ms: float) -> None:
        count = max(0, int(self.sample_rate * duration_ms / 1000.0))
        if count:
            self.samples.extend([0] * count)

    def normalize(self, peak: float = 0.92) -> "AudioBuffer":
        if not self.samples:
            return self
        current = max(abs(value) for value in self.samples)
        target = int(MAX_I16 * peak)
        if current <= 0 or current <= target:
            return self
        scale = target / current
        self.samples = array("h", (clamp_i16(value * scale) for value in self.samples))
        return self

    def to_wav_bytes(self) -> bytes:
        out = io.BytesIO()
        with wave.open(out, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(self.sample_rate)
            wav.writeframes(self.samples.tobytes())
        return out.getvalue()

    def write_wav(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(self.to_wav_bytes())
        return target

    def copy(self) -> "AudioBuffer":
        return AudioBuffer(self.sample_rate, array("h", self.samples))


def sine_samples(
    frequencies: float | Iterable[float],
    duration_ms: float,
    sample_rate: int,
    amplitude: float = 0.45,
    fade_ms: float = 6.0,
) -> array:
    if isinstance(frequencies, (int, float)):
        freqs = [float(frequencies)]
    else:
        freqs = [float(freq) for freq in frequencies]
    count = max(0, int(sample_rate * duration_ms / 1000.0))
    fade = int(sample_rate * fade_ms / 1000.0)
    out = array("h")
    if not freqs or count == 0:
        return out
    gain = amplitude * MAX_I16 / len(freqs)
    for index in range(count):
        t = index / sample_rate
        env = fade_value(index, count, fade)
        value = 0.0
        for freq in freqs:
            value += math.sin(2.0 * math.pi * freq * t)
        out.append(clamp_i16(value * gain * env))
    return out

