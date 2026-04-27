from pathlib import Path
import os
import subprocess
import tempfile
import unittest
import wave

from dectalk import DectalkParser, TextToSpeech
from dectalk.native import native_bundle_dir
from dectalk.parser import SpeechSegment, ToneSegment


class ParserTests(unittest.TestCase):
    def test_inline_rate_voice_and_tone(self):
        parser = DectalkParser()
        segments = parser.parse("[:nb][:rate 120]Hi [:tone 500,100]there")
        speech = [segment for segment in segments if isinstance(segment, SpeechSegment)]
        tones = [segment for segment in segments if isinstance(segment, ToneSegment)]
        self.assertEqual(speech[0].state.voice_name, "betty")
        self.assertEqual(speech[0].state.rate, 120)
        self.assertEqual(tones[0].frequencies, (500.0,))
        self.assertEqual(tones[0].duration_ms, 100)

    def test_phoneme_mode(self):
        parser = DectalkParser()
        segments = parser.parse("[:phoneme arpabet speak on][dh ih s]")
        self.assertEqual(len(segments), 1)
        self.assertTrue(segments[0].phonemes)


class NativeSynthTests(unittest.TestCase):
    def test_wav_output(self):
        engine = TextToSpeech()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "out.wav"
            engine.open_wave_out_file(path)
            engine.speak("[:np] hello from python")
            engine.close_wave_out_file()
            self.assertGreater(path.stat().st_size, 44)
            with wave.open(str(path), "rb") as wav:
                self.assertEqual(wav.getnchannels(), 1)
                self.assertEqual(wav.getsampwidth(), 2)
                self.assertEqual(wav.getframerate(), 11025)
                self.assertGreater(wav.getnframes(), 1000)

    def test_direct_native_synth_matches_original_say(self):
        engine = TextToSpeech()
        audio = engine.synthesize("[:np] Hello, world!")
        self.assertEqual(audio.sample_rate, 11025)
        self.assertGreater(len(audio.samples), 1000)

        bundle = native_bundle_dir()
        say = bundle / "say"
        if not say.exists():
            self.skipTest("native say executable is not bundled")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "say.wav"
            subprocess.run(
                [str(say), "-e", "1", "-fo", str(path), "-a", "[:np] Hello, world!"],
                cwd=bundle,
                env={**os.environ, "LD_LIBRARY_PATH": str(bundle)},
                check=True,
            )
            self.assertEqual(audio.to_wav_bytes(), path.read_bytes())


if __name__ == "__main__":
    unittest.main()
