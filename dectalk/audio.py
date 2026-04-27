from __future__ import annotations

from array import array
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
import io
import wave


MAX_I16 = 32767
MIN_I16 = -32768


def clamp_i16(value: float) -> int:
    if value > MAX_I16:
        return MAX_I16
    if value < MIN_I16:
        return MIN_I16
    return int(value)


@dataclass
class AudioBuffer:
    sample_rate: int = 11025
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

    @classmethod
    def from_wav_bytes(cls, data: bytes) -> "AudioBuffer":
        with wave.open(io.BytesIO(data), "rb") as wav:
            channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            sample_rate = wav.getframerate()
            frames = wav.readframes(wav.getnframes())
        if channels != 1:
            raise ValueError(f"expected mono WAV, got {channels} channels")
        if sample_width != 2:
            raise ValueError(f"expected 16-bit PCM WAV, got {sample_width * 8}-bit samples")
        samples = array("h")
        samples.frombytes(frames)
        if samples.itemsize != 2:
            raise ValueError("native 16-bit array type is unavailable")
        return cls(sample_rate, samples)

    @classmethod
    def read_wav(cls, path: str | Path) -> "AudioBuffer":
        return cls.from_wav_bytes(Path(path).read_bytes())
