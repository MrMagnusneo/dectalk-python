from pathlib import Path
import tempfile
import unittest
import wave

from dectalk_py import DectalkParser, DectalkSynthesizer, TextToSpeech
from dectalk_py.g2p import arpabet_to_phones, text_to_phones
from dectalk_py.parser import SpeechSegment, ToneSegment


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


class G2PTests(unittest.TestCase):
    def test_text_to_phones(self):
        symbols = [phone.symbol for phone in text_to_phones("hello DECtalk")]
        self.assertIn("HH", symbols)
        self.assertIn("AO", symbols)

    def test_arpabet_pause(self):
        phones = arpabet_to_phones("dh ih s _<200>")
        self.assertEqual(phones[-1].symbol, "SIL")
        self.assertEqual(phones[-1].duration_ms, 200)


class SynthTests(unittest.TestCase):
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
                self.assertGreater(wav.getnframes(), 1000)

    def test_direct_synth(self):
        synth = DectalkSynthesizer(sample_rate=11025)
        audio = synth.synthesize("[:rate 300]test")
        self.assertEqual(audio.sample_rate, 11025)
        self.assertGreater(len(audio.samples), 500)


if __name__ == "__main__":
    unittest.main()

