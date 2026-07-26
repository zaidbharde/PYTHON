import struct
import wave
import math
import os

SAMPLE_RATE = 44100

def sine_wave(freq, duration, volume=0.5):
    samples = int(SAMPLE_RATE * duration)
    return [volume * math.sin(2 * math.pi * freq * t / SAMPLE_RATE) for t in range(samples)]

def square_wave(freq, duration, volume=0.3):
    samples = int(SAMPLE_RATE * duration)
    return [volume * (1 if math.sin(2 * math.pi * freq * t / SAMPLE_RATE) >= 0 else -1) for t in range(samples)]

def sawtooth_wave(freq, duration, volume=0.3):
    samples = int(SAMPLE_RATE * duration)
    return [volume * (2 * (freq * t / SAMPLE_RATE % 1) - 1) for t in range(samples)]

def triangle_wave(freq, duration, volume=0.5):
    samples = int(SAMPLE_RATE * duration)
    return [volume * (4 * abs(freq * t / SAMPLE_RATE % 1 - 0.5) - 1) for t in range(samples)]

def apply_envelope(samples, attack=0.05, decay=0.1, sustain=0.7, release=0.1):
    n = len(samples)
    a = int(attack * SAMPLE_RATE)
    d = int(decay * SAMPLE_RATE)
    r = int(release * SAMPLE_RATE)

    result = []
    for i, s in enumerate(samples):
        if i < a:
            env = i / a
        elif i < a + d:
            env = 1.0 - (1.0 - sustain) * ((i - a) / d)
        elif i < n - r:
            env = sustain
        else:
            env = sustain * (n - i) / r
        result.append(s * env)
    return result

def add_reverb(samples, delay=0.05, decay=0.3):
    delay_samples = int(delay * SAMPLE_RATE)
    result = samples[:]
    for i in range(delay_samples, len(result)):
        result[i] += result[i - delay_samples] * decay
    return result

def mix(*tracks):
    max_len = max(len(t) for t in tracks)
    result = [0.0] * max_len
    for track in tracks:
        for i, s in enumerate(track):
            result[i] += s
    peak = max(abs(s) for s in result) or 1.0
    return [s / peak * 0.9 for s in result]

def note_freq(name):
    notes = {'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}
    if name == 'R':
        return 0
    note = name[:-1]
    octave = int(name[-1])
    semitones = notes[note] + (octave - 4) * 12 - 9
    return 440.0 * (2 ** (semitones / 12.0))

def play_melody(notes_str, wave_fn=sine_wave, bpm=120):
    beat = 60.0 / bpm
    samples = []
    for token in notes_str.split():
        parts = token.split(':')
        name = parts[0]
        duration = float(parts[1]) * beat if len(parts) > 1 else beat

        if name == 'R':
            samples.extend([0.0] * int(SAMPLE_RATE * duration))
        else:
            freq = note_freq(name)
            wave = wave_fn(freq, duration)
            wave = apply_envelope(wave)
            samples.extend(wave)
    return samples

def save_wav(filename, samples):
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        for s in samples:
            clamped = max(-1.0, min(1.0, s))
            packed = struct.pack('<h', int(clamped * 32767))
            f.writeframes(packed)

def chord(notes, duration=1.0, wave_fn=sine_wave):
    waves = [wave_fn(note_freq(n), duration, volume=0.3) for n in notes]
    return mix(*waves)


if __name__ == "__main__":
    print("=" * 50)
    print("  🎵 Music Synthesizer")
    print("=" * 50)

    twinkle = "C4:1 C4:1 G4:1 G4:1 A4:1 A4:1 G4:2 F4:1 F4:1 E4:1 E4:1 D4:1 D4:1 C4:2"

    ode_to_joy = "E4:1 E4:1 F4:1 G4:1 G4:1 F4:1 E4:1 D4:1 C4:1 C4:1 D4:1 E4:1 E4:1.5 D4:0.5 D4:2"

    scale = "C4:0.5 D4:0.5 E4:0.5 F4:0.5 G4:0.5 A4:0.5 B4:0.5 C5:1"

    songs = [
        ("twinkle.wav",  twinkle,     sine_wave,     "Twinkle Twinkle (Sine)"),
        ("ode.wav",      ode_to_joy,  triangle_wave, "Ode to Joy (Triangle)"),
        ("scale_sq.wav", scale,       square_wave,   "C Major Scale (Square)"),
        ("scale_saw.wav",scale,       sawtooth_wave, "C Major Scale (Sawtooth)"),
    ]

    for filename, melody, wave_fn, label in songs:
        print(f"\n  Generating: {label}")
        samples = play_melody(melody, wave_fn=wave_fn, bpm=120)
        samples = add_reverb(samples)
        save_wav(filename, samples)
        duration = len(samples) / SAMPLE_RATE
        print(f"    Saved: {filename} ({duration:.1f}s)")

    print(f"\n  Generating: C Major Chord")
    c_major = chord(["C4", "E4", "G4"], duration=2.0, wave_fn=sine_wave)
    c_major = add_reverb(c_major)
    save_wav("chord_c.wav", c_major)

    print(f"\n  Generating: Chord Progression (C-F-G-C)")
    progression = []
    for notes in [["C4","E4","G4"], ["F4","A4","C5"], ["G4","B4","D5"], ["C4","E4","G4"]]:
        c = chord(notes, duration=1.0, wave_fn=triangle_wave)
        c = apply_envelope(c, attack=0.02, release=0.3)
        progression.extend(c)
    progression = add_reverb(progression, delay=0.08, decay=0.2)
    save_wav("progression.wav", progression)

    print(f"\n  Wave comparison (A4 = 440Hz):")
    for name, fn in [("Sine", sine_wave), ("Square", square_wave),
                      ("Sawtooth", sawtooth_wave), ("Triangle", triangle_wave)]:
        wave = fn(440, 0.01)
        visual = ''.join('█' if s > 0.1 else '▄' if s > -0.1 else ' ' for s in wave[:80])
        print(f"    {name:>10} : {visual}")

    print(f"\n  Note frequencies:")
    for n in ["C4","D4","E4","F4","G4","A4","B4","C5"]:
        print(f"    {n} = {note_freq(n):.2f} Hz")

    files = ["twinkle.wav", "ode.wav", "scale_sq.wav", "scale_saw.wav", "chord_c.wav", "progression.wav"]
    for f in files:
        if os.path.exists(f):
            os.remove(f)
    print("\n  Cleaned up generated files.")
