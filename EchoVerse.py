import logging
import datetime
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import speech_recognition as sr
from textblob import TextBlob

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ── Constants ─────────────────────────────────────────────────────────────────
POSITIVE_THRESHOLD = 0.2      # polarity above this  → Positive
NEGATIVE_THRESHOLD = -0.2     # polarity below this  → Negative
MAX_KEYWORDS = 4              # max noun phrases shown in reflection
JOURNAL_DIR = Path.home() / "voice_journal"   # ~/voice_journal/
AUDIO_TIMEOUT = 10            # seconds to wait for speech to start
AUDIO_PHRASE_LIMIT = 30       # max seconds of speech per entry


# ── Data model ────────────────────────────────────────────────────────────────
@dataclass
class JournalEntry:
    """A single voice journal entry with all derived fields."""
    timestamp: datetime.datetime
    raw_text: str
    polarity: float
    mood: str
    keywords: list[str]
    reflection: str

    @property
    def date_str(self) -> str:
        return self.timestamp.strftime("%Y-%m-%d %H:%M")

    @property
    def filename(self) -> Path:
        day = self.timestamp.strftime("%Y%m%d")
        return JOURNAL_DIR / f"journal_{day}.txt"

    def as_text(self) -> str:
        kw = ", ".join(self.keywords) if self.keywords else "nothing specific"
        return (
            f"\n{'─' * 48}\n"
            f"[{self.date_str}]\n"
            f"Entry     : {self.raw_text}\n"
            f"Mood      : {self.mood}  (polarity: {self.polarity:+.3f})\n"
            f"Keywords  : {kw}\n"
            f"Reflection: {self.reflection}\n"
        )


# ── Audio capture ─────────────────────────────────────────────────────────────
def listen(
    timeout: int = AUDIO_TIMEOUT,
    phrase_limit: int = AUDIO_PHRASE_LIMIT,
) -> Optional[str]:
    """
    Capture one spoken phrase from the microphone and return transcribed text.

    Returns None on any audio or recognition failure so the caller can decide
    whether to retry or exit.

    Parameters
    ----------
    timeout      : seconds to wait for speech to begin
    phrase_limit : maximum seconds of speech captured per call
    """
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            log.info("Calibrating for ambient noise — please wait…")
            # Adjusts the energy threshold to current background noise
            recognizer.adjust_for_ambient_noise(source, duration=1)

            print("\n🎙️  Speak now…  (Ctrl+C to stop)\n")
            audio = recognizer.listen(
                source,
                timeout=phrase_limit,
                phrase_time_limit=phrase_limit,
            )

        text = recognizer.recognize_google(audio)
        log.info("Transcription successful.")
        return text

    except sr.WaitTimeoutError:
        log.warning("No speech detected within %s seconds.", timeout)
    except sr.UnknownValueError:
        log.warning("Speech was detected but could not be understood.")
    except sr.RequestError as exc:
        log.error("Google Speech API error: %s", exc)

    return None


# ── Analysis ──────────────────────────────────────────────────────────────────
def analyze(text: str) -> tuple[float, str, list[str]]:
    """
    Run sentiment analysis and keyword extraction on transcribed text.

    Returns
    -------
    polarity : float in [-1.0, 1.0]
    mood     : 'Positive' | 'Neutral' | 'Negative'
    keywords : deduplicated list of noun phrases (lowercased)
    """
    blob = TextBlob(text)
    polarity: float = blob.sentiment.polarity

    if polarity > POSITIVE_THRESHOLD:
        mood = "Positive"
    elif polarity < NEGATIVE_THRESHOLD:
        mood = "Negative"
    else:
        mood = "Neutral"

    # Deduplicate while preserving order (set() loses order in older Pythons)
    seen: set[str] = set()
    keywords: list[str] = []
    for phrase in blob.noun_phrases:
        phrase_lower = phrase.lower()
        if phrase_lower not in seen:
            seen.add(phrase_lower)
            keywords.append(phrase_lower)

    return polarity, mood, keywords


# ── Reflection ────────────────────────────────────────────────────────────────
def build_reflection(mood: str, keywords: list[str]) -> str:
    """
    Compose a short reflective message based on mood and extracted topics.

    Handles the empty-keywords edge case explicitly.
    """
    topic_str = (
        f"you talked about: {', '.join(keywords[:MAX_KEYWORDS])}"
        if keywords
        else "no specific topics stood out"
    )

    mood_messages = {
        "Positive": "Keep up the good energy! 💪",
        "Negative": "It's okay to feel low — be kind to yourself. 🧠",
        "Neutral":  "Stay balanced and keep reflecting. ☯️",
    }
    closing = mood_messages.get(mood, "Keep going. 🌱")

    return f"You expressed a {mood.lower()} mood and {topic_str}. {closing}"


# ── Persistence ───────────────────────────────────────────────────────────────
def save_entry(entry: JournalEntry) -> None:
    """
    Append a journal entry to the day's file inside JOURNAL_DIR.

    Creates the directory automatically if it does not exist.
    """
    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
    with entry.filename.open("a", encoding="utf-8") as fh:
        fh.write(entry.as_text())
    log.info("Entry saved → %s", entry.filename)


def load_today(date: Optional[datetime.date] = None) -> list[str]:
    """
    Read and return all entries for a given date (defaults to today).

    Returns an empty list if no file exists yet.
    """
    day = date or datetime.date.today()
    path = JOURNAL_DIR / f"journal_{day.strftime('%Y%m%d')}.txt"

    if not path.exists():
        return []

    return path.read_text(encoding="utf-8").splitlines()


# ── CLI helpers ───────────────────────────────────────────────────────────────
def _print_separator(char: str = "─", width: int = 48) -> None:
    print(char * width)


def show_menu() -> str:
    print("\n📔  Voice Journal")
    _print_separator()
    print("  [r] Record a new entry")
    print("  [v] View today's entries")
    print("  [q] Quit")
    _print_separator()
    return input("Choice: ").strip().lower()


# ── Main loop ─────────────────────────────────────────────────────────────────
def main() -> None:
    print("🎙️  Voice Journal — powered by SpeechRecognition + TextBlob")
    print(f"   Journal folder: {JOURNAL_DIR}\n")

    while True:
        try:
            choice = show_menu()

            if choice == "r":
                text = listen()
                if not text:
                    print("⚠️  Nothing recorded — try again.\n")
                    continue

                print(f"\n📝 You said: {text}")

                polarity, mood, keywords = analyze(text)
                reflection = build_reflection(mood, keywords)

                entry = JournalEntry(
                    timestamp=datetime.datetime.now(),
                    raw_text=text,
                    polarity=polarity,
                    mood=mood,
                    keywords=keywords,
                    reflection=reflection,
                )

                print(f"\n🧠 Reflection: {reflection}")
                save_entry(entry)

            elif choice == "v":
                lines = load_today()
                if lines:
                    print("\n📖 Today's entries:\n")
                    print("\n".join(lines))
                else:
                    print("📭 No entries recorded today yet.")

            elif choice == "q":
                print("\n🛑 Goodbye — keep reflecting! 👋")
                break

            else:
                print("⚠️  Unknown option. Please enter r, v, or q.")

        except KeyboardInterrupt:
            print("\n\n🛑 Interrupted — goodbye!")
            break


if __name__ == "__main__":
    main()
