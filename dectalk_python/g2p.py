from __future__ import annotations

from dataclasses import dataclass
import re

from .parser import SynthState


@dataclass(frozen=True)
class Phone:
    symbol: str
    stress: float = 1.0
    duration_ms: int | None = None


VOWELS = {
    "AA",
    "AE",
    "AH",
    "AO",
    "AW",
    "AY",
    "EH",
    "ER",
    "EY",
    "IH",
    "IY",
    "OW",
    "OY",
    "UH",
    "UW",
    "AX",
}


LETTER_NAMES: dict[str, list[str]] = {
    "a": ["EY"],
    "b": ["B", "IY"],
    "c": ["S", "IY"],
    "d": ["D", "IY"],
    "e": ["IY"],
    "f": ["EH", "F"],
    "g": ["JH", "IY"],
    "h": ["EY", "CH"],
    "i": ["AY"],
    "j": ["JH", "EY"],
    "k": ["K", "EY"],
    "l": ["EH", "L"],
    "m": ["EH", "M"],
    "n": ["EH", "N"],
    "o": ["OW"],
    "p": ["P", "IY"],
    "q": ["K", "Y", "UW"],
    "r": ["AA", "R"],
    "s": ["EH", "S"],
    "t": ["T", "IY"],
    "u": ["Y", "UW"],
    "v": ["V", "IY"],
    "w": ["D", "AH", "B", "AH", "L", "Y", "UW"],
    "x": ["EH", "K", "S"],
    "y": ["W", "AY"],
    "z": ["Z", "IY"],
}


COMMON_WORDS: dict[str, list[str]] = {
    "a": ["AX"],
    "an": ["AE", "N"],
    "and": ["AE", "N", "D"],
    "are": ["AA", "R"],
    "as": ["AE", "Z"],
    "be": ["B", "IY"],
    "dectalk": ["D", "EH", "K", "T", "AO", "K"],
    "for": ["F", "AO", "R"],
    "hello": ["HH", "EH", "L", "OW"],
    "i": ["AY"],
    "is": ["IH", "Z"],
    "of": ["AH", "V"],
    "python": ["P", "AY", "TH", "AA", "N"],
    "speech": ["S", "P", "IY", "CH"],
    "talk": ["T", "AO", "K"],
    "test": ["T", "EH", "S", "T"],
    "the": ["DH", "AX"],
    "this": ["DH", "IH", "S"],
    "to": ["T", "UW"],
    "voice": ["V", "OY", "S"],
    "you": ["Y", "UW"],
}


TOKEN_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+|[^\w\s]|\s+", re.ASCII)


def text_to_phones(
    text: str,
    state: SynthState | None = None,
    dictionary: dict[str, list[Phone]] | None = None,
) -> list[Phone]:
    state = state or SynthState()
    dictionary = dictionary or {}
    phones: list[Phone] = []
    for match in TOKEN_RE.finditer(text):
        token = match.group(0)
        if token.isspace():
            if "\n" in token:
                phones.append(Phone("SIL", duration_ms=120))
            continue
        if token.isdigit():
            for word in number_to_words(int(token)):
                phones.extend(_word_to_phone_objects(word, state, dictionary))
                phones.append(Phone("SIL", duration_ms=25))
            continue
        if token.isalpha() or "'" in token:
            phones.extend(_word_to_phone_objects(token, state, dictionary))
            phones.append(Phone("SIL", duration_ms=28))
            continue
        phones.extend(punctuation_to_phones(token, state))
    return _trim_trailing_pause(phones)


def arpabet_to_phones(text: str) -> list[Phone]:
    cleaned = text.replace("[", " ").replace("]", " ")
    phones: list[Phone] = []
    for raw in re.findall(r"_<\d+>|[A-Za-z#']+|\S", cleaned):
        token = raw.strip().lower()
        if not token:
            continue
        if token.startswith("_<") and token.endswith(">"):
            phones.append(Phone("SIL", duration_ms=int(token[2:-1])))
            continue
        stress = 1.0
        token = token.replace("'", "")
        if token.endswith("#"):
            stress = 1.15
            token = token[:-1]
        symbol = ARPABET.get(token)
        if symbol:
            phones.append(Phone(symbol, stress=stress))
    return phones


def phones_to_symbols(phones: list[Phone]) -> list[str]:
    out: list[str] = []
    for phone in phones:
        if phone.symbol == "SIL":
            out.append(f"_{phone.duration_ms or 0}")
        else:
            out.append(phone.symbol)
    return out


def syllables_from_phones(phones: list[Phone]) -> list[str]:
    syllables: list[list[str]] = []
    current: list[str] = []
    for phone in phones:
        if phone.symbol == "SIL":
            if current:
                syllables.append(current)
                current = []
            continue
        current.append(phone.symbol)
        if phone.symbol in VOWELS and current:
            syllables.append(current)
            current = []
    if current:
        syllables.append(current)
    return ["-".join(syllable) for syllable in syllables]


def _word_to_phone_objects(
    word: str,
    state: SynthState,
    dictionary: dict[str, list[Phone]],
) -> list[Phone]:
    cleaned = re.sub(r"[^A-Za-z']", "", word).lower()
    if not cleaned:
        return []
    if cleaned in dictionary:
        return list(dictionary[cleaned])
    if state.spell_mode or state.say_mode == "letter":
        out: list[Phone] = []
        for char in cleaned:
            out.extend(Phone(symbol) for symbol in LETTER_NAMES.get(char, []))
            out.append(Phone("SIL", duration_ms=35))
        return out
    return [Phone(symbol) for symbol in word_to_phones(cleaned)]


def punctuation_to_phones(token: str, state: SynthState) -> list[Phone]:
    if token in {".", "!", "?"}:
        return [Phone("SIL", duration_ms=180)]
    if token in {",", ";", ":"}:
        return [Phone("SIL", duration_ms=105)]
    if token in {"-", "/", "\\"}:
        return [Phone("SIL", duration_ms=65)]
    if state.math_mode:
        words = {
            "+": "plus",
            "*": "times",
            "=": "equals",
            "<": "less",
            ">": "greater",
        }.get(token)
        if words:
            return text_to_phones(words, state)
    return [Phone("SIL", duration_ms=25)]


def word_to_phones(word: str) -> list[str]:
    if word in COMMON_WORDS:
        return list(COMMON_WORDS[word])

    letters = word.lower()
    phones: list[str] = []
    index = 0
    while index < len(letters):
        tail = letters[index:]

        if tail.startswith("'"):
            index += 1
            continue
        if index == len(letters) - 1 and letters[index] == "e" and len(letters) > 2:
            break

        matched = False
        for text, symbols in DIGRAPHS:
            if tail.startswith(text):
                phones.extend(symbols)
                index += len(text)
                matched = True
                break
        if matched:
            continue

        char = letters[index]
        next_char = letters[index + 1] if index + 1 < len(letters) else ""
        prev_char = letters[index - 1] if index > 0 else ""
        if char in SINGLE_CONSONANTS:
            if char == "c" and next_char in {"e", "i", "y"}:
                phones.append("S")
            elif char == "g" and next_char in {"e", "i", "y"}:
                phones.append("JH")
            elif char == "x":
                phones.extend(["K", "S"])
            else:
                phones.extend(SINGLE_CONSONANTS[char])
        elif char in VOWEL_LETTERS:
            phones.extend(vowel_sound(char, next_char, prev_char, index, len(letters)))
        index += 1
    if not any(phone in VOWELS for phone in phones):
        phones.append("AX")
    return phones


def vowel_sound(char: str, next_char: str, prev_char: str, index: int, length: int) -> list[str]:
    finalish = index >= length - 2
    if char == "a":
        return ["EY"] if finalish and next_char == "e" else ["AE"]
    if char == "e":
        return ["IY"] if finalish else ["EH"]
    if char == "i":
        return ["AY"] if finalish else ["IH"]
    if char == "o":
        return ["OW"] if finalish else ["AA"]
    if char == "u":
        return ["UW"] if prev_char in {"r", "l", "j"} else ["AH"]
    if char == "y":
        return ["IY"] if finalish else ["AY"]
    return ["AX"]


def number_to_words(value: int) -> list[str]:
    if value == 0:
        return ["zero"]
    if value < 0:
        return ["minus", *number_to_words(abs(value))]
    if value >= 1_000_000:
        return number_to_words(value // 1_000_000) + ["million"] + number_to_words(value % 1_000_000)
    if value >= 1000:
        remainder = value % 1000
        result = number_to_words(value // 1000) + ["thousand"]
        if remainder:
            result.extend(number_to_words(remainder))
        return result
    if value >= 100:
        remainder = value % 100
        result = [ONES[value // 100], "hundred"]
        if remainder:
            result.extend(number_to_words(remainder))
        return result
    if value >= 20:
        remainder = value % 10
        result = [TENS[value // 10]]
        if remainder:
            result.append(ONES[remainder])
        return result
    return [ONES[value]]


def _trim_trailing_pause(phones: list[Phone]) -> list[Phone]:
    while phones and phones[-1].symbol == "SIL":
        phones.pop()
    return phones


DIGRAPHS: list[tuple[str, list[str]]] = [
    ("tion", ["SH", "AX", "N"]),
    ("sion", ["ZH", "AX", "N"]),
    ("ough", ["AO"]),
    ("eigh", ["EY"]),
    ("ph", ["F"]),
    ("th", ["TH"]),
    ("sh", ["SH"]),
    ("ch", ["CH"]),
    ("ng", ["NG"]),
    ("wh", ["W"]),
    ("ck", ["K"]),
    ("qu", ["K", "W"]),
    ("ee", ["IY"]),
    ("ea", ["IY"]),
    ("oo", ["UW"]),
    ("ai", ["EY"]),
    ("ay", ["EY"]),
    ("ei", ["EY"]),
    ("ie", ["IY"]),
    ("oa", ["OW"]),
    ("ow", ["AW"]),
    ("ou", ["AW"]),
    ("oi", ["OY"]),
    ("oy", ["OY"]),
    ("ar", ["AA", "R"]),
    ("er", ["ER"]),
    ("ir", ["ER"]),
    ("ur", ["ER"]),
    ("or", ["AO", "R"]),
]

SINGLE_CONSONANTS: dict[str, list[str]] = {
    "b": ["B"],
    "c": ["K"],
    "d": ["D"],
    "f": ["F"],
    "g": ["G"],
    "h": ["HH"],
    "j": ["JH"],
    "k": ["K"],
    "l": ["L"],
    "m": ["M"],
    "n": ["N"],
    "p": ["P"],
    "q": ["K"],
    "r": ["R"],
    "s": ["S"],
    "t": ["T"],
    "v": ["V"],
    "w": ["W"],
    "x": ["K", "S"],
    "z": ["Z"],
}

VOWEL_LETTERS = set("aeiouy")

ARPABET: dict[str, str] = {
    "aa": "AA",
    "ae": "AE",
    "ah": "AH",
    "ao": "AO",
    "aw": "AW",
    "ay": "AY",
    "ax": "AX",
    "eh": "EH",
    "er": "ER",
    "ey": "EY",
    "ih": "IH",
    "iy": "IY",
    "ix": "IH",
    "ow": "OW",
    "oy": "OY",
    "uh": "UH",
    "uw": "UW",
    "b": "B",
    "ch": "CH",
    "d": "D",
    "dh": "DH",
    "f": "F",
    "g": "G",
    "hh": "HH",
    "h": "HH",
    "jh": "JH",
    "k": "K",
    "l": "L",
    "m": "M",
    "n": "N",
    "nx": "NG",
    "ng": "NG",
    "p": "P",
    "r": "R",
    "s": "S",
    "sh": "SH",
    "t": "T",
    "th": "TH",
    "v": "V",
    "w": "W",
    "y": "Y",
    "z": "Z",
    "zh": "ZH",
}

ONES = [
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
]
TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

