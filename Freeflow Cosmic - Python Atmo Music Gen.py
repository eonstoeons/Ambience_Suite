1#!/usr/bin/env python3
"""
FREEFLOW v2.0 — Pure Python Music + Soundscape Engine
Zero dependencies beyond Python 3.6+ stdlib.
Generates music, nature soundscapes, noise, binaural beats, bytebeat,
singing bowls, cosmic drones, storms, and hybrid blends — all from math.

Usage:
    python freeflow.py                          # interactive menu
    python freeflow.py --mode ambient           # specific mode
    python freeflow.py --prompt "dark drone +vinyl +tape 90 bpm"
    python freeflow.py --mode synthwave --duration 120 --bpm 100
    python freeflow.py --random --duration 60   # surprise me
    python freeflow.py --list                   # show all modes
    python freeflow.py --test                   # 5-second smoke test
"""
import argparse, array, difflib, math, os, random, re, shutil
import struct, subprocess, sys, time, traceback, wave
from pathlib import Path

__version__ = "2.0.0"

# ─── CONFIG ──────────────────────────────────────────────────────────────────

CFG = {
    "sample_rate": 44100,
    "bit_depth": 16,
    "channels": 2,
    "chunk_seconds": 10,
    "default_duration": 180,
    "default_mode": "ambient",
    "output_dir": str(Path.home() / "Documents" / "Freeflow"),
    "filename_prefix": "freeflow",
    "progress_step_percent": 10,
    "master_gain": 0.90,
    "master_drive": 1.12,
    "stereo_width": 1.15,
    "vinyl_hiss": 0.010,
    "vinyl_crackle_prob": 0.00025,
    "vinyl_crackle_amp": 0.28,
    "vinyl_rumble": 0.005,
    "tape_wow_rate": 0.35,
    "tape_wow_depth": 0.0011,
    "tape_flutter_rate": 6.0,
    "tape_flutter_depth": 0.00035,
    "tape_bandwidth": 13500.0,
    "tape_drive": 1.06,
    "humanize_seconds": 0.004,
}

SR = CFG["sample_rate"]
INV_SR = 1.0 / SR
TAU = math.tau
NYQUIST = SR * 0.5
CHUNK = int(CFG["chunk_seconds"] * SR)
_sin = math.sin
_cos = math.cos
_tanh = math.tanh
_exp = math.exp
_log = math.log
_pi = math.pi
_sqrt = math.sqrt
_rand = random.random
_gauss = random.gauss
_uniform = random.uniform

# ─── HELPERS ─────────────────────────────────────────────────────────────────

def clamp(x, lo=-1.0, hi=1.0):
    return lo if x < lo else hi if x > hi else x

def soft_clip(x, drive=1.12):
    d = _tanh(drive)
    return _tanh(x * drive) / d if d else x

def lerp(a, b, t):
    return a + (b - a) * t

def mtof(note):
    return 440.0 * (2.0 ** ((note - 69.0) / 12.0))

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def note_name_to_midi(name):
    s = name.strip().upper()
    if not s:
        return 48
    base_map = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    if s[0] not in base_map:
        return 48
    base = base_map[s[0]]
    idx = 1
    if len(s) > 1 and s[1] == "#":
        base += 1
        idx = 2
    elif len(s) > 1 and s[1] == "B":
        base -= 1
        idx = 2
    try:
        octave = int(s[idx:])
    except Exception:
        octave = 3
    return (octave + 1) * 12 + base

def midi_to_name(midi):
    return f"{NOTE_NAMES[midi % 12]}{midi // 12 - 1}"

def humanize(t, amt=None):
    a = CFG["humanize_seconds"] if amt is None else amt
    return t + _gauss(0.0, a)

def parse_duration_text(text):
    if not text:
        return None
    m = re.search(r'(\d+)\s*(seconds?|sec|s|minutes?|min|m|hours?|hr|h)\b', text)
    if not m:
        return None
    n = int(m.group(1))
    u = m.group(2)
    if u.startswith('h'):
        return n * 3600
    return n * 60 if u.startswith('m') else n

# ─── PROMPT PARSER ───────────────────────────────────────────────────────────

MODE_ALIASES = {
    # music
    "ambient": "ambient",
    "dark ambient": "dark_ambient", "darkambient": "dark_ambient", "dark": "dark_ambient",
    "meditation": "meditation", "sleep": "meditation", "calm": "meditation",
    "drone": "drone",
    "bellscape": "bellscape", "bells": "bellscape",
    "sacred": "sacred", "ritual": "sacred", "temple": "sacred",
    "experimental": "experimental", "weird": "experimental",
    "synthwave": "synthwave", "retro synth": "synthwave", "retrowave": "synthwave", "retro": "synthwave",
    "lofi": "lo_fi", "lo-fi": "lo_fi", "lo fi": "lo_fi",
    "cosmic": "cosmic", "space": "cosmic", "cosmos": "cosmic", "astral": "cosmic",
    # pure nature
    "nature": "pure_nature", "pure nature": "pure_nature",
    "wind": "pure_wind", "pure wind": "pure_wind",
    "rain": "pure_rain", "pure rain": "pure_rain",
    "ocean": "pure_ocean", "waves": "pure_ocean", "pure ocean": "pure_ocean",
    "water": "pure_water", "stream": "pure_water", "pure water": "pure_water",
    "fire": "pure_fire", "pure fire": "pure_fire",
    "birds": "pure_birds", "pure birds": "pure_birds",
    "storm": "pure_storm", "pure storm": "pure_storm", "thunder": "pure_storm", "thunderstorm": "pure_storm",
    "night": "pure_night", "pure night": "pure_night", "crickets": "pure_night",
    # pure noise
    "white noise": "pure_white", "pure white noise": "pure_white",
    "pink noise": "pure_pink", "pure pink noise": "pure_pink",
    "brown noise": "pure_brown", "brownian noise": "pure_brown", "pure brown noise": "pure_brown",
    # pure tonal
    "theta": "pure_theta", "pure theta": "pure_theta",
    "alpha": "pure_alpha", "pure alpha": "pure_alpha",
    "delta": "pure_delta", "pure delta": "pure_delta",
    "bowls": "pure_bowls", "singing bowls": "pure_bowls", "pure bowls": "pure_bowls", "tibetan": "pure_bowls",
    "heartbeat": "pure_heartbeat", "pure heartbeat": "pure_heartbeat", "heart": "pure_heartbeat",
    "chimes": "pure_chimes", "wind chimes": "pure_chimes", "pure chimes": "pure_chimes",
    # pure algorithmic
    "bytebeat": "pure_bytebeat", "pure bytebeat": "pure_bytebeat",
    "fractal": "pure_bytebeat", "algorithmic": "pure_bytebeat", "bitwise": "pure_bytebeat",
}

FLAG_ALIASES = {
    "+vinyl": "vinyl", "vinyl": "vinyl",
    "+tape": "tape", "tape": "tape",
    "+nature": "nature",
    "+drums": "drums", "drums": "drums",
    "+nodrums": "nodrums", "nodrums": "nodrums",
    "+binaural": "binaural", "binaural": "binaural",
    "+bytebeat": "bytebeat",
    "+bright": "bright", "bright": "bright",
    "+dark": "dark_tone",
    "+warm": "warm", "warm": "warm",
    "+cold": "cold", "cold": "cold",
    "+wide": "wide", "wide": "wide",
    "+narrow": "narrow", "narrow": "narrow",
    "+dense": "dense", "dense": "dense",
    "+sparse": "sparse", "sparse": "sparse",
    "+bowls": "bowls",
    "+chimes": "chimes",
    "+storm": "storm",
    "+heartbeat": "heartbeat",
    "+night": "night",
}

def normalize_prompt(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#\s_\-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def fuzzy_lookup(token, table):
    keys = list(table.keys())
    hit = difflib.get_close_matches(token, keys, n=1, cutoff=0.75)
    return table[hit[0]] if hit else None

def parse_prompt(text):
    norm = normalize_prompt(text)
    tokens = norm.split()
    mode = None
    flags = set()
    bpm = None
    duration = parse_duration_text(norm)
    root = None
    scale = None
    # multi-word aliases first (longest match)
    for alias in sorted(MODE_ALIASES.keys(), key=len, reverse=True):
        if alias in norm:
            mode = MODE_ALIASES[alias]
            break
    if mode is None:
        for tok in tokens:
            v = fuzzy_lookup(tok, MODE_ALIASES)
            if v:
                mode = v
                break
    for alias, flag in FLAG_ALIASES.items():
        if alias in norm:
            flags.add(flag)
    bpm_match = re.search(r'\b(\d{2,3})\s*bpm\b', norm)
    if bpm_match:
        bpm = clamp(int(bpm_match.group(1)), 20, 300)
    note_match = re.search(r"\b([a-g](?:#|b)?[0-8])\b", norm, re.I)
    if note_match:
        root = note_name_to_midi(note_match.group(1))
    for s in ["major", "minor", "dorian", "phrygian", "lydian", "mixolydian",
              "pentatonic", "minor_pentatonic", "blues", "chromatic",
              "whole_tone", "harmonic_minor"]:
        if s.replace("_", " ") in norm or s in norm:
            scale = s
            break
    return {"mode": mode, "flags": flags, "bpm": bpm,
            "duration": duration, "root": root, "scale": scale}

# ─── THEORY ──────────────────────────────────────────────────────────────────

SCALES = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "pentatonic": [0, 2, 4, 7, 9],
    "minor_pentatonic": [0, 3, 5, 7, 10],
    "blues": [0, 3, 5, 6, 7, 10],
    "chromatic": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    "whole_tone": [0, 2, 4, 6, 8, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
}

CHORDS = {
    "maj": [0, 4, 7],
    "min": [0, 3, 7],
    "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    "dim": [0, 3, 6],
    "aug": [0, 4, 8],
    "add9": [0, 4, 7, 14],
}

PROGRESSIONS = {
    "ambient": [(0, "sus2"), (4, "sus2"), (3, "maj7"), (0, "sus2")],
    "dark_ambient": [(0, "min"), (1, "min"), (4, "min"), (3, "maj")],
    "synthwave": [(0, "min"), (3, "maj"), (4, "min"), (6, "maj")],
    "lo_fi": [(0, "maj7"), (1, "min7"), (2, "min7"), (4, "maj7")],
    "sacred": [(0, "sus2"), (5, "sus4"), (3, "maj7"), (0, "sus2")],
    "experimental": [(0, "sus2"), (1, "min"), (2, "min"), (4, "maj"), (0, "sus2")],
    "cosmic": [(0, "sus2"), (4, "add9"), (3, "sus4"), (2, "min7"), (0, "sus2")],
    "drone": [(0, "sus2")],
    "meditation": [(0, "sus2"), (4, "sus2")],
    "bellscape": [(0, "sus2"), (4, "sus2"), (0, "sus2")],
}

def build_scale(root, scale_name, octaves=3):
    pat = SCALES.get(scale_name, SCALES["minor"])
    out = []
    for o in range(octaves):
        base = root + o * 12
        for i in pat:
            n = base + i
            if 0 <= n <= 127:
                out.append(n)
    return out

def build_chord(root, chord_name):
    return [root + i for i in CHORDS.get(chord_name, CHORDS["min"])]

def euclidean_rhythm(steps, pulses):
    if pulses <= 0:
        return [False] * steps
    if pulses >= steps:
        return [True] * steps
    pattern = []
    bucket = 0
    for _ in range(steps):
        bucket += pulses
        if bucket >= steps:
            pattern.append(True)
            bucket -= steps
        else:
            pattern.append(False)
    return pattern

# ─── DSP PRIMITIVES ─────────────────────────────────────────────────────────

def osc_tri(phase):
    p = (phase % TAU) / TAU
    return 4.0 * abs(p - 0.5) - 1.0

def osc_pulse(phase, pw=0.5):
    return 1.0 if ((phase % TAU) / TAU) < pw else -1.0

def osc_saw_blep(phase, freq):
    t = (phase % TAU) / TAU
    v = 2.0 * t - 1.0
    dt = freq * INV_SR
    if dt <= 0.0:
        return v
    if t < dt:
        x = t / dt
        v -= x + x - x * x - 1.0
    elif t > 1.0 - dt:
        x = (t - 1.0) / dt
        v -= x + x + x * x + 1.0
    return v

def osc_square_blep(phase, freq):
    t = (phase % TAU) / TAU
    v = 1.0 if t < 0.5 else -1.0
    dt = freq * INV_SR
    if dt <= 0.0:
        return v
    if t < dt:
        x = t / dt
        v += x + x - x * x - 1.0
    elif t > 1.0 - dt:
        x = (t - 1.0) / dt
        v -= x + x + x * x + 1.0
    t2 = (t + 0.5) % 1.0
    if t2 < dt:
        x = t2 / dt
        v -= x + x - x * x - 1.0
    elif t2 > 1.0 - dt:
        x = (t2 - 1.0) / dt
        v += x + x + x * x + 1.0
    return v


class SVF:
    """State Variable Filter — LP / HP / BP."""
    __slots__ = ("lp", "bp", "hp", "_f", "_q")

    def __init__(self, cutoff=1000.0, res=0.0):
        self.lp = self.bp = self.hp = 0.0
        self._f = 0.0
        self._q = 1.0
        self.set(cutoff, res)

    def set(self, cutoff, res=None):
        cutoff = min(max(20.0, cutoff), NYQUIST * 0.95)
        self._f = 2.0 * _sin(_pi * cutoff * INV_SR)
        if res is not None:
            self._q = 1.0 - min(max(0.0, res), 0.97)

    def lp_process(self, x):
        hp = x - self.lp - self._q * self.bp
        self.bp += self._f * hp
        self.lp += self._f * self.bp
        self.hp = hp
        return self.lp

    def hp_process(self, x):
        self.lp_process(x)
        return self.hp

    def bp_process(self, x):
        self.lp_process(x)
        return self.bp


class OnePole:
    """Simple one-pole lowpass / highpass."""
    __slots__ = ("a", "z")

    def __init__(self, cutoff=1000.0):
        self.z = 0.0
        self.set(cutoff)

    def set(self, cutoff):
        x = _exp(-TAU * min(max(cutoff, 1.0), NYQUIST * 0.99) * INV_SR)
        self.a = 1.0 - x

    def lp(self, x):
        self.z += self.a * (x - self.z)
        return self.z

    def hp(self, x):
        return x - self.lp(x)


class ADSR:
    __slots__ = ("a", "d", "s", "r")

    def __init__(self, a=0.01, d=0.1, s=0.7, r=0.3):
        self.a = max(a, 0.001)
        self.d = max(d, 0.001)
        self.s = s
        self.r = max(r, 0.001)

    def get(self, t, dur):
        if t < 0.0:
            return 0.0
        if t < self.a:
            return t / self.a
        if t < self.a + self.d:
            return 1.0 - (1.0 - self.s) * ((t - self.a) / self.d)
        if t < dur:
            return self.s
        rt = t - dur
        if rt < self.r:
            return self.s * (1.0 - rt / self.r)
        return 0.0


# ─── VOICE ENGINES ───────────────────────────────────────────────────────────

class SuperSaw:
    __slots__ = ("phases", "incs", "mix", "freq")

    def __init__(self, freq, detune=0.30, mix=0.82):
        spreads = [-0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03]
        self.phases = [_uniform(0.0, TAU) for _ in range(7)]
        self.incs = [TAU * freq * (1.0 + detune * s) * INV_SR for s in spreads]
        self.mix = mix / 7.0
        self.freq = freq

    def sample(self, t=0.0, env=1.0):
        v = 0.0
        for i in range(7):
            self.phases[i] += self.incs[i]
            v += osc_saw_blep(self.phases[i], self.freq)
        return v * self.mix


class FMSynth:
    __slots__ = ("car_inc", "mod_inc", "depth", "fb", "pc", "pm", "prev")

    def __init__(self, freq, ratio=2.0, depth=1.4, feedback=0.12):
        self.car_inc = TAU * freq * INV_SR
        self.mod_inc = TAU * freq * ratio * INV_SR
        self.depth = depth
        self.fb = feedback
        self.pc = 0.0
        self.pm = 0.0
        self.prev = 0.0

    def sample(self, t=0.0, env=1.0):
        mod = _sin(self.pm + self.prev * self.fb) * self.depth
        self.pm += self.mod_inc
        out = _sin(self.pc + mod)
        self.pc += self.car_inc
        self.prev = out
        return out


class SubSynth:
    __slots__ = ("phase", "inc", "wave", "filt", "env_depth", "base_cut", "freq")

    def __init__(self, freq, wave="saw", cutoff=2000.0, res=0.22, env_depth=2500.0):
        self.phase = _uniform(0.0, TAU)
        self.inc = TAU * freq * INV_SR
        self.wave = wave
        self.filt = SVF(cutoff, res)
        self.env_depth = env_depth
        self.base_cut = cutoff
        self.freq = freq

    def sample(self, t=0.0, env=1.0):
        self.phase += self.inc
        w = self.wave
        if w == "saw":
            v = osc_saw_blep(self.phase, self.freq)
        elif w == "square":
            v = osc_square_blep(self.phase, self.freq)
        elif w == "tri":
            v = osc_tri(self.phase)
        elif w == "pulse":
            pw = 0.35 + 0.15 * _sin(TAU * 0.45 * t)
            v = osc_pulse(self.phase, pw)
        else:
            v = _sin(self.phase)
        cutoff = min(self.base_cut + self.env_depth * env, NYQUIST * 0.95)
        self.filt.set(cutoff)
        return self.filt.lp_process(v)


class KarplusStrong:
    __slots__ = ("buf", "idx", "decay", "bright")

    def __init__(self, freq, decay=0.996, brightness=0.55):
        period = max(int(SR / max(freq, 24.0)), 2)
        self.buf = [_uniform(-1.0, 1.0) for _ in range(period)]
        self.idx = 0
        self.decay = decay
        self.bright = 1.0 - brightness * 0.7

    def sample(self, t=0.0, env=1.0):
        buf = self.buf
        L = len(buf)
        i = self.idx % L
        j = (i + 1) % L
        out = buf[i]
        buf[i] = (buf[i] + buf[j]) * 0.5 * self.bright * self.decay
        self.idx += 1
        return out


class Pad:
    __slots__ = ("phases", "incs", "lfo", "lfo_inc", "n")

    def __init__(self, notes, detune=0.005):
        phases = []
        incs = []
        for n in notes:
            f = mtof(n)
            for d in (-detune, 0.0, detune):
                phases.append(_uniform(0.0, TAU))
                incs.append(TAU * f * (1.0 + d) * INV_SR)
        self.phases = phases
        self.incs = incs
        self.lfo = _uniform(0.0, TAU)
        self.lfo_inc = TAU * 0.16 * INV_SR
        self.n = len(phases)

    def sample(self, t=0.0, env=1.0):
        self.lfo += self.lfo_inc
        mod = 0.7 + 0.3 * (0.5 + 0.5 * _sin(self.lfo))
        v = 0.0
        phases = self.phases
        incs = self.incs
        for i in range(self.n):
            phases[i] += incs[i]
            v += _sin(phases[i])
        return (v / self.n) * mod if self.n else 0.0


class Organ:
    __slots__ = ("phase", "inc")

    def __init__(self, freq):
        self.phase = 0.0
        self.inc = TAU * freq * INV_SR

    def sample(self, t=0.0, env=1.0):
        self.phase += self.inc
        p = self.phase
        return 0.60 * _sin(p) + 0.22 * _sin(p * 2.0) + 0.10 * _sin(p * 3.0) + 0.06 * _sin(p * 4.0)


# ─── DRUMS ───────────────────────────────────────────────────────────────────

class Kick808:
    __slots__ = ("punch", "decay", "tone")

    def __init__(self, punch=1.0, decay=0.40, tone=50.0):
        self.punch = punch
        self.decay = decay
        self.tone = tone

    def sample(self, t=0.0, env=1.0):
        if t < 0.0:
            return 0.0
        pitch = self.tone + 190.0 * self.punch * _exp(-30.0 * t)
        amp = _exp(-t / max(self.decay, 0.001))
        click = _exp(-150.0 * t) * 0.40 * self.punch
        return soft_clip((_sin(TAU * pitch * t) * amp + click) * 0.95, 1.25)


class Snare909:
    __slots__ = ("tone", "noise_amt", "decay", "hpf")

    def __init__(self, tone=195.0, noise_amt=0.62, decay=0.18):
        self.tone = tone
        self.noise_amt = noise_amt
        self.decay = decay
        self.hpf = SVF(2200.0, 0.04)

    def sample(self, t=0.0, env=1.0):
        if t < 0.0:
            return 0.0
        tone_env = _exp(-18.0 * t)
        noise_env = _exp(-t / max(self.decay, 0.001))
        tonal = _sin(TAU * self.tone * t) * tone_env * (1.0 - self.noise_amt)
        noise = self.hpf.hp_process(_uniform(-1.0, 1.0)) * noise_env * self.noise_amt
        return soft_clip((tonal + noise) * 0.82, 1.35)


class HiHat:
    __slots__ = ("decay", "hpf", "phases", "incs")
    RATIOS = (1.0, 1.3420, 1.2312, 1.6532, 1.9523, 2.1523)

    def __init__(self, open_hat=False, decay=0.045):
        self.decay = 0.22 if open_hat else decay
        self.hpf = SVF(7800.0, 0.05)
        base = 420.0
        self.phases = [0.0] * 6
        self.incs = [TAU * base * r * INV_SR for r in self.RATIOS]

    def sample(self, t=0.0, env=1.0):
        if t < 0.0:
            return 0.0
        amp = _exp(-t / max(self.decay, 0.001))
        v = 0.0
        for i in range(6):
            self.phases[i] += self.incs[i]
            v += 1.0 if (self.phases[i] % TAU) < _pi else -1.0
        return self.hpf.hp_process(v / 6.0) * amp * 0.48


class Clap:
    __slots__ = ("decay", "bpf")

    def __init__(self, decay=0.14):
        self.decay = decay
        self.bpf = SVF(1600.0, 0.55)

    def sample(self, t=0.0, env=1.0):
        if t < 0.0:
            return 0.0
        amp = _exp(-t / max(self.decay, 0.001))
        burst = 0.0
        for off in (0.0, 0.010, 0.021, 0.031):
            bt = t - off
            if bt >= 0.0:
                burst += _exp(-90.0 * bt) * _uniform(-1.0, 1.0)
        return self.bpf.bp_process(burst * amp * 0.45)


# ─── NOISE / NATURE / TONAL GENERATORS ──────────────────────────────────────

class PinkNoise:
    __slots__ = ("b",)

    def __init__(self):
        self.b = [0.0] * 6

    def sample(self):
        b = self.b
        w = _uniform(-1.0, 1.0)
        b[0] = 0.99886 * b[0] + w * 0.0555179
        b[1] = 0.99332 * b[1] + w * 0.0750759
        b[2] = 0.96900 * b[2] + w * 0.1538520
        b[3] = 0.86650 * b[3] + w * 0.3104856
        b[4] = 0.55000 * b[4] + w * 0.5329522
        b[5] = -0.7616 * b[5] - w * 0.0168980
        return (b[0] + b[1] + b[2] + b[3] + b[4] + b[5] + w * 0.5362) * 0.11


class BrownNoise:
    __slots__ = ("z",)

    def __init__(self):
        self.z = 0.0

    def sample(self):
        self.z = 0.98 * self.z + 0.03 * _uniform(-1.0, 1.0)
        return clamp(self.z)


class Wind:
    __slots__ = ("pink", "lfo", "inc", "hpf", "lpf", "intensity")

    def __init__(self, intensity=0.4):
        self.pink = PinkNoise()
        self.lfo = _uniform(0.0, TAU)
        self.inc = TAU * 0.09 * INV_SR
        self.hpf = OnePole(80.0)
        self.lpf = OnePole(1600.0)
        self.intensity = intensity

    def sample(self, t=0.0):
        self.lfo += self.inc
        mod = 0.35 + 0.65 * (0.5 + 0.5 * _sin(self.lfo))
        v = self.pink.sample()
        v = self.hpf.hp(v)
        v = self.lpf.lp(v)
        return v * mod * self.intensity


class Rain:
    __slots__ = ("hpf", "bed", "intensity")

    def __init__(self, intensity=0.45):
        self.hpf = OnePole(5000.0)
        self.bed = PinkNoise()
        self.intensity = intensity

    def sample(self, t=0.0):
        noise = self.hpf.hp(self.bed.sample()) * 0.12
        click = _uniform(0.2, 1.0) * self.intensity if _rand() < self.intensity * 0.010 else 0.0
        return noise * self.intensity + click * 0.15


class Ocean:
    __slots__ = ("pink", "lfo", "inc", "lp", "hp", "intensity")

    def __init__(self, intensity=0.5):
        self.pink = PinkNoise()
        self.lfo = _uniform(0.0, TAU)
        self.inc = TAU * 0.035 * INV_SR
        self.lp = OnePole(900.0)
        self.hp = OnePole(35.0)
        self.intensity = intensity

    def sample(self, t=0.0):
        self.lfo += self.inc
        swell = 0.25 + 0.75 * (0.5 + 0.5 * _sin(self.lfo))
        v = self.pink.sample()
        v = self.hp.hp(v)
        v = self.lp.lp(v)
        return v * swell * self.intensity * 0.85


class WaterStream:
    __slots__ = ("pink", "hpf", "lpf", "intensity")

    def __init__(self, intensity=0.35):
        self.pink = PinkNoise()
        self.hpf = OnePole(600.0)
        self.lpf = OnePole(5000.0)
        self.intensity = intensity

    def sample(self, t=0.0):
        v = self.pink.sample()
        v = self.hpf.hp(v)
        v = self.lpf.lp(v)
        burst = 1.0 if _rand() < self.intensity * 0.004 else 0.0
        return (v * 0.25 + burst * _uniform(0.0, 0.3)) * self.intensity


class Fire:
    __slots__ = ("lp", "intensity")

    def __init__(self, intensity=0.35):
        self.lp = OnePole(3200.0)
        self.intensity = intensity

    def sample(self, t=0.0):
        crack = _uniform(-1.0, 1.0) * 0.7 if _rand() < self.intensity * 0.007 else 0.0
        base = self.lp.lp(_uniform(-1.0, 1.0)) * 0.07
        return (base + crack * 0.3) * self.intensity


class Birds:
    __slots__ = ("density", "active", "time_left", "freq", "phase", "fm")

    def __init__(self, density=0.07):
        self.density = density
        self.active = False
        self.time_left = 0.0
        self.freq = 2500.0
        self.phase = 0.0
        self.fm = 0.0

    def sample(self, t=0.0):
        if not self.active:
            if _rand() < self.density * 0.004:
                self.active = True
                self.time_left = _uniform(0.07, 0.32)
                self.freq = random.choice([1800.0, 2200.0, 2600.0, 3200.0, 4100.0])
                self.phase = 0.0
                self.fm = random.choice([1.6, 2.0, 2.5, 3.0])
            return 0.0
        self.time_left -= INV_SR
        if self.time_left <= 0.0:
            self.active = False
            return 0.0
        self.phase += INV_SR
        env = _sin(clamp((1.0 - self.time_left / 0.32), 0.0, 1.0) * _pi)
        mod = _sin(TAU * self.freq * self.fm * self.phase) * 0.45
        return _sin(TAU * self.freq * self.phase + mod) * env * 0.22


class Thunder:
    """Low rumble bursts with filtered noise decay."""
    __slots__ = ("active", "time_left", "amp", "lp1", "lp2", "hp", "intensity", "cooldown")

    def __init__(self, intensity=0.5):
        self.active = False
        self.time_left = 0.0
        self.amp = 0.0
        self.lp1 = OnePole(120.0)
        self.lp2 = OnePole(350.0)
        self.hp = OnePole(25.0)
        self.intensity = intensity
        self.cooldown = 0.0

    def sample(self, t=0.0):
        if self.cooldown > 0.0:
            self.cooldown -= INV_SR
        if not self.active:
            if self.cooldown <= 0.0 and _rand() < self.intensity * 0.00004:
                self.active = True
                self.time_left = _uniform(1.5, 4.5)
                self.amp = _uniform(0.5, 1.0)
                self.cooldown = _uniform(4.0, 12.0)
            return 0.0
        self.time_left -= INV_SR
        if self.time_left <= 0.0:
            self.active = False
            return 0.0
        env = _exp(-1.8 / max(self.time_left, 0.01))
        rumble = self.lp1.lp(_uniform(-1.0, 1.0))
        crack = self.lp2.lp(_uniform(-1.0, 1.0))
        v = (rumble * 0.6 + crack * 0.4) * env * self.amp
        v = self.hp.hp(v)
        return v * self.intensity * 0.7


class Crickets:
    """Stridulation — fast-pulsed sine bursts at insect frequencies."""
    __slots__ = ("density", "phase", "chirp_t", "chirp_dur", "freq", "pulse_rate", "intensity")

    def __init__(self, density=0.5, intensity=0.25):
        self.density = density
        self.phase = 0.0
        self.chirp_t = -1.0
        self.chirp_dur = 0.0
        self.freq = 4200.0
        self.pulse_rate = 55.0
        self.intensity = intensity

    def sample(self, t=0.0):
        if self.chirp_t < 0.0:
            if _rand() < self.density * 0.003:
                self.chirp_t = 0.0
                self.chirp_dur = _uniform(0.3, 1.2)
                self.freq = _uniform(3600.0, 5500.0)
                self.pulse_rate = _uniform(40.0, 70.0)
                self.phase = 0.0
            return 0.0
        self.chirp_t += INV_SR
        if self.chirp_t > self.chirp_dur:
            self.chirp_t = -1.0
            return 0.0
        self.phase += TAU * self.freq * INV_SR
        pulse = (0.5 + 0.5 * _sin(TAU * self.pulse_rate * self.chirp_t))
        env = _sin(clamp(self.chirp_t / self.chirp_dur, 0.0, 1.0) * _pi)
        return _sin(self.phase) * pulse * env * self.intensity * 0.18


class SingingBowl:
    """Tibetan singing bowl — decaying partials with beating."""
    __slots__ = ("partials", "decay", "t", "interval", "next_strike", "amp", "intensity")

    def __init__(self, intensity=0.45):
        self.partials = []
        self.decay = 0.0
        self.t = 0.0
        self.interval = 0.0
        self.next_strike = 0.0
        self.amp = 0.0
        self.intensity = intensity
        self._new_strike()

    def _new_strike(self):
        base = random.choice([180.0, 220.0, 260.0, 310.0, 370.0, 440.0])
        # bowl partials with slight inharmonicity
        ratios = [1.0, 2.71, 4.77, 7.03, 9.43]
        beats = [0.0, 0.7, 1.2, 0.5, 0.9]
        self.partials = []
        for r, b in zip(ratios, beats):
            f = base * r
            if f < NYQUIST * 0.9:
                self.partials.append((_uniform(0.0, TAU), TAU * f * INV_SR,
                                      TAU * b * INV_SR, 1.0 / (r * r * 0.3 + 1.0)))
        self.decay = _uniform(5.0, 12.0)
        self.t = 0.0
        self.amp = _uniform(0.5, 1.0)
        self.interval = _uniform(6.0, 18.0)
        self.next_strike = self.interval

    def sample(self, t_sec=0.0):
        self.t += INV_SR
        if self.t > self.next_strike:
            self._new_strike()
        env = _exp(-self.t * 2.0 / max(self.decay, 0.01))
        if env < 0.001:
            return 0.0
        v = 0.0
        for i, (ph, inc, beat_inc, amp) in enumerate(self.partials):
            ph += inc
            v += _sin(ph) * amp * (0.85 + 0.15 * _sin(ph * 0.0001 + beat_inc * self.t * SR))
            self.partials[i] = (ph, inc, beat_inc, amp)
        return v * env * self.amp * self.intensity * 0.16


class Heartbeat:
    """Double-pulse heartbeat at configurable BPM."""
    __slots__ = ("bpm", "phase", "inc", "lp", "intensity")

    def __init__(self, bpm=60.0, intensity=0.45):
        self.bpm = bpm
        self.phase = 0.0
        self.inc = bpm / 60.0 * INV_SR
        self.lp = OnePole(60.0)
        self.intensity = intensity

    def sample(self, t=0.0):
        self.phase += self.inc
        p = self.phase % 1.0
        # S1 peak ~0.0, S2 peak ~0.33
        s1 = _exp(-((p - 0.0) ** 2) / 0.0008) * 1.0
        s2 = _exp(-((p - 0.33) ** 2) / 0.0012) * 0.65
        v = s1 + s2
        v = self.lp.lp(_sin(TAU * 38.0 * p) * v)
        return v * self.intensity * 0.55


class WindChimes:
    """Stochastic bell-like tones with metallic partials."""
    __slots__ = ("density", "active_chimes", "intensity")

    def __init__(self, density=0.3, intensity=0.30):
        self.density = density
        self.active_chimes = []  # list of (phase, freq, decay_rate, t, amp)
        self.intensity = intensity

    def sample(self, t=0.0):
        # maybe trigger new chime (cap at 12 concurrent)
        if len(self.active_chimes) < 12 and _rand() < self.density * 0.0003:
            freq = random.choice([1200.0, 1580.0, 1890.0, 2100.0, 2640.0, 3150.0, 3520.0])
            self.active_chimes.append([0.0, freq, _uniform(3.0, 8.0), 0.0, _uniform(0.3, 1.0)])
        v = 0.0
        alive = []
        for ch in self.active_chimes:
            ch[0] += TAU * ch[1] * INV_SR  # phase
            ch[3] += INV_SR  # t
            env = _exp(-ch[3] / ch[2])
            if env < 0.001:
                continue
            alive.append(ch)
            # fundamental + inharmonic partial
            tone = _sin(ch[0]) * 0.6 + _sin(ch[0] * 2.76) * 0.25 + _sin(ch[0] * 5.4) * 0.12
            v += tone * env * ch[4]
        self.active_chimes = alive
        return v * self.intensity * 0.12


class Binaural:
    __slots__ = ("carrier", "beat", "phase", "t")

    def __init__(self, carrier=200.0, beat=4.0):
        self.carrier = carrier
        self.beat = beat
        self.phase = 0.0
        self.t = 0.0

    def sample(self):
        self.phase += TAU * self.carrier * INV_SR
        self.t += INV_SR
        return _sin(self.phase), _sin(self.phase + TAU * self.beat * self.t)


class BytebeatAmbient:
    __slots__ = ("t", "sr_scale", "lp1", "lp2", "hp", "feedback",
                 "mode", "intensity", "drift_phase", "drift_inc")

    def __init__(self, intensity=0.35, mode=0):
        self.t = 0
        self.sr_scale = max(1, int(SR / 8000))
        self.lp1 = OnePole(1800.0)
        self.lp2 = OnePole(900.0)
        self.hp = OnePole(40.0)
        self.feedback = 0.0
        self.mode = mode % 5
        self.intensity = intensity
        self.drift_phase = _uniform(0.0, TAU)
        self.drift_inc = TAU * 0.013 * INV_SR

    def _formula(self, x):
        m = self.mode
        if m == 0:
            y = ((x >> 7) | (x >> 6) | (x * 3)) & 255
            z = ((x * ((y & 31) + 1)) >> 8) & 255
            return (y ^ z) & 255
        elif m == 1:
            y = (x * ((x >> 9) | (x >> 13))) & 255
            z = ((x >> 5) | (x >> 8)) & 255
            return (y ^ z) & 255
        elif m == 2:
            y = ((x * 5 & (x >> 7)) | (x * 3 & (x >> 10))) & 255
            z = ((x >> 4) ^ (x >> 6) ^ (x >> 9)) & 255
            return (y + z) & 255
        elif m == 3:
            y = ((x >> 8) | (x >> 5) | (x * 9)) & 255
            z = ((x * ((x >> 11) & 15 or 1)) >> 7) & 255
            return (y ^ z) & 255
        else:
            # new: harmonic cascade
            y = ((x | (x >> 11)) * (x & (x >> 3))) & 255
            z = ((x >> 6) * (x >> 2) & (x >> 8)) & 255
            return (y ^ z) & 255

    def sample(self, t_sec=0.0):
        self.drift_phase += self.drift_inc
        drift = 0.98 + 0.04 * (0.5 + 0.5 * _sin(self.drift_phase))
        x = int(self.t / self.sr_scale * drift)
        raw = self._formula(x)
        fb_term = int((self.feedback * 127.0) + 128.0) & 255
        raw = (raw ^ (fb_term >> 1)) & 255
        v = (raw - 128.0) / 128.0
        v = self.lp1.lp(v)
        v = self.lp2.lp(v)
        v = v - self.hp.lp(v) * 0.15
        self.feedback = 0.985 * self.feedback + 0.015 * v
        self.t += 1
        return v * self.intensity


# ─── EFFECTS ─────────────────────────────────────────────────────────────────

class Delay:
    __slots__ = ("bl", "br", "il", "ir", "fb", "mix")

    def __init__(self, time_l=0.375, time_r=0.25, feedback=0.35, mix=0.25):
        self.bl = [0.0] * (int(SR * time_l) + 2)
        self.br = [0.0] * (int(SR * time_r) + 2)
        self.il = 0
        self.ir = 0
        self.fb = feedback
        self.mix = mix

    def process(self, l, r):
        bl = self.bl
        br = self.br
        il = self.il % len(bl)
        ir = self.ir % len(br)
        dl = bl[il]
        dr = br[ir]
        bl[il] = l + dl * self.fb
        br[ir] = r + dr * self.fb
        self.il += 1
        self.ir += 1
        return l + dl * self.mix, r + dr * self.mix


class Reverb:
    __slots__ = ("combs", "ci", "cfb", "aps", "ai", "lps", "damp", "mix")
    COMB_DELAYS = (0.02257, 0.02743, 0.03119, 0.03371, 0.03570, 0.03712)
    AP_DELAYS = (0.0050, 0.0017, 0.00051)

    def __init__(self, size=0.9, damp=0.45, mix=0.30):
        self.combs = [[0.0] * max(int(SR * d * size), 2) for d in self.COMB_DELAYS]
        self.ci = [0] * len(self.combs)
        self.cfb = 0.82
        self.aps = [[0.0] * max(int(SR * d), 2) for d in self.AP_DELAYS]
        self.ai = [0] * len(self.aps)
        self.lps = [0.0] * len(self.combs)
        self.damp = damp
        self.mix = mix

    def process(self, x):
        out = 0.0
        for i, buf in enumerate(self.combs):
            idx = self.ci[i] % len(buf)
            val = buf[idx]
            self.lps[i] = val * (1.0 - self.damp) + self.lps[i] * self.damp
            buf[idx] = x + self.lps[i] * self.cfb
            self.ci[i] += 1
            out += val
        out /= len(self.combs)
        for i, buf in enumerate(self.aps):
            idx = self.ai[i] % len(buf)
            bv = buf[idx]
            buf[idx] = out + bv * 0.5
            self.ai[i] += 1
            out = bv - out * 0.5
        return x * (1.0 - self.mix) + out * self.mix


class Chorus:
    __slots__ = ("buf", "idx", "ph1", "ph2", "inc1", "inc2", "depth", "mix")

    def __init__(self, rate=1.1, depth=0.003, mix=0.28):
        self.buf = [0.0] * (int(SR * 0.04) + 2)
        self.idx = 0
        self.ph1 = 0.0
        self.ph2 = _pi / 3.0
        self.inc1 = TAU * rate * INV_SR
        self.inc2 = TAU * rate * 1.07 * INV_SR
        self.depth = depth * SR
        self.mix = mix

    def process(self, x):
        buf = self.buf
        L = len(buf)
        idx = self.idx
        buf[idx % L] = x
        self.idx += 1
        self.ph1 += self.inc1
        self.ph2 += self.inc2
        off1 = self.depth * (1.0 + _sin(self.ph1)) * 0.5
        ri1 = idx - int(off1)
        f1 = off1 - int(off1)
        a1 = buf[ri1 % L]
        b1 = buf[(ri1 - 1) % L]
        wet1 = a1 + (b1 - a1) * f1
        off2 = self.depth * (1.0 + _sin(self.ph2)) * 0.5
        ri2 = idx - int(off2)
        f2 = off2 - int(off2)
        a2 = buf[ri2 % L]
        b2 = buf[(ri2 - 1) % L]
        wet2 = a2 + (b2 - a2) * f2
        m = self.mix
        return x * (1.0 - m) + wet1 * m, x * (1.0 - m) + wet2 * m


class VinylTexture:
    __slots__ = ("pink", "rumble_lp", "crackle")

    def __init__(self):
        self.pink = PinkNoise()
        self.rumble_lp = OnePole(70.0)
        self.crackle = 0.0

    def sample(self):
        hiss = self.pink.sample() * CFG["vinyl_hiss"]
        rumble = self.rumble_lp.lp(_uniform(-1.0, 1.0)) * CFG["vinyl_rumble"]
        crack = 0.0
        if self.crackle > 0.001:
            self.crackle *= 0.88
            crack = _uniform(-1.0, 1.0) * self.crackle
        elif _rand() < CFG["vinyl_crackle_prob"]:
            self.crackle = CFG["vinyl_crackle_amp"]
        return hiss + rumble + crack


class TapeProcessor:
    __slots__ = ("buf", "idx", "wow", "flutter", "wow_inc",
                 "flutter_inc", "lp", "drive", "dw", "df")

    def __init__(self):
        self.buf = [0.0] * (int(SR * 0.05) + 2)
        self.idx = 0
        self.wow = 0.0
        self.flutter = 0.0
        self.wow_inc = TAU * CFG["tape_wow_rate"] * INV_SR
        self.flutter_inc = TAU * CFG["tape_flutter_rate"] * INV_SR
        self.lp = OnePole(CFG["tape_bandwidth"])
        self.drive = CFG["tape_drive"]
        self.dw = CFG["tape_wow_depth"] * SR
        self.df = CFG["tape_flutter_depth"] * SR

    def process(self, x):
        buf = self.buf
        L = len(buf)
        buf[self.idx % L] = x
        self.idx += 1
        self.wow += self.wow_inc
        self.flutter += self.flutter_inc
        offset = (self.dw * (1.0 + _sin(self.wow)) * 0.5 +
                  self.df * (1.0 + _sin(self.flutter)) * 0.5 + 2.0)
        ri = self.idx - int(offset)
        frac = offset - int(offset)
        a = buf[ri % L]
        b = buf[(ri - 1) % L]
        wet = a + (b - a) * frac
        wet = self.lp.lp(wet)
        return soft_clip(wet, self.drive)


# ─── EVENTS / GENRES ─────────────────────────────────────────────────────────

class Event:
    __slots__ = ("time", "duration", "engine", "vol", "pan", "env", "is_sub", "is_drum")

    def __init__(self, time, duration, engine, vol=0.5, pan=0.0,
                 env=None, is_sub=False, is_drum=False):
        self.time = time
        self.duration = duration
        self.engine = engine
        self.vol = vol
        self.pan = pan
        self.env = env or ADSR(0.01, 0.1, 0.7, 0.3)
        self.is_sub = is_sub
        self.is_drum = is_drum


GENRES = {
    "ambient": {
        "bpm": (60, 76), "scale": "pentatonic", "key": 48, "prog": "ambient",
        "density": 0.20, "drums": False,
        "bass_wave": "sine", "bass_oct": -2, "bass_cut": 300, "bass_res": 0.08,
        "lead": "fm", "lead_oct": 1, "lead_detune": 0.06, "lead_vol": 0.26,
        "pad": True, "pad_vol": 0.62,
        "reverb_size": 1.20, "reverb_damp": 0.38, "reverb_mix": 0.54,
        "delay_time": 0.50, "delay_fb": 0.40, "delay_mix": 0.40,
        "chorus_rate": 0.65, "chorus_depth": 0.004,
        "duration": (200, 380),
    },
    "dark_ambient": {
        "bpm": (52, 66), "scale": "phrygian", "key": 45, "prog": "dark_ambient",
        "density": 0.14, "drums": False,
        "bass_wave": "sine", "bass_oct": -2, "bass_cut": 220, "bass_res": 0.18,
        "lead": "fm", "lead_oct": 0, "lead_detune": 0.04, "lead_vol": 0.22,
        "pad": True, "pad_vol": 0.72,
        "reverb_size": 1.42, "reverb_damp": 0.62, "reverb_mix": 0.64,
        "delay_time": 0.65, "delay_fb": 0.42, "delay_mix": 0.40,
        "chorus_rate": 0.38, "chorus_depth": 0.005,
        "duration": (260, 520),
    },
    "meditation": {
        "bpm": (50, 62), "scale": "pentatonic", "key": 48, "prog": "meditation",
        "density": 0.10, "drums": False,
        "bass_wave": "sine", "bass_oct": -2, "bass_cut": 180, "bass_res": 0.03,
        "lead": "fm", "lead_oct": 1, "lead_detune": 0.015, "lead_vol": 0.18,
        "pad": True, "pad_vol": 0.70,
        "reverb_size": 1.55, "reverb_damp": 0.58, "reverb_mix": 0.66,
        "delay_time": 0.75, "delay_fb": 0.42, "delay_mix": 0.42,
        "chorus_rate": 0.42, "chorus_depth": 0.003,
        "duration": (300, 720),
    },
    "drone": {
        "bpm": (40, 52), "scale": "minor", "key": 36, "prog": "drone",
        "density": 0.05, "drums": False,
        "bass_wave": "sine", "bass_oct": -2, "bass_cut": 150, "bass_res": 0.02,
        "lead": "fm", "lead_oct": 0, "lead_detune": 0.12, "lead_vol": 0.14,
        "pad": True, "pad_vol": 0.82,
        "reverb_size": 1.60, "reverb_damp": 0.70, "reverb_mix": 0.70,
        "delay_time": 1.0, "delay_fb": 0.46, "delay_mix": 0.45,
        "chorus_rate": 0.25, "chorus_depth": 0.006,
        "duration": (300, 600),
    },
    "bellscape": {
        "bpm": (68, 84), "scale": "pentatonic", "key": 60, "prog": "bellscape",
        "density": 0.26, "drums": False,
        "bass_wave": "sine", "bass_oct": -1, "bass_cut": 420, "bass_res": 0.06,
        "lead": "karplus", "lead_oct": 1, "lead_detune": 0.0, "lead_vol": 0.44,
        "pad": True, "pad_vol": 0.28,
        "reverb_size": 1.10, "reverb_damp": 0.28, "reverb_mix": 0.52,
        "delay_time": 0.375, "delay_fb": 0.30, "delay_mix": 0.34,
        "chorus_rate": 0.82, "chorus_depth": 0.002,
        "duration": (150, 300),
    },
    "sacred": {
        "bpm": (45, 58), "scale": "pentatonic", "key": 48, "prog": "sacred",
        "density": 0.16, "drums": False,
        "bass_wave": "sine", "bass_oct": -2, "bass_cut": 240, "bass_res": 0.06,
        "lead": "karplus", "lead_oct": 1, "lead_detune": 0.0, "lead_vol": 0.40,
        "pad": True, "pad_vol": 0.60,
        "reverb_size": 1.35, "reverb_damp": 0.45, "reverb_mix": 0.58,
        "delay_time": 0.60, "delay_fb": 0.36, "delay_mix": 0.34,
        "chorus_rate": 0.55, "chorus_depth": 0.003,
        "duration": (240, 480),
    },
    "cosmic": {
        "bpm": (42, 58), "scale": "whole_tone", "key": 40, "prog": "cosmic",
        "density": 0.12, "drums": False,
        "bass_wave": "sine", "bass_oct": -2, "bass_cut": 200, "bass_res": 0.05,
        "lead": "fm", "lead_oct": 1, "lead_detune": 0.08, "lead_vol": 0.20,
        "pad": True, "pad_vol": 0.75,
        "reverb_size": 1.60, "reverb_damp": 0.50, "reverb_mix": 0.68,
        "delay_time": 0.80, "delay_fb": 0.45, "delay_mix": 0.44,
        "chorus_rate": 0.30, "chorus_depth": 0.005,
        "duration": (300, 600),
    },
    "synthwave": {
        "bpm": (94, 112), "scale": "minor", "key": 43, "prog": "synthwave",
        "density": 0.54, "drums": True,
        "bass_wave": "saw", "bass_oct": -1, "bass_cut": 1300, "bass_res": 0.30,
        "lead": "supersaw", "lead_oct": 1, "lead_detune": 0.30, "lead_vol": 0.36,
        "pad": True, "pad_vol": 0.42,
        "reverb_size": 0.88, "reverb_damp": 0.32, "reverb_mix": 0.34,
        "delay_time": 0.375, "delay_fb": 0.34, "delay_mix": 0.28,
        "chorus_rate": 1.0, "chorus_depth": 0.003,
        "duration": (180, 320),
    },
    "lo_fi": {
        "bpm": (74, 90), "scale": "dorian", "key": 48, "prog": "lo_fi",
        "density": 0.36, "drums": True,
        "bass_wave": "tri", "bass_oct": -1, "bass_cut": 580, "bass_res": 0.14,
        "lead": "fm", "lead_oct": 1, "lead_detune": 0.018, "lead_vol": 0.24,
        "pad": True, "pad_vol": 0.30,
        "reverb_size": 0.72, "reverb_damp": 0.56, "reverb_mix": 0.30,
        "delay_time": 0.333, "delay_fb": 0.28, "delay_mix": 0.20,
        "chorus_rate": 1.05, "chorus_depth": 0.003,
        "duration": (120, 260),
    },
    "experimental": {
        "bpm": (55, 110), "scale": "blues", "key": 42, "prog": "experimental",
        "density": 0.42, "drums": False,
        "bass_wave": "pulse", "bass_oct": -1, "bass_cut": 1400, "bass_res": 0.28,
        "lead": "karplus", "lead_oct": 1, "lead_detune": 0.08, "lead_vol": 0.34,
        "pad": True, "pad_vol": 0.30,
        "reverb_size": 0.95, "reverb_damp": 0.28, "reverb_mix": 0.42,
        "delay_time": 0.333, "delay_fb": 0.40, "delay_mix": 0.34,
        "chorus_rate": 1.4, "chorus_depth": 0.004,
        "duration": (120, 300),
    },
}

PURE_MODES = {
    "pure_nature", "pure_wind", "pure_rain", "pure_ocean", "pure_water",
    "pure_fire", "pure_birds", "pure_storm", "pure_night",
    "pure_white", "pure_pink", "pure_brown",
    "pure_theta", "pure_alpha", "pure_delta",
    "pure_bowls", "pure_heartbeat", "pure_chimes",
    "pure_bytebeat",
}


def apply_flags_to_genre(cfg, flags):
    cfg = dict(cfg)
    if "nodrums" in flags:
        cfg["drums"] = False
    if "drums" in flags:
        cfg["drums"] = True
    if "warm" in flags:
        cfg["bass_cut"] = int(cfg["bass_cut"] * 0.7)
        cfg["pad_vol"] = min(1.0, cfg["pad_vol"] + 0.05)
        cfg["reverb_damp"] = max(cfg["reverb_damp"], 0.55)
    if "cold" in flags:
        cfg["bass_cut"] = int(cfg["bass_cut"] * 1.3)
        cfg["pad_vol"] = max(0.0, cfg["pad_vol"] - 0.05)
        cfg["reverb_damp"] = min(cfg["reverb_damp"], 0.30)
    if "bright" in flags:
        cfg["lead_vol"] = min(0.8, cfg["lead_vol"] + 0.05)
    if "dark_tone" in flags:
        cfg["lead_vol"] = max(0.05, cfg["lead_vol"] - 0.03)
        cfg["reverb_damp"] = max(cfg["reverb_damp"], 0.60)
    if "sparse" in flags:
        cfg["density"] *= 0.55
    if "dense" in flags:
        cfg["density"] = min(1.0, cfg["density"] * 1.4)
    return cfg


def energy_curve(t, total_dur):
    p = t / max(total_dur, 1.0)
    if p < 0.08:
        return (p / 0.08) * 0.30
    if p < 0.25:
        return 0.30 + ((p - 0.08) / 0.17) * 0.70
    if p < 0.70:
        return 1.0
    if p < 0.80:
        return 1.0 - ((p - 0.70) / 0.10) * 0.40
    if p < 0.90:
        return 0.60 + ((p - 0.80) / 0.10) * 0.40
    fade = (p - 0.90) / 0.10
    return max(0.0, 1.0 - fade)


def generate_music_events(mode, rng, bpm=None, root=None,
                          scale_name=None, duration=None, flags=None):
    flags = flags or set()
    genre = apply_flags_to_genre(GENRES.get(mode, GENRES["ambient"]), flags)
    bpm = bpm or rng.randint(*genre["bpm"])
    beat = 60.0 / bpm
    bar = beat * 4.0
    root = root if root is not None else genre["key"]
    scale_name = scale_name or genre["scale"]
    duration = duration or rng.randint(*genre["duration"])
    total_bars = max(1, int(duration / bar))
    scale = build_scale(root, scale_name, 3)
    bass_scale = build_scale(root + genre["bass_oct"] * 12, scale_name, 2)
    prog = PROGRESSIONS.get(genre["prog"], PROGRESSIONS["ambient"])
    events = []
    density = genre["density"]

    # pads
    if genre["pad"]:
        step_bars = rng.choice([2, 4, 4, 8])
        for bar_n in range(0, total_bars, step_bars):
            en = energy_curve(bar_n * bar, duration)
            if en < 0.12:
                continue
            root_deg, chord_type = prog[bar_n % len(prog)]
            chord_root = scale[root_deg % len(scale)] + 12
            notes = build_chord(chord_root, chord_type)
            t = bar_n * bar
            dur = min(bar * rng.choice([2, 4, 4, 8]), max(0.5, duration - t))
            pad = Pad(notes, detune=rng.uniform(0.003, 0.008))
            events.append(Event(
                t, dur, pad,
                vol=genre["pad_vol"] * (0.35 + 0.65 * en),
                pan=rng.uniform(-0.25, 0.25),
                env=ADSR(rng.uniform(0.5, 2.0), rng.uniform(0.4, 1.0),
                         rng.uniform(0.65, 0.92), rng.uniform(1.2, 3.2))))

    # bass
    for bar_n in range(total_bars):
        en = energy_curve(bar_n * bar, duration)
        root_deg, _ = prog[bar_n % len(prog)]
        bass_root = bass_scale[root_deg % len(bass_scale)]
        bpat = euclidean_rhythm(16, rng.choice([4, 6, 8]))
        for step in range(16):
            if bpat[step] and rng.random() < density * (0.4 + 0.6 * en):
                t = humanize(bar_n * bar + step * beat * 0.25, 0.004)
                nd = beat * rng.choice([0.5, 1.0, 1.0, 2.0])
                freq = mtof(bass_root + rng.choice([0, 0, 0, 12]))
                bass = SubSynth(freq, wave=genre["bass_wave"],
                                cutoff=genre["bass_cut"], res=genre["bass_res"],
                                env_depth=genre["bass_cut"] * 2.2)
                events.append(Event(t, nd, bass, vol=0.56, pan=0.0,
                                    env=ADSR(0.006, 0.12, 0.60, 0.12), is_sub=True))

    # lead
    for bar_n in range(total_bars):
        en = energy_curve(bar_n * bar, duration)
        if rng.random() > density * (0.30 + 0.70 * en):
            continue
        root_deg, chord_type = prog[bar_n % len(prog)]
        chord_root = scale[root_deg % len(scale)] + genre["lead_oct"] * 12
        num_notes = rng.randint(2, 7)
        for n in range(num_notes):
            t = humanize(bar_n * bar + n * bar / num_notes, 0.006)
            nd = bar / num_notes * rng.uniform(0.5, 0.9)
            if t >= duration:
                continue
            note = (rng.choice(build_chord(chord_root, chord_type))
                    if rng.random() < 0.60
                    else rng.choice(scale) + genre["lead_oct"] * 12)
            freq = mtof(note)
            lead_type = genre["lead"]
            is_sub = False
            if lead_type == "supersaw":
                synth = SuperSaw(freq, detune=genre["lead_detune"],
                                 mix=rng.uniform(0.60, 0.90))
            elif lead_type == "fm":
                synth = FMSynth(freq, ratio=rng.choice([1.0, 2.0, 3.0, 4.0, 0.5]),
                                depth=rng.uniform(0.6, 2.8),
                                feedback=rng.uniform(0.0, 0.25))
            elif lead_type == "karplus":
                synth = KarplusStrong(freq, decay=rng.uniform(0.992, 0.998),
                                      brightness=rng.uniform(0.3, 0.8))
            elif lead_type == "organ":
                synth = Organ(freq)
            else:
                synth = SubSynth(freq, wave="saw", cutoff=3000.0,
                                 res=0.20, env_depth=2200.0)
                is_sub = True
            events.append(Event(
                t, nd, synth,
                vol=genre["lead_vol"] * (0.50 + 0.50 * en),
                pan=rng.uniform(-0.45, 0.45),
                env=ADSR(rng.uniform(0.01, 0.05), rng.uniform(0.08, 0.25),
                         rng.uniform(0.30, 0.75), rng.uniform(0.08, 0.35)),
                is_sub=is_sub))

    # drums
    if genre["drums"]:
        kick_pat = euclidean_rhythm(16, 4)
        hat_pat = euclidean_rhythm(16, rng.choice([8, 10, 12, 14]))
        for bar_n in range(total_bars):
            en = energy_curve(bar_n * bar, duration)
            for step in range(16):
                t = humanize(bar_n * bar + step * beat * 0.25, 0.003)
                if t >= duration:
                    continue
                if kick_pat[step] and rng.random() < (0.65 + 0.35 * en):
                    events.append(Event(
                        t, 0.5,
                        Kick808(punch=rng.uniform(0.78, 1.10),
                                decay=rng.uniform(0.30, 0.48),
                                tone=rng.choice([46.0, 50.0, 54.0])),
                        vol=0.78, pan=0.0,
                        env=ADSR(0.001, 0.01, 1.0, 0.10), is_drum=True))
                if step in (4, 12) and rng.random() < (0.45 + 0.55 * en):
                    events.append(Event(
                        t, 0.3,
                        Snare909(tone=rng.uniform(180.0, 220.0),
                                 noise_amt=rng.uniform(0.50, 0.70),
                                 decay=rng.uniform(0.14, 0.22)),
                        vol=0.55, pan=rng.uniform(-0.10, 0.10),
                        env=ADSR(0.001, 0.01, 1.0, 0.04), is_drum=True))
                if hat_pat[step]:
                    open_hat = (step % 8 == 6) and rng.random() < 0.25
                    hat = HiHat(open_hat=open_hat,
                                decay=0.22 if open_hat else rng.uniform(0.025, 0.060))
                    vel = 0.28 if step % 2 == 0 else 0.18
                    events.append(Event(
                        t, 0.14, hat,
                        vol=vel * (0.35 + 0.65 * en),
                        pan=rng.uniform(-0.35, 0.35),
                        env=ADSR(0.001, 0.008, 1.0, 0.02), is_drum=True))
            if mode in ("synthwave", "lo_fi") and bar_n % 2 == 0 and rng.random() < 0.35:
                ct = bar_n * bar + 2.0 * beat
                if ct < duration:
                    events.append(Event(
                        ct, 0.20,
                        Clap(decay=rng.uniform(0.11, 0.17)),
                        vol=0.24, pan=rng.uniform(-0.15, 0.15),
                        env=ADSR(0.001, 0.01, 1.0, 0.04), is_drum=True))

    # fallback
    if not events:
        pad_notes = build_chord(root + 12, "sus2")
        events.append(Event(
            0.0, max(1.0, duration * 0.9),
            Pad(pad_notes, detune=0.004),
            vol=max(0.22, genre.get("pad_vol", 0.3)), pan=0.0,
            env=ADSR(0.02, 0.20, 0.85, 0.50)))
        sub = SubSynth(mtof(root - 12), wave="sine",
                       cutoff=max(120, genre.get("bass_cut", 200)),
                       res=0.05,
                       env_depth=max(200, genre.get("bass_cut", 200)))
        events.append(Event(
            0.0, max(0.8, duration * 0.75), sub,
            vol=0.30, pan=0.0,
            env=ADSR(0.02, 0.15, 0.70, 0.25), is_sub=True))

    return events, duration, bpm, root, scale_name


# ─── PURE MODE MIXER ────────────────────────────────────────────────────────

def pure_mode_mix(mode):
    mix = {
        "wind": 0.0, "rain": 0.0, "ocean": 0.0, "water": 0.0,
        "fire": 0.0, "birds": 0.0, "thunder": 0.0, "crickets": 0.0,
        "white": 0.0, "pink": 0.0, "brown": 0.0,
        "binaural": 0.0, "bowls": 0.0, "heartbeat": 0.0,
        "chimes": 0.0, "bytebeat": 0.0,
    }
    if mode == "pure_nature":
        mix.update({"wind": 0.20, "rain": 0.20, "ocean": 0.18,
                     "water": 0.18, "fire": 0.05, "birds": 0.08})
    elif mode == "pure_wind":
        mix["wind"] = 1.0
    elif mode == "pure_rain":
        mix["rain"] = 1.0
    elif mode == "pure_ocean":
        mix["ocean"] = 1.0
    elif mode == "pure_water":
        mix["water"] = 1.0
    elif mode == "pure_fire":
        mix["fire"] = 1.0
    elif mode == "pure_birds":
        mix["birds"] = 1.0
    elif mode == "pure_storm":
        mix.update({"wind": 0.45, "rain": 0.65, "thunder": 0.70})
    elif mode == "pure_night":
        mix.update({"crickets": 0.60, "wind": 0.15, "birds": 0.03})
    elif mode == "pure_white":
        mix["white"] = 1.0
    elif mode == "pure_pink":
        mix["pink"] = 1.0
    elif mode == "pure_brown":
        mix["brown"] = 1.0
    elif mode == "pure_bytebeat":
        mix["bytebeat"] = 1.0
    elif mode == "pure_bowls":
        mix["bowls"] = 1.0
    elif mode == "pure_heartbeat":
        mix["heartbeat"] = 1.0
    elif mode == "pure_chimes":
        mix.update({"chimes": 0.80, "wind": 0.15})
    elif mode == "pure_theta":
        mix["binaural"] = 0.8
    elif mode == "pure_alpha":
        mix["binaural"] = 0.8
    elif mode == "pure_delta":
        mix["binaural"] = 0.8
    return mix


# ─── OUTPUT ──────────────────────────────────────────────────────────────────

def maybe_make_mp3(wav_path):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("  ffmpeg not found — skipping mp3 export.")
        return None
    mp3_path = wav_path.with_suffix(".mp3")
    cmd = [ffmpeg, "-y", "-i", str(wav_path), "-codec:a", "libmp3lame",
           "-b:a", "192k", str(mp3_path)]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        print(f"  Saved MP3: {mp3_path}")
        return mp3_path
    except Exception as e:
        print(f"  MP3 export failed: {e}")
        return None


# ─── RENDER ENGINE ───────────────────────────────────────────────────────────

def render_music_to_wav(path, events, total_dur, mode, bpm,
                        flags=None, mp3=False):
    flags = flags or set()
    genre = apply_flags_to_genre(GENRES.get(mode, GENRES["ambient"]), flags)
    use_vinyl = "vinyl" in flags
    use_tape = "tape" in flags
    use_bytebeat = "bytebeat" in flags

    reverb_l = Reverb(size=genre["reverb_size"], damp=genre["reverb_damp"],
                      mix=genre["reverb_mix"])
    reverb_r = Reverb(size=genre["reverb_size"] * 1.07,
                      damp=min(0.95, genre["reverb_damp"] * 1.04),
                      mix=genre["reverb_mix"])
    delay = Delay(time_l=genre["delay_time"],
                  time_r=genre["delay_time"] * 0.75,
                  feedback=genre["delay_fb"], mix=genre["delay_mix"])
    chorus = Chorus(rate=genre["chorus_rate"],
                    depth=genre["chorus_depth"], mix=0.26)
    vinyl = VinylTexture() if use_vinyl else None
    tape_l = TapeProcessor() if use_tape else None
    tape_r = TapeProcessor() if use_tape else None
    bytebeat = BytebeatAmbient(intensity=0.14, mode=0) if use_bytebeat else None
    bb_lp_l = OnePole(2600.0)
    bb_lp_r = OnePole(2400.0)

    # optional layer generators from flags
    layer_bowls = SingingBowl(0.30) if "bowls" in flags else None
    layer_chimes = WindChimes(0.25, 0.20) if "chimes" in flags else None
    layer_heartbeat = Heartbeat(60.0, 0.30) if "heartbeat" in flags else None

    # nature layers from flags
    layer_wind = Wind(0.15) if "nature" in flags or "storm" in flags else None
    layer_rain = Rain(0.20) if "nature" in flags or "storm" in flags else None
    layer_thunder = Thunder(0.50) if "storm" in flags else None
    layer_crickets = Crickets(0.40, 0.20) if "night" in flags else None

    events = sorted(events, key=lambda e: e.time)
    total_samples = int(total_dur * SR) + SR
    ev_ptr = 0
    active = []
    width = CFG["stereo_width"]
    if "wide" in flags:
        width = min(2.0, width * 1.35)
    if "narrow" in flags:
        width = max(0.3, width * 0.65)
    mg = CFG["master_gain"]
    md = CFG["master_drive"]
    progress_mark = -1

    # pre-allocate frame buffer for a chunk
    pack = struct.pack

    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)

        for chunk_start in range(0, total_samples, CHUNK):
            chunk_end = min(chunk_start + CHUNK, total_samples)
            chunk_size = chunk_end - chunk_start
            frames = bytearray(chunk_size * 4)
            fi = 0

            for i in range(chunk_start, chunk_end):
                t = i * INV_SR

                # activate events
                while ev_ptr < len(events) and events[ev_ptr].time <= t + 0.005:
                    active.append(events[ev_ptr])
                    ev_ptr += 1

                sl = 0.0
                sr = 0.0
                still = []

                for ev in active:
                    lt = t - ev.time
                    if lt > ev.duration + ev.env.r + 1.2:
                        continue
                    still.append(ev)
                    env_v = ev.env.get(lt, ev.duration)
                    if env_v < 0.00005:
                        continue
                    if ev.is_sub:
                        v = ev.engine.sample(lt, env_v)
                    else:
                        v = ev.engine.sample(lt)
                    v *= env_v * ev.vol
                    pan_r = (ev.pan + 1.0) * _pi * 0.25
                    sl += v * _cos(pan_r)
                    sr += v * _sin(pan_r)

                active = still

                # extra layers
                if bytebeat is not None:
                    bb = bytebeat.sample(t)
                    sl += bb_lp_l.lp(bb * 0.95)
                    sr += bb_lp_r.lp(bb * 1.05)
                if layer_bowls is not None:
                    bv = layer_bowls.sample(t)
                    sl += bv
                    sr += bv
                if layer_chimes is not None:
                    cv = layer_chimes.sample(t)
                    sl += cv * 0.8
                    sr += cv * 1.2
                if layer_heartbeat is not None:
                    hv = layer_heartbeat.sample(t)
                    sl += hv
                    sr += hv
                if layer_wind is not None:
                    wv = layer_wind.sample(t)
                    sl += wv
                    sr += wv * 0.95
                if layer_rain is not None:
                    rv = layer_rain.sample(t)
                    sl += rv
                    sr += rv
                if layer_thunder is not None:
                    tv = layer_thunder.sample(t)
                    sl += tv
                    sr += tv * 0.92
                if layer_crickets is not None:
                    crv = layer_crickets.sample(t)
                    sl += crv * 0.9
                    sr += crv * 1.1

                # effects chain
                cl, cr = chorus.process(sl)
                cl = reverb_l.process(cl)
                cr = reverb_r.process(cr)
                cl, cr = delay.process(cl, cr)

                if vinyl is not None:
                    tex = vinyl.sample()
                    cl += tex
                    cr += tex * (1.0 + _uniform(-0.20, 0.20))
                if tape_l is not None:
                    cl = tape_l.process(cl)
                    cr = tape_r.process(cr)

                # stereo width
                mid = (cl + cr) * 0.5
                side = (cl - cr) * 0.5 * width
                cl = mid + side
                cr = mid - side

                # master
                cl = soft_clip(cl, md) * mg
                cr = soft_clip(cr, md) * mg
                cl = clamp(cl, -0.999, 0.999)
                cr = clamp(cr, -0.999, 0.999)

                struct.pack_into("<hh", frames, fi,
                                int(cl * 32767), int(cr * 32767))
                fi += 4

            w.writeframes(frames)

            pct = int((chunk_end / total_samples) * 100)
            step = CFG["progress_step_percent"]
            if pct != progress_mark and pct % step == 0:
                print(f"  Rendering {pct}%")
                progress_mark = pct

    if mp3:
        maybe_make_mp3(path)


def render_pure_to_wav(path, mode, duration, seed, flags=None, mp3=False):
    flags = flags or set()
    total_samples = int(duration * SR)
    mix = pure_mode_mix(mode)

    # flag overrides
    if "nature" in flags:
        for k in ("wind", "rain", "ocean"):
            mix[k] = max(mix[k], 0.12)
    if "bytebeat" in flags and mode != "pure_bytebeat":
        mix["bytebeat"] = max(mix.get("bytebeat", 0.0), 0.18)
    if "bowls" in flags:
        mix["bowls"] = max(mix.get("bowls", 0.0), 0.40)
    if "chimes" in flags:
        mix["chimes"] = max(mix.get("chimes", 0.0), 0.35)
    if "heartbeat" in flags:
        mix["heartbeat"] = max(mix.get("heartbeat", 0.0), 0.40)
    if "storm" in flags:
        mix["thunder"] = max(mix.get("thunder", 0.0), 0.50)
        mix["rain"] = max(mix.get("rain", 0.0), 0.40)
        mix["wind"] = max(mix.get("wind", 0.0), 0.30)
    if "night" in flags:
        mix["crickets"] = max(mix.get("crickets", 0.0), 0.40)
        mix["wind"] = max(mix.get("wind", 0.0), 0.10)

    # instantiate generators
    wind = Wind(mix["wind"]) if mix["wind"] > 0 else None
    rain = Rain(mix["rain"]) if mix["rain"] > 0 else None
    ocean = Ocean(mix["ocean"]) if mix["ocean"] > 0 else None
    water = WaterStream(mix["water"]) if mix["water"] > 0 else None
    fire = Fire(mix["fire"]) if mix["fire"] > 0 else None
    birds = Birds(mix["birds"]) if mix["birds"] > 0 else None
    thunder = Thunder(mix["thunder"]) if mix.get("thunder", 0) > 0 else None
    crickets = Crickets(mix.get("crickets", 0) * 1.2, mix.get("crickets", 0) * 0.5) if mix.get("crickets", 0) > 0 else None
    pink = PinkNoise() if mix["pink"] > 0 else None
    brown = BrownNoise() if mix["brown"] > 0 else None
    bowls = SingingBowl(mix.get("bowls", 0)) if mix.get("bowls", 0) > 0 else None
    heartbeat = Heartbeat(60.0, mix.get("heartbeat", 0)) if mix.get("heartbeat", 0) > 0 else None
    chimes = WindChimes(mix.get("chimes", 0) * 0.8, mix.get("chimes", 0) * 0.5) if mix.get("chimes", 0) > 0 else None
    bytebeat = (BytebeatAmbient(
        intensity=0.30 if mode == "pure_bytebeat" else mix.get("bytebeat", 0.0),
        mode=seed % 5)
        if (mode == "pure_bytebeat" or mix.get("bytebeat", 0.0) > 0) else None)
    binaural = (
        Binaural(200.0, 4.0) if mode == "pure_theta" else
        Binaural(200.0, 10.0) if mode == "pure_alpha" else
        Binaural(200.0, 2.0) if mode == "pure_delta" else
        None)

    vinyl = VinylTexture() if "vinyl" in flags else None
    tape_l = TapeProcessor() if "tape" in flags else None
    tape_r = TapeProcessor() if "tape" in flags else None

    reverb_l = Reverb(size=1.1, damp=0.50,
                      mix=0.28 if mode != "pure_bytebeat" else 0.35)
    reverb_r = Reverb(size=1.16, damp=0.54,
                      mix=0.28 if mode != "pure_bytebeat" else 0.35)
    bb_lp_l = OnePole(2400.0)
    bb_lp_r = OnePole(2200.0)

    width = CFG["stereo_width"]
    if "wide" in flags:
        width = min(2.0, width * 1.35)
    if "narrow" in flags:
        width = max(0.3, width * 0.65)
    mg = CFG["master_gain"]
    md = CFG["master_drive"]
    progress_mark = -1

    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)

        for chunk_start in range(0, total_samples, CHUNK):
            chunk_end = min(chunk_start + CHUNK, total_samples)
            chunk_size = chunk_end - chunk_start
            frames = bytearray(chunk_size * 4)
            fi = 0

            for i in range(chunk_start, chunk_end):
                t = i * INV_SR
                l = 0.0
                r = 0.0

                if wind:
                    v = wind.sample(t)
                    l += v
                    r += v * 0.95
                if rain:
                    v = rain.sample(t)
                    l += v
                    r += v * 1.03
                if ocean:
                    v = ocean.sample(t)
                    l += v
                    r += v * 0.97
                if water:
                    v = water.sample(t)
                    l += v * 0.9
                    r += v
                if fire:
                    v = fire.sample(t)
                    l += v * 0.9
                    r += v * 1.1
                if birds:
                    v = birds.sample(t)
                    l += v * (0.7 + _rand() * 0.3)
                    r += v * (0.7 + _rand() * 0.3)
                if thunder:
                    v = thunder.sample(t)
                    l += v
                    r += v * 0.92
                if crickets:
                    v = crickets.sample(t)
                    l += v * 0.9
                    r += v * 1.1
                if mix["white"] > 0:
                    v = _uniform(-1.0, 1.0) * mix["white"] * 0.25
                    l += v
                    r += v
                if pink:
                    v = pink.sample() * mix["pink"] * 0.30
                    l += v
                    r += v
                if brown:
                    v = brown.sample() * mix["brown"] * 0.38
                    l += v
                    r += v
                if bowls:
                    v = bowls.sample(t)
                    l += v
                    r += v
                if heartbeat:
                    v = heartbeat.sample(t)
                    l += v
                    r += v
                if chimes:
                    v = chimes.sample(t)
                    l += v * 0.85
                    r += v * 1.15
                if bytebeat:
                    v = bytebeat.sample(t)
                    l += bb_lp_l.lp(v * 0.95)
                    r += bb_lp_r.lp(v * 1.05)
                if binaural:
                    bl, br = binaural.sample()
                    l += bl * mix["binaural"] * 0.25
                    r += br * mix["binaural"] * 0.25

                l = reverb_l.process(l)
                r = reverb_r.process(r)

                if vinyl:
                    tex = vinyl.sample()
                    l += tex
                    r += tex * (1.0 + _uniform(-0.15, 0.15))
                if tape_l:
                    l = tape_l.process(l)
                    r = tape_r.process(r)

                mid = (l + r) * 0.5
                side = (l - r) * 0.5 * width
                l = mid + side
                r = mid - side
                l = soft_clip(l, md) * mg
                r = soft_clip(r, md) * mg
                l = clamp(l, -0.999, 0.999)
                r = clamp(r, -0.999, 0.999)

                struct.pack_into("<hh", frames, fi,
                                int(l * 32767), int(r * 32767))
                fi += 4

            w.writeframes(frames)

            pct = int((chunk_end / total_samples) * 100)
            step = CFG["progress_step_percent"]
            if pct != progress_mark and pct % step == 0:
                print(f"  Rendering {pct}%")
                progress_mark = pct

    if mp3:
        maybe_make_mp3(path)


# ─── CLI & INTERACTIVE ──────────────────────────────────────────────────────

def build_parser():
    p = argparse.ArgumentParser(
        description="FREEFLOW v2 — Pure Python Music + Soundscape Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  python freeflow.py --mode ambient --duration 120
  python freeflow.py --prompt "dark drone +vinyl +tape 80 bpm C3 minor"
  python freeflow.py --mode synthwave --bpm 100 +vinyl
  python freeflow.py --mode pure_storm --duration 300
  python freeflow.py --random --duration 60
  python freeflow.py --list
""")
    p.add_argument("--mode", type=str, default=None,
                   help="Mode / preset name")
    p.add_argument("--prompt", type=str, default=None,
                   help="Free-text prompt (mode, flags, bpm, key, scale, duration)")
    p.add_argument("--duration", type=int, default=None,
                   help="Duration in seconds")
    p.add_argument("--bpm", type=int, default=None,
                   help="Beats per minute")
    p.add_argument("--scale", type=str, default=None,
                   help="Scale (minor, pentatonic, blues, ...)")
    p.add_argument("--root", type=str, default=None,
                   help="Root note (C3, A#2, Eb4, ...)")
    p.add_argument("--seed", type=int, default=None,
                   help="Random seed for reproducibility")
    p.add_argument("--out", type=str, default=None,
                   help="Output folder")
    p.add_argument("--mp3", action="store_true",
                   help="Also export mp3 (needs ffmpeg)")
    p.add_argument("--test", action="store_true",
                   help="Quick 5-second smoke test")
    p.add_argument("--random", action="store_true",
                   help="Pick a random mode")
    p.add_argument("--list", action="store_true",
                   help="List all available modes and flags")
    return p


def list_modes():
    print("\n  FREEFLOW v2 — Available Modes\n")
    print("  MUSIC MODES:")
    for k in sorted(GENRES):
        g = GENRES[k]
        print(f"    {k:18s}  bpm {g['bpm'][0]}-{g['bpm'][1]}  "
              f"scale={g['scale']}  drums={'yes' if g['drums'] else 'no'}")
    print("\n  PURE / SOUNDSCAPE MODES:")
    cats = {
        "Nature": ["pure_nature", "pure_wind", "pure_rain", "pure_ocean",
                    "pure_water", "pure_fire", "pure_birds", "pure_storm", "pure_night"],
        "Noise": ["pure_white", "pure_pink", "pure_brown"],
        "Tonal": ["pure_theta", "pure_alpha", "pure_delta",
                   "pure_bowls", "pure_heartbeat", "pure_chimes"],
        "Algorithmic": ["pure_bytebeat"],
    }
    for cat, modes in cats.items():
        print(f"    {cat}: {', '.join(modes)}")
    print("\n  FLAGS (append to prompt or command line):")
    print("    +vinyl +tape +nature +drums +nodrums +binaural +bytebeat")
    print("    +bright +dark +warm +cold +wide +narrow +dense +sparse")
    print("    +bowls +chimes +storm +heartbeat +night\n")


def _is_double_click():
    return os.name == "nt" and len(sys.argv) == 1


def _pause(msg="Press Enter to close..."):
    try:
        input(msg)
    except Exception:
        pass


def interactive_menu():
    """Simple text menu for no-args / double-click launch."""
    print(f"""
╔══════════════════════════════════════════════════════╗
║         FREEFLOW v{__version__}                             ║
║    Pure Python Music + Soundscape Engine             ║
╚══════════════════════════════════════════════════════╝
""")
    all_modes = sorted(GENRES.keys()) + sorted(PURE_MODES)
    print("  Available modes:\n")
    for i, m in enumerate(all_modes, 1):
        tag = "[music]" if m in GENRES else "[sound]"
        print(f"    {i:2d}. {m:22s} {tag}")
    print(f"\n    {len(all_modes)+1:2d}. RANDOM (surprise me)")
    print(f"    {len(all_modes)+2:2d}. QUIT\n")

    try:
        choice = input("  Choose a number (or type a mode name): ").strip()
    except (EOFError, KeyboardInterrupt):
        return None, None, None

    if not choice:
        return "ambient", set(), 180

    # number selection
    try:
        num = int(choice)
        if num == len(all_modes) + 2:
            return None, None, None
        if num == len(all_modes) + 1:
            mode = random.choice(all_modes)
        elif 1 <= num <= len(all_modes):
            mode = all_modes[num - 1]
        else:
            print("  Invalid choice, using ambient.")
            mode = "ambient"
    except ValueError:
        # treat as prompt text
        pd = parse_prompt(choice)
        mode = pd["mode"] or "ambient"
        flags = pd["flags"]
        dur = pd["duration"] or 180
        return mode, flags, dur

    # duration
    try:
        dur_input = input("  Duration in seconds [180]: ").strip()
        dur = int(dur_input) if dur_input else 180
    except (EOFError, KeyboardInterrupt, ValueError):
        dur = 180

    # flags
    try:
        flag_input = input("  Flags (e.g. +vinyl +tape +warm) [none]: ").strip()
        flags = set()
        if flag_input:
            for tok in flag_input.split():
                f = FLAG_ALIASES.get(tok.lower())
                if f:
                    flags.add(f)
    except (EOFError, KeyboardInterrupt):
        flags = set()

    return mode, flags, dur


def main():
    double_click = _is_double_click()
    no_args = len(sys.argv) == 1

    parser = build_parser()
    argv = []
    plus_bits = []
    for a in sys.argv[1:]:
        if a.startswith('+'):
            plus_bits.append(a)
        else:
            argv.append(a)
    args = parser.parse_args(argv)

    if args.list:
        list_modes()
        return

    # interactive mode if no args
    if no_args:
        mode, flags, duration = interactive_menu()
        if mode is None:
            print("  Goodbye.")
            return
        seed = int(time.time() * 1000) % (2 ** 32)
        random.seed(seed)
        bpm = None
        root = None
        scale = None
        mp3 = False
        out_dir = Path(CFG["output_dir"]).expanduser()
    else:
        seed = args.seed if args.seed is not None else int(time.time() * 1000) % (2 ** 32)
        random.seed(seed)

        prompt_text = args.prompt or ''
        if plus_bits:
            prompt_text = (prompt_text + ' ' + ' '.join(plus_bits)).strip()

        prompt_data = (parse_prompt(prompt_text) if prompt_text
                       else {"mode": None, "flags": set(), "bpm": None,
                             "duration": None, "root": None, "scale": None})

        mode = args.mode or prompt_data["mode"] or CFG["default_mode"]
        flags = set(prompt_data["flags"])
        duration = (5 if args.test
                    else (args.duration or prompt_data["duration"]
                          or CFG["default_duration"]))
        bpm = args.bpm or prompt_data["bpm"]
        root = note_name_to_midi(args.root) if args.root else prompt_data["root"]
        scale = args.scale or prompt_data["scale"]
        mp3 = args.mp3
        out_dir = Path(args.out or CFG["output_dir"]).expanduser()

        if args.random and not args.mode and not prompt_data["mode"]:
            mode = random.choice(list(GENRES.keys()) + list(PURE_MODES))

    if mode is None:
        mode = CFG["default_mode"]

    # fuzzy match unknown modes
    if mode not in GENRES and mode not in PURE_MODES:
        all_valid = list(GENRES.keys()) + list(PURE_MODES)
        close = difflib.get_close_matches(mode, all_valid, n=1, cutoff=0.55)
        if close:
            print(f"  Unknown mode '{mode}' → using closest: '{close[0]}'")
            mode = close[0]
        else:
            print(f"  Unknown mode '{mode}' → using default: '{CFG['default_mode']}'")
            mode = CFG["default_mode"]

    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    stem = f"{CFG['filename_prefix']}_{mode}_{seed}_{ts}"
    wav_path = out_dir / f"{stem}.wav"

    print(f"\n  FREEFLOW v{__version__}")
    print(f"  Seed:     {seed}")
    print(f"  Mode:     {mode}")
    if flags:
        print(f"  Flags:    {' '.join(sorted(flags))}")

    t_start = time.time()

    if mode in PURE_MODES:
        duration = duration or CFG["default_duration"]
        print(f"  Duration: {duration}s")
        render_pure_to_wav(wav_path, mode, duration, seed,
                           flags=flags, mp3=mp3)
    else:
        rng = random.Random(seed)
        events, duration, bpm, root, scale = generate_music_events(
            mode, rng, bpm=bpm, root=root, scale_name=scale,
            duration=duration, flags=flags)
        print(f"  BPM:      {bpm}")
        print(f"  Root:     {midi_to_name(root)}")
        print(f"  Scale:    {scale}")
        print(f"  Duration: {duration}s")
        print(f"  Events:   {len(events)}")
        render_music_to_wav(wav_path, events, duration, mode, bpm,
                            flags=flags, mp3=mp3)

    elapsed = time.time() - t_start
    print(f"\n  Saved WAV: {wav_path}")
    print(f"  Rendered in {elapsed:.1f}s "
          f"({duration / max(elapsed, 0.001):.1f}x realtime)\n")

    if double_click:
        _pause("  Done. Press Enter to close...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n  Interrupted.")
    except Exception as e:
        print(f"\n  CRASH: {repr(e)}")
        print(traceback.format_exc())
        if os.name == "nt":
            _pause()