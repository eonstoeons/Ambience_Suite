#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  FREEFLOW CORE v1.0    —  Terminal-Only Cosmic Soundscape Engine            ║
║  Zero external dependencies. Python 3.8+ stdlib only.                      ║
║   > If one day, someone looks at this and asks why – tell them we ran out of answers down here, so we looked up to the stars.                                                                           ║
║  Sound generated from mathematics, music theory, and deep space data.       ║
║  No AI. No training data. No human or living-organism sources.              ║
║  No internet. No external libraries. Runs on any device.                    ║
║                                                                              ║
║  Data source: COSMIC_OBJECTS — a built-in catalog of stellar,               ║
║  nebular, and galactic measurements drawn from public astronomical           ║
║  observation records (temperature, luminosity, distance, mass).             ║
║  These numbers seed the synthesis engine. No biology. No culture.           ║
║  Only the universe.                                                          ║
║                                                                              ║
║  Features:                                                                   ║
║  • 10 music modes + 19 pure soundscape modes                                ║
║  • Nature synthesis: wind, rain, ocean, water, fire, thunder                ║
║  • Instruments: pads, bells, plucks, flutes, supersaw, FM, karplus,organ   ║
║  • Effects: reverb (Freeverb 8-comb), delay, chorus, vinyl, tape            ║
║  • Geological entity simulation: mountains, glaciers, canyons, dunes        ║
║  • Cosmic entity simulation: nebulae, stellar objects, deep field           ║
║  • Mood & Environment presets                                                ║
║  • Quality modes: mobile / balanced / studio                                ║
║  • Terminal-only CLI + quick interactive menu                                ║
║  • Preset save/load (JSON), reproducible seeds                              ║
║  • WAV output 44.1 kHz 16-bit stereo, optional MP3 via ffmpeg              ║
║  • Built-in COSMIC_OBJECTS dataset seeds generative parameters              ║
║  • Optional override: place cosmic.json in same folder                      ║
║                                                                              ║
║  Usage:                                                                      ║
║    python freeflow_aurora.py                    # CLI usage                  ║
║    python freeflow_core.py --mode ambient       # specific mode             ║
║    python freeflow_core.py --cosmic             # cosmic seed mode          ║
║    python freeflow_core.py --object Rigel       # specific cosmic object    ║
║    python freeflow_core.py --random --duration 60                           ║
║    python freeflow_core.py --list                                           ║
║    python freeflow_core.py --test                                           ║
║                                                                              ║
║  License: MIT  |  Author: FREEFLOW Project  |  Version: 1.0.0              ║
╚══════════════════════════════════════════════════════════════════════════════╝

MIT License

Copyright (c) 2026 FREEFLOW Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import argparse
import difflib
import json
import math
import os
import random
import re
import shutil
import struct
import subprocess
import sys
import time
import traceback
import wave
from pathlib import Path

__version__ = "1.0.0"
__author__  = "FREEFLOW Project"
__license__ = "MIT"

# ─── COSMIC DATASET ─────────────────────────────────────────────────────────
# All values are derived from publicly available astronomical observation data.
# Sources: NASA/IPAC, ESA Gaia, Hipparcos catalogue, Simbad, NED.
# No living organisms, no human cultural data, no sampled audio.
# Temperature in Kelvin. Luminosity in solar units. Distance in light-years.
# Mass in solar masses. Each object is inanimate. Each value is a number.
# These numbers are translated into synthesis parameters. Pure mathematics.

COSMIC_OBJECTS = [
    # ── Stars ──────────────────────────────────────────────────────────────
    {"name":"Sirius A",      "type":"star","temp":9940,  "lum":25.4,   "dist":8.6,    "mass":2.02},
    {"name":"Vega",          "type":"star","temp":9600,  "lum":40.1,   "dist":25.0,   "mass":2.14},
    {"name":"Arcturus",      "type":"star","temp":4286,  "lum":170.0,  "dist":36.7,   "mass":1.08},
    {"name":"Rigel",         "type":"star","temp":12100, "lum":120000, "dist":860.0,  "mass":21.0},
    {"name":"Betelgeuse",    "type":"star","temp":3500,  "lum":126000, "dist":700.0,  "mass":16.5},
    {"name":"Antares",       "type":"star","temp":3660,  "lum":75900,  "dist":550.0,  "mass":12.4},
    {"name":"Polaris",       "type":"star","temp":6015,  "lum":2500,   "dist":433.0,  "mass":5.4},
    {"name":"Deneb",         "type":"star","temp":8525,  "lum":196000, "dist":2600.0, "mass":19.0},
    {"name":"Canopus",       "type":"star","temp":7400,  "lum":10700,  "dist":310.0,  "mass":8.5},
    {"name":"Aldebaran",     "type":"star","temp":3910,  "lum":518.0,  "dist":65.0,   "mass":1.16},
    {"name":"Spica",         "type":"star","temp":25300, "lum":20500,  "dist":250.0,  "mass":11.4},
    {"name":"Fomalhaut",     "type":"star","temp":8590,  "lum":16.6,   "dist":25.1,   "mass":1.92},
    {"name":"Proxima Cen",   "type":"star","temp":3042,  "lum":0.0017, "dist":4.24,   "mass":0.12},
    {"name":"Tau Ceti",      "type":"star","temp":5344,  "lum":0.52,   "dist":11.9,   "mass":0.78},
    {"name":"Epsilon Eri",   "type":"star","temp":5084,  "lum":0.34,   "dist":10.5,   "mass":0.82},
    {"name":"61 Cygni A",    "type":"star","temp":4526,  "lum":0.15,   "dist":11.4,   "mass":0.70},
    {"name":"Barnards Star", "type":"star","temp":3134,  "lum":0.0035, "dist":5.96,   "mass":0.17},
    {"name":"Altair",        "type":"star","temp":7550,  "lum":10.6,   "dist":16.7,   "mass":1.79},
    {"name":"Procyon A",     "type":"star","temp":6530,  "lum":6.93,   "dist":11.5,   "mass":1.50},
    {"name":"Castor A",      "type":"star","temp":8840,  "lum":34.0,   "dist":51.5,   "mass":2.76},
    # ── Nebulae ────────────────────────────────────────────────────────────
    {"name":"Orion Nebula",  "type":"nebula","temp":10000, "lum":400000,"dist":1344,  "mass":2000},
    {"name":"Helix Nebula",  "type":"nebula","temp":120000,"lum":300,   "dist":650,   "mass":0.6},
    {"name":"Crab Nebula",   "type":"nebula","temp":11000, "lum":100000,"dist":6500,  "mass":10},
    {"name":"Ring Nebula",   "type":"nebula","temp":120000,"lum":200,   "dist":2300,  "mass":1.1},
    {"name":"Eagle Nebula",  "type":"nebula","temp":30000, "lum":300000,"dist":7000,  "mass":5000},
    {"name":"Lagoon Nebula", "type":"nebula","temp":8500,  "lum":280000,"dist":4100,  "mass":500},
    {"name":"Trifid Nebula", "type":"nebula","temp":9000,  "lum":100000,"dist":5200,  "mass":400},
    {"name":"Rosette Nebula","type":"nebula","temp":35000, "lum":500000,"dist":5200,  "mass":10000},
    {"name":"Pillars Creat", "type":"nebula","temp":8000,  "lum":200000,"dist":7000,  "mass":900},
    {"name":"Horsehead Neb", "type":"nebula","temp":50,    "lum":0.001, "dist":1500,  "mass":100},
    # ── Galaxies & Deep Field ──────────────────────────────────────────────
    {"name":"Andromeda",     "type":"galaxy","temp":5000,  "lum":2.6e10,"dist":2537000,"mass":1.5e12},
    {"name":"Triangulum",    "type":"galaxy","temp":6000,  "lum":1.4e9, "dist":2730000,"mass":5e10},
    {"name":"Sombrero",      "type":"galaxy","temp":5500,  "lum":8e10,  "dist":28000000,"mass":8e11},
    {"name":"Whirlpool",     "type":"galaxy","temp":7000,  "lum":2.5e10,"dist":23000000,"mass":1.6e11},
    {"name":"Pinwheel",      "type":"galaxy","temp":6500,  "lum":1.3e10,"dist":21000000,"mass":1e12},
    # ── Remnants & Exotica ────────────────────────────────────────────────
    {"name":"Vela Pulsar",   "type":"remnant","temp":1000000,"lum":11000,"dist":1000, "mass":1.86},
    {"name":"Crab Pulsar",   "type":"remnant","temp":2000000,"lum":200000,"dist":6500,"mass":1.4},
    {"name":"Cassiopeia A",  "type":"remnant","temp":20000, "lum":10000, "dist":11000, "mass":5},
    {"name":"Tycho SNR",     "type":"remnant","temp":15000, "lum":5000,  "dist":9800,  "mass":3},
]

# ─── COSMIC DATA INTEGRATION ─────────────────────────────────────────────────

def get_cosmic_object(name=None):
    """
    Return a cosmic object dict.
    Priority: cosmic.json override → named object → random from dataset.
    All values are inanimate astronomical measurements.
    """
    if os.path.exists("cosmic.json"):
        try:
            with open("cosmic.json") as f:
                data = json.load(f)
            print(f"  [Aurora] Using cosmic.json override: {data.get('name','custom')}")
            return data
        except Exception:
            pass
    if name:
        nl = name.lower()
        for obj in COSMIC_OBJECTS:
            if obj["name"].lower() == nl or nl in obj["name"].lower():
                return obj
        print(f"  [Aurora] Object '{name}' not found — using random cosmic object.")
    return random.choice(COSMIC_OBJECTS)

def cosmic_to_params(obj):
    """
    Map inanimate astronomical measurements to synthesis parameters.

    Temperature (K):
      < 4000  → drone / dark_ambient  (cool red giants, dark nebulae)
      4000-7000 → ambient / meditation (sun-like, stable stars)
      7000-12000 → bellscape / sacred  (white-blue main sequence)
      12000-30000 → cosmic             (hot blue giants)
      > 30000 or pulsar → experimental (extreme objects)

    Luminosity → reverb mix, density, pad volume
    Distance   → delay time, stereo width
    Mass       → bass weight, BPM
    """
    temp = obj.get("temp", 6000)
    lum  = obj.get("lum", 1.0)
    dist = obj.get("dist", 100.0)
    mass = obj.get("mass", 1.0)

    # Mode from temperature
    if temp < 100:           mode = "drone";        mood = "somber"
    elif temp < 4000:        mode = "dark_ambient";  mood = "melancholic"
    elif temp < 6000:        mode = "ambient";       mood = "peaceful"
    elif temp < 7500:        mode = "meditation";    mood = "ethereal"
    elif temp < 12000:       mode = "bellscape";     mood = "mysterious"
    elif temp < 30000:       mode = "cosmic";        mood = "ethereal"
    else:                    mode = "experimental";  mood = "intense"

    # Luminosity → density (log-scaled, clamped)
    log_lum = math.log10(max(lum, 0.0001))
    density = max(0.05, min(0.90, (log_lum + 4) / 14.0))

    # Distance → stereo width (far = wider)
    log_dist = math.log10(max(dist, 1.0))
    width = max(0.6, min(2.0, 0.6 + log_dist * 0.18))

    # Mass → BPM (heavier = slower, lighter = faster)
    log_mass = math.log10(max(mass, 0.001))
    bpm = int(max(38, min(120, 62 - log_mass * 4)))

    flags = set()
    if temp < 4000:  flags.add("sparse")
    if temp > 20000: flags.add("bright")
    if lum > 10000:  flags.add("wide")
    if dist > 50000: flags.add("sparse")

    return {
        "mode":  mode,
        "mood":  mood,
        "bpm":   bpm,
        "flags": flags,
        "_cosmic_source": obj.get("name", "unknown"),
        "_cosmic_temp":   temp,
        "_cosmic_lum":    lum,
        "_cosmic_dist":   dist,
    }

def apply_cosmic_seed(params, object_name=None):
    """
    If --cosmic or --object is set, derive synthesis params from cosmic data.
    Does not override user-set mode if explicitly provided via CLI.
    """
    obj    = get_cosmic_object(object_name)
    mapped = cosmic_to_params(obj)
    print(f"  [Aurora] Cosmic seed: {obj['name']} | "
          f"T={obj.get('temp',0):,}K | "
          f"L={obj.get('lum',0):.2g}☉ | "
          f"d={obj.get('dist',0):,.0f}ly")
    if not params.get("_mode_explicit"):
        params["mode"] = mapped["mode"]
        params["mood"] = mapped["mood"]
    if not params.get("bpm"):
        params["bpm"] = mapped["bpm"]
    existing_flags = set(params.get("flags", set()))
    params["flags"] = existing_flags | mapped["flags"]
    params["_cosmic_source"] = mapped["_cosmic_source"]
    return params

# ─── CONSTANTS & CONFIG ──────────────────────────────────────────────────────

SR      = 44100
INV_SR  = 1.0 / SR
TAU     = math.tau
_PI     = math.pi
NYQUIST = SR * 0.5
CHUNK   = SR * 10   # 10-second render chunks

_sin     = math.sin
_cos     = math.cos
_exp     = math.exp
_tanh    = math.tanh
_sqrt    = math.sqrt
_rand    = random.random
_gauss   = random.gauss
_uniform = random.uniform

# ─── SIN LOOKUP TABLE ────────────────────────────────────────────────────────

_SIN_N = 4096
_SIN_T = [math.sin(i * TAU / _SIN_N) for i in range(_SIN_N)]

def fast_sin(phase):
    """Table-interpolated sine — ~3x faster than math.sin in tight loops."""
    p = (phase % TAU) * (_SIN_N / TAU)
    i = int(p) & (_SIN_N - 1)
    f = p - int(p)
    return _SIN_T[i] + (_SIN_T[(i + 1) & (_SIN_N - 1)] - _SIN_T[i]) * f

# ─── QUALITY PROFILES ────────────────────────────────────────────────────────

QUALITY = {
    "mobile":   {"max_voices":4,  "reverb_combs":4, "max_chimes":6,  "bytebeat_sr":4000, "label":"Mobile"},
    "balanced": {"max_voices":12, "reverb_combs":6, "max_chimes":10, "bytebeat_sr":8000, "label":"Balanced"},
    "studio":   {"max_voices":32, "reverb_combs":8, "max_chimes":12, "bytebeat_sr":8000, "label":"Studio"},
}

_Q = dict(QUALITY["balanced"])

def set_quality(name):
    global _Q
    _Q = dict(QUALITY.get(name, QUALITY["balanced"]))

# ─── HELPERS ─────────────────────────────────────────────────────────────────

def clamp(x, lo=-1.0, hi=1.0):
    return lo if x < lo else (hi if x > hi else x)

def soft_clip(x, drive=1.10):
    d = _tanh(drive)
    return _tanh(x * drive) / d if d else x

def lerp(a, b, t):
    return a + (b - a) * t

def mtof(note):
    return 440.0 * (2.0 ** ((note - 69.0) / 12.0))

NOTE_NAMES = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]

def note_name_to_midi(name):
    s = name.strip().upper()
    if not s: return 48
    base_map = {"C":0,"D":2,"E":4,"F":5,"G":7,"A":9,"B":11}
    if s[0] not in base_map: return 48
    base = base_map[s[0]]; idx = 1
    if len(s) > 1 and s[1] == "#":        base += 1; idx = 2
    elif len(s) > 1 and s[1] in ("B","b"): base -= 1; idx = 2
    try:    octave = int(s[idx:])
    except: octave = 3
    return (octave + 1) * 12 + base

def midi_to_name(midi):
    return f"{NOTE_NAMES[midi % 12]}{midi // 12 - 1}"

def humanize(t, amt=0.004):
    return t + _gauss(0.0, amt)

def parse_duration_text(text):
    if not text: return None
    m = re.search(r'(\d+)\s*(seconds?|sec|s\b|minutes?|min|m\b|hours?|hr|h\b)', text, re.I)
    if not m: return None
    n = int(m.group(1)); u = m.group(2).lower()
    if u.startswith('h'): return n * 3600
    if u.startswith('m'): return n * 60
    return n

# ─── DC BLOCKER ──────────────────────────────────────────────────────────────

class DCBlocker:
    __slots__ = ("xm1","ym1","R")
    def __init__(self, R=0.995):
        self.xm1 = 0.0; self.ym1 = 0.0; self.R = R
    def process(self, x):
        y = x - self.xm1 + self.R * self.ym1
        self.xm1 = x; self.ym1 = y
        return y

# ─── DSP FILTERS ─────────────────────────────────────────────────────────────

class SVF:
    __slots__ = ("lp","bp","hp","_f","_q")
    def __init__(self, cutoff=1000.0, res=0.0):
        self.lp = self.bp = self.hp = 0.0
        self._f = 0.0; self._q = 1.0
        self.set(cutoff, res)
    def set(self, cutoff, res=None):
        cutoff = min(max(20.0, cutoff), NYQUIST * 0.95)
        self._f = 2.0 * _sin(_PI * cutoff * INV_SR)
        if res is not None:
            self._q = 1.0 - min(max(0.0, res), 0.97)
    def lp_process(self, x):
        hp = x - self.lp - self._q * self.bp
        self.bp += self._f * hp
        self.lp += self._f * self.bp
        self.hp = hp
        return self.lp
    def hp_process(self, x):
        self.lp_process(x); return self.hp
    def bp_process(self, x):
        self.lp_process(x); return self.bp

class OnePole:
    __slots__ = ("a","z")
    def __init__(self, cutoff=1000.0):
        self.z = 0.0; self.set(cutoff)
    def set(self, cutoff):
        self.a = 1.0 - _exp(-TAU * min(max(cutoff, 1.0), NYQUIST * 0.99) * INV_SR)
    def lp(self, x):
        self.z += self.a * (x - self.z); return self.z
    def hp(self, x):
        return x - self.lp(x)

class ADSR:
    __slots__ = ("a","d","s","r")
    def __init__(self, a=0.01, d=0.1, s=0.7, r=0.3):
        self.a = max(a,0.001); self.d = max(d,0.001)
        self.s = s; self.r = max(r,0.001)
    def get(self, t, dur):
        if t < 0:             return 0.0
        if t < self.a:        return t / self.a
        if t < self.a+self.d: return 1.0 - (1.0-self.s)*((t-self.a)/self.d)
        if t < dur:           return self.s
        rt = t - dur
        if rt < self.r:       return self.s * (1.0 - rt/self.r)
        return 0.0

# ─── OSC PRIMITIVES ──────────────────────────────────────────────────────────

def osc_tri(phase):
    p = (phase % TAU) / TAU
    return 4.0 * abs(p - 0.5) - 1.0

def osc_pulse(phase, pw=0.5):
    return 1.0 if ((phase % TAU) / TAU) < pw else -1.0

def osc_saw_blep(phase, freq):
    t = (phase % TAU) / TAU; v = 2.0 * t - 1.0; dt = freq * INV_SR
    if dt <= 0: return v
    if t < dt:
        x = t/dt; v -= x+x - x*x - 1.0
    elif t > 1.0 - dt:
        x = (t-1.0)/dt; v -= x+x + x*x + 1.0
    return v

def osc_square_blep(phase, freq):
    t = (phase % TAU) / TAU; v = 1.0 if t < 0.5 else -1.0; dt = freq * INV_SR
    if dt <= 0: return v
    if t < dt:
        x = t/dt; v += x+x - x*x - 1.0
    elif t > 1.0-dt:
        x = (t-1.0)/dt; v -= x+x + x*x + 1.0
    t2 = (t+0.5) % 1.0
    if t2 < dt:
        x = t2/dt; v -= x+x - x*x - 1.0
    elif t2 > 1.0-dt:
        x = (t2-1.0)/dt; v += x+x + x*x + 1.0
    return v

# ─── VOICE ENGINES ───────────────────────────────────────────────────────────

class SuperSaw:
    __slots__ = ("phases","incs","mix","freq")
    def __init__(self, freq, detune=0.30, mix=0.82):
        spreads = [-0.03,-0.02,-0.01,0.0,0.01,0.02,0.03]
        self.phases = [_uniform(0,TAU) for _ in range(7)]
        self.incs   = [TAU*freq*(1.0+detune*s)*INV_SR for s in spreads]
        self.mix = mix / 7.0; self.freq = freq
    def sample(self, t=0.0, env=1.0):
        v = 0.0; ph = self.phases; inc = self.incs; fr = self.freq
        for i in range(7):
            ph[i] += inc[i]; v += osc_saw_blep(ph[i], fr)
        return v * self.mix

class FMSynth:
    __slots__ = ("car_inc","mod_inc","depth","fb","pc","pm","prev")
    def __init__(self, freq, ratio=2.0, depth=1.4, feedback=0.12):
        self.car_inc = TAU*freq*INV_SR; self.mod_inc = TAU*freq*ratio*INV_SR
        self.depth = depth; self.fb = feedback
        self.pc = 0.0; self.pm = 0.0; self.prev = 0.0
    def sample(self, t=0.0, env=1.0):
        mod = fast_sin(self.pm + self.prev*self.fb) * self.depth
        self.pm += self.mod_inc
        out = fast_sin(self.pc + mod)
        self.pc += self.car_inc; self.prev = out
        return out

class SubSynth:
    __slots__ = ("phase","inc","wave","filt","env_depth","base_cut","freq")
    def __init__(self, freq, wave="saw", cutoff=2000.0, res=0.22, env_depth=2500.0):
        self.phase = _uniform(0,TAU); self.inc = TAU*freq*INV_SR
        self.wave = wave; self.filt = SVF(cutoff, res)
        self.env_depth = env_depth; self.base_cut = cutoff; self.freq = freq
    def sample(self, t=0.0, env=1.0):
        self.phase += self.inc; w = self.wave
        if   w == "saw":    v = osc_saw_blep(self.phase, self.freq)
        elif w == "square": v = osc_square_blep(self.phase, self.freq)
        elif w == "tri":    v = osc_tri(self.phase)
        elif w == "pulse":  v = osc_pulse(self.phase, 0.35+0.15*fast_sin(TAU*0.45*t))
        else:               v = fast_sin(self.phase)
        self.filt.set(min(self.base_cut + self.env_depth*env, NYQUIST*0.95))
        return self.filt.lp_process(v)

class KarplusStrong:
    __slots__ = ("buf","idx","decay","bright")
    def __init__(self, freq, decay=0.996, brightness=0.55):
        period = max(int(SR / max(freq, 24.0)), 2)
        self.buf = [_uniform(-1,1) for _ in range(period)]
        self.idx = 0; self.decay = decay
        self.bright = 1.0 - brightness*0.7
    def sample(self, t=0.0, env=1.0):
        buf = self.buf; L = len(buf)
        i = self.idx % L; j = (i+1) % L
        out = buf[i]
        buf[i] = (buf[i]+buf[j]) * 0.5 * self.bright * self.decay
        self.idx += 1; return out

class Pad:
    __slots__ = ("phases","incs","lfo","lfo_inc","n")
    def __init__(self, notes, detune=0.005):
        phases = []; incs = []
        for n in notes:
            f = mtof(n)
            for d in (-detune, 0.0, detune):
                phases.append(_uniform(0,TAU))
                incs.append(TAU*f*(1.0+d)*INV_SR)
        self.phases = phases; self.incs = incs
        self.lfo = _uniform(0,TAU); self.lfo_inc = TAU*0.16*INV_SR
        self.n = len(phases)
    def sample(self, t=0.0, env=1.0):
        self.lfo += self.lfo_inc
        mod = 0.7 + 0.3*(0.5 + 0.5*fast_sin(self.lfo))
        v = 0.0; ph = self.phases; inc = self.incs
        for i in range(self.n):
            ph[i] += inc[i]; v += fast_sin(ph[i])
        return (v/self.n)*mod if self.n else 0.0

class Organ:
    __slots__ = ("phase","inc")
    def __init__(self, freq):
        self.phase = 0.0; self.inc = TAU*freq*INV_SR
    def sample(self, t=0.0, env=1.0):
        self.phase += self.inc; p = self.phase
        return (0.60*fast_sin(p) + 0.22*fast_sin(p*2)
                + 0.10*fast_sin(p*3) + 0.06*fast_sin(p*4))

class FluteSynth:
    __slots__ = ("phase","inc","vib_phase","vib_inc","breath_lp","freq")
    def __init__(self, freq):
        self.phase = _uniform(0,TAU); self.inc = TAU*freq*INV_SR
        self.vib_phase = 0.0; self.vib_inc = TAU*5.5*INV_SR
        self.breath_lp = OnePole(4000.0); self.freq = freq
    def sample(self, t=0.0, env=1.0):
        self.vib_phase += self.vib_inc
        vib = fast_sin(self.vib_phase) * 0.012 * min(t*4, 1.0)
        self.phase += self.inc * (1.0 + vib)
        breath = self.breath_lp.lp(_uniform(-1,1)) * 0.08
        return fast_sin(self.phase) * 0.85 + breath

# ─── DRUMS ───────────────────────────────────────────────────────────────────

class Kick808:
    __slots__ = ("punch","decay","tone")
    def __init__(self, punch=1.0, decay=0.40, tone=50.0):
        self.punch=punch; self.decay=decay; self.tone=tone
    def sample(self, t=0.0, env=1.0):
        if t < 0: return 0.0
        pitch = self.tone + 190.0*self.punch*_exp(-30.0*t)
        amp   = _exp(-t / max(self.decay, 0.001))
        click = _exp(-150.0*t) * 0.40*self.punch
        return soft_clip((_sin(TAU*pitch*t)*amp + click)*0.95, 1.25)

class Snare909:
    __slots__ = ("tone","noise_amt","decay","hpf")
    def __init__(self, tone=195.0, noise_amt=0.62, decay=0.18):
        self.tone=tone; self.noise_amt=noise_amt
        self.decay=decay; self.hpf=SVF(2200.0, 0.04)
    def sample(self, t=0.0, env=1.0):
        if t < 0: return 0.0
        te = _exp(-18.0*t); ne = _exp(-t/max(self.decay,0.001))
        tonal = _sin(TAU*self.tone*t)*te*(1.0-self.noise_amt)
        noise = self.hpf.hp_process(_uniform(-1,1))*ne*self.noise_amt
        return soft_clip((tonal+noise)*0.82, 1.35)

class HiHat:
    __slots__ = ("decay","hpf","phases","incs")
    RATIOS = (1.0, 1.342, 1.2312, 1.6532, 1.9523, 2.1523)
    def __init__(self, open_hat=False, decay=0.045):
        self.decay = 0.22 if open_hat else decay
        self.hpf = SVF(7800.0, 0.05)
        self.phases = [0.0]*6
        self.incs = [TAU*420.0*r*INV_SR for r in self.RATIOS]
    def sample(self, t=0.0, env=1.0):
        if t < 0: return 0.0
        amp = _exp(-t/max(self.decay,0.001)); v = 0.0
        for i in range(6):
            self.phases[i] += self.incs[i]
            v += 1.0 if (self.phases[i]%TAU) < _PI else -1.0
        return self.hpf.hp_process(v/6.0)*amp*0.48

class Clap:
    __slots__ = ("decay","bpf")
    def __init__(self, decay=0.14):
        self.decay=decay; self.bpf=SVF(1600.0, 0.55)
    def sample(self, t=0.0, env=1.0):
        if t < 0: return 0.0
        amp = _exp(-t/max(self.decay,0.001)); burst = 0.0
        for off in (0.0, 0.010, 0.021, 0.031):
            bt = t-off
            if bt >= 0: burst += _exp(-90.0*bt)*_uniform(-1,1)
        return self.bpf.bp_process(burst*amp*0.45)

# ─── NOISE GENERATORS ────────────────────────────────────────────────────────

class PinkNoise:
    __slots__ = ("b",)
    def __init__(self): self.b = [0.0]*6
    def sample(self):
        b = self.b; w = _uniform(-1,1)
        b[0]=0.99886*b[0]+w*0.0555179
        b[1]=0.99332*b[1]+w*0.0750759
        b[2]=0.96900*b[2]+w*0.1538520
        b[3]=0.86650*b[3]+w*0.3104856
        b[4]=0.55000*b[4]+w*0.5329522
        b[5]=-0.7616*b[5]-w*0.0168980
        return (b[0]+b[1]+b[2]+b[3]+b[4]+b[5]+w*0.5362)*0.11

class BrownNoise:
    __slots__ = ("z",)
    def __init__(self): self.z = 0.0
    def sample(self):
        self.z = 0.98*self.z + 0.03*_uniform(-1,1)
        return clamp(self.z)

# ─── NATURE GENERATORS ───────────────────────────────────────────────────────

class Wind:
    __slots__ = ("pink","pink2","lfo_b","lfo_g","lfo_s","inc_b","inc_g","inc_s","lp1","hp","bp","intensity")
    def __init__(self, intensity=0.4):
        self.pink = PinkNoise(); self.pink2 = PinkNoise()
        self.lfo_b = _uniform(0,TAU); self.lfo_g = _uniform(0,TAU); self.lfo_s = _uniform(0,TAU)
        self.inc_b = TAU*0.12*INV_SR; self.inc_g = TAU*0.025*INV_SR; self.inc_s = TAU*0.004*INV_SR
        self.lp1 = OnePole(1200.0); self.hp = OnePole(60.0); self.bp = SVF(800.0,0.15)
        self.intensity = intensity
    def sample_stereo(self, t=0.0):
        self.lfo_b+=self.inc_b; self.lfo_g+=self.inc_g; self.lfo_s+=self.inc_s
        breath = 0.5+0.5*fast_sin(self.lfo_b)
        gust   = max(0, fast_sin(self.lfo_g)**3)
        mod    = 0.15+0.45*breath+0.35*gust
        v1 = self.pink.sample(); v2 = self.pink2.sample()
        cut = 600.0+1400.0*gust+400.0*breath
        self.lp1.set(cut); self.bp.set(cut*0.7, 0.12+0.15*gust)
        l = self.hp.hp(self.lp1.lp(v1) + self.bp.bp_process(v1)*0.3*gust)
        r = self.hp.hp(self.lp1.lp(v2) + self.bp.bp_process(v2)*0.25*gust)
        s = mod*self.intensity
        return l*s, r*s*0.93

class Rain:
    __slots__ = ("bed","small_lp","med_lp","heavy_lp","hp","intensity")
    def __init__(self, intensity=0.45):
        self.bed = PinkNoise(); self.small_lp = OnePole(8000.0)
        self.med_lp = OnePole(3500.0); self.heavy_lp = OnePole(1800.0)
        self.hp = OnePole(200.0); self.intensity = intensity
    def sample_stereo(self, t=0.0):
        inten = self.intensity
        bed   = self.hp.hp(self.bed.sample()) * 0.08*inten
        small = self.small_lp.lp(_uniform(-1,1))*_uniform(0.02,0.06)*inten if _rand()<inten*0.06 else 0.0
        med   = self.med_lp.lp(_uniform(-1,1))*_uniform(0.08,0.18)*inten   if _rand()<inten*0.012 else 0.0
        heavy = self.heavy_lp.lp(_uniform(-1,1))*_uniform(0.15,0.30)*inten if _rand()<inten*0.003 else 0.0
        mono  = bed+small+med+heavy
        pan = _uniform(-0.4,0.4); pr = (pan+1.0)*_PI*0.25
        return mono*_cos(pr), mono*_sin(pr)

class Ocean:
    __slots__ = ("pink1","pink2","pink3","foam","lfo1","lfo2","lfo3","inc1","inc2","inc3",
                 "lp1","lp2","lp3","hp","foam_lp","crash_t","crash_amp","crash_dur","intensity")
    def __init__(self, intensity=0.5):
        self.pink1=PinkNoise(); self.pink2=PinkNoise()
        self.pink3=PinkNoise(); self.foam=PinkNoise()
        self.lfo1=_uniform(0,TAU); self.lfo2=_uniform(0,TAU); self.lfo3=_uniform(0,TAU)
        self.inc1=TAU*0.045*INV_SR; self.inc2=TAU*0.11*INV_SR; self.inc3=TAU*0.28*INV_SR
        self.lp1=OnePole(400.0); self.lp2=OnePole(900.0); self.lp3=OnePole(2200.0)
        self.hp=OnePole(25.0); self.foam_lp=OnePole(6000.0)
        self.crash_t=-1.0; self.crash_amp=0.0; self.crash_dur=0.0
        self.intensity=intensity
    def sample_stereo(self, t=0.0):
        self.lfo1+=self.inc1; self.lfo2+=self.inc2; self.lfo3+=self.inc3
        swell  = max(0, fast_sin(self.lfo1))**1.5
        wave2  = 0.5+0.5*fast_sin(self.lfo2)
        ripple = 0.5+0.5*fast_sin(self.lfo3)
        v1 = self.lp1.lp(self.pink1.sample())*swell*0.55
        v2 = self.lp2.lp(self.pink2.sample())*wave2*0.28
        v3 = self.lp3.lp(self.pink3.sample())*ripple*0.12
        base = self.hp.hp(v1+v2+v3)
        if self.crash_t < 0 and swell > 0.85 and _rand() < 0.02:
            self.crash_t=0.0; self.crash_amp=_uniform(0.3,0.7); self.crash_dur=_uniform(1.5,3.5)
        crash = 0.0
        if self.crash_t >= 0:
            self.crash_t += INV_SR
            if self.crash_t < self.crash_dur:
                ce = _exp(-self.crash_t*2.0/self.crash_dur)
                crash = self.foam_lp.lp(self.foam.sample())*ce*self.crash_amp*0.4
            else:
                self.crash_t = -1.0
        mono = (base+crash)*self.intensity*0.75
        sp = 0.5+0.15*fast_sin(self.lfo1*0.3)
        return mono*sp, mono*(1.0-sp)

class WaterStream:
    __slots__ = ("pink","hpf","lpf","bubble_lp","intensity")
    def __init__(self, intensity=0.35):
        self.pink=PinkNoise(); self.hpf=OnePole(500.0)
        self.lpf=OnePole(4500.0); self.bubble_lp=OnePole(2800.0)
        self.intensity=intensity
    def sample_stereo(self, t=0.0):
        v = self.hpf.hp(self.lpf.lp(self.pink.sample()))*0.18
        bub    = self.bubble_lp.lp(_uniform(-1,1))*_uniform(0.1,0.35) if _rand()<self.intensity*0.008 else 0.0
        splash = _uniform(0.15,0.4) if _rand()<self.intensity*0.0015 else 0.0
        mono = (v + bub*0.3 + splash*0.15)*self.intensity
        pan = _uniform(-0.5,0.5); pr = (pan+1)*_PI*0.25
        return mono*_cos(pr), mono*_sin(pr)

class Fire:
    __slots__ = ("roar_lp","crackle_lp","crackle_hp","pop_hp","ember_bp","lfo","lfo_inc","intensity")
    def __init__(self, intensity=0.35):
        self.roar_lp=OnePole(250.0); self.crackle_lp=OnePole(2500.0)
        self.crackle_hp=OnePole(400.0); self.pop_hp=OnePole(1500.0)
        self.ember_bp=SVF(4500.0,0.3)
        self.lfo=_uniform(0,TAU); self.lfo_inc=TAU*0.07*INV_SR
        self.intensity=intensity
    def sample_stereo(self, t=0.0):
        self.lfo+=self.lfo_inc
        breath = 0.6+0.4*(0.5+0.5*fast_sin(self.lfo))
        roar   = self.roar_lp.lp(_uniform(-1,1))*0.12*breath
        crack  = self.crackle_hp.hp(self.crackle_lp.lp(_uniform(-1,1)))*_uniform(0.2,0.5) if _rand()<self.intensity*0.015 else 0.0
        pop    = self.pop_hp.hp(_uniform(-1,1))*_uniform(0.3,0.7) if _rand()<self.intensity*0.004 else 0.0
        ember  = self.ember_bp.bp_process(_uniform(-1,1))*_uniform(0.1,0.3) if _rand()<self.intensity*0.001 else 0.0
        mono = (roar + crack*0.25 + pop*0.15 + ember*0.08)*self.intensity
        pan = _uniform(-0.3,0.3); pr = (pan+1)*_PI*0.25
        return mono*_cos(pr), mono*_sin(pr)

class Thunder:
    __slots__ = ("active","stage","stage_t","amp","distance","lp1","lp2","lp3","hp","intensity","cooldown")
    def __init__(self, intensity=0.5):
        self.active=False; self.stage=0; self.stage_t=0.0
        self.amp=0.0; self.distance=0.5
        self.lp1=OnePole(80.0); self.lp2=OnePole(250.0); self.lp3=OnePole(500.0)
        self.hp=OnePole(20.0); self.intensity=intensity; self.cooldown=0.0
    def sample_stereo(self, t=0.0):
        if self.cooldown > 0: self.cooldown -= INV_SR
        if not self.active:
            if self.cooldown <= 0 and _rand() < self.intensity*0.00003:
                self.active=True; self.stage=0; self.stage_t=0.0
                self.amp=_uniform(0.5,1.0); self.distance=_uniform(0.2,1.0)
                self.cooldown=_uniform(5.0,15.0)
                self.lp1.set(60+80*(1-self.distance))
                self.lp2.set(150+200*(1-self.distance))
            return 0.0, 0.0
        self.stage_t += INV_SR; v = 0.0
        if self.stage == 0:
            if self.stage_t < 0.05*(1+self.distance):
                v = self.lp3.lp(_uniform(-1,1))*_exp(-self.stage_t*30)*self.amp*0.6
            else:
                self.stage=1; self.stage_t=0.0
        elif self.stage == 1:
            dur = (1.5 + 1.5*self.distance)
            if self.stage_t < dur:
                env = _exp(-self.stage_t*1.5/dur)
                v = (self.lp1.lp(_uniform(-1,1))*0.5 + self.lp2.lp(_uniform(-1,1))*0.35*_exp(-self.stage_t*3))*env*self.amp
            else:
                self.stage=2; self.stage_t=0.0
        elif self.stage == 2:
            tail = 2.0+4.0*self.distance
            if self.stage_t < tail:
                v = self.lp1.lp(_uniform(-1,1))*_exp(-self.stage_t*2.0/tail)*self.amp*0.25
            else:
                self.active=False; return 0.0, 0.0
        v = self.hp.hp(v)*self.intensity*0.65
        w = 0.4*(1-self.distance)+0.05
        return v*(0.5+w), v*(0.5-w)

# ─── TONAL GENERATORS ────────────────────────────────────────────────────────

class SingingBowl:
    __slots__ = ("partials","decay","t","next_strike","amp","intensity")
    def __init__(self, intensity=0.45):
        self.partials=[]; self.decay=0.0; self.t=0.0
        self.next_strike=0.0; self.amp=0.0; self.intensity=intensity
        self._new_strike()
    def _new_strike(self):
        base = random.choice([180.0,220.0,260.0,310.0,370.0,440.0])
        ratios=[1.0,2.71,4.77,7.03,9.43]; beats=[0.0,0.7,1.2,0.5,0.9]
        self.partials=[]
        for r,b in zip(ratios,beats):
            f=base*r
            if f<NYQUIST*0.9:
                self.partials.append([_uniform(0,TAU),TAU*f*INV_SR,TAU*b*INV_SR,1.0/(r*r*0.3+1.0)])
        self.decay=_uniform(5.0,12.0); self.t=0.0; self.amp=_uniform(0.5,1.0)
        self.next_strike=_uniform(6.0,18.0)
    def sample(self, t_sec=0.0):
        self.t += INV_SR
        if self.t > self.next_strike: self._new_strike()
        env = _exp(-self.t*2.0/max(self.decay,0.01))
        if env < 0.001: return 0.0
        v=0.0
        for p in self.partials:
            p[0]+=p[1]
            v += fast_sin(p[0])*p[3]*(0.85+0.15*fast_sin(p[0]*0.0001+p[2]*self.t*SR))
        return v*env*self.amp*self.intensity*0.16

class WindChimes:
    __slots__ = ("density","active_chimes","intensity")
    def __init__(self, density=0.3, intensity=0.30):
        self.density=density; self.active_chimes=[]; self.intensity=intensity
    def sample_stereo(self, t=0.0):
        maxc = _Q["max_chimes"]
        if len(self.active_chimes) < maxc and _rand() < self.density*0.0003:
            freq = random.choice([1200,1580,1890,2100,2640,3150,3520])
            self.active_chimes.append([0.0,float(freq),_uniform(3,8),0.0,_uniform(0.3,1.0),_uniform(-0.5,0.5)])
        l=0.0; r=0.0; alive=[]
        for ch in self.active_chimes:
            ch[0]+=TAU*ch[1]*INV_SR; ch[3]+=INV_SR
            env=_exp(-ch[3]/ch[2])
            if env<0.001: continue
            alive.append(ch)
            tone=fast_sin(ch[0])*0.6+fast_sin(ch[0]*2.76)*0.25+fast_sin(ch[0]*5.4)*0.12
            v=tone*env*ch[4]*self.intensity*0.12
            pr=(ch[5]+1)*_PI*0.25
            l+=v*_cos(pr); r+=v*_sin(pr)
        self.active_chimes=alive
        return l, r

class Binaural:
    __slots__ = ("carrier","beat","phase","t")
    def __init__(self, carrier=200.0, beat=4.0):
        self.carrier=carrier; self.beat=beat; self.phase=0.0; self.t=0.0
    def sample(self):
        self.phase += TAU*self.carrier*INV_SR; self.t += INV_SR
        return fast_sin(self.phase), fast_sin(self.phase+TAU*self.beat*self.t)

class BytebeatAmbient:
    __slots__ = ("t","sr_scale","lp1","lp2","hp","feedback","mode","intensity","drift_phase","drift_inc")
    def __init__(self, intensity=0.35, mode=0):
        self.t=0; self.sr_scale=max(1,int(SR/max(_Q["bytebeat_sr"],1000)))
        self.lp1=OnePole(1800.0); self.lp2=OnePole(900.0); self.hp=OnePole(40.0)
        self.feedback=0.0; self.mode=mode%5; self.intensity=intensity
        self.drift_phase=_uniform(0,TAU); self.drift_inc=TAU*0.013*INV_SR
    def _formula(self, x):
        m=self.mode
        if   m==0: y=((x>>7)|(x>>6)|(x*3))&255; z=((x*((y&31)+1))>>8)&255; return (y^z)&255
        elif m==1: y=(x*((x>>9)|(x>>13)))&255;   z=((x>>5)|(x>>8))&255;     return (y^z)&255
        elif m==2: y=((x*5&(x>>7))|(x*3&(x>>10)))&255; z=((x>>4)^(x>>6)^(x>>9))&255; return (y+z)&255
        elif m==3: y=((x>>8)|(x>>5)|(x*9))&255;  z=((x*((x>>11)&15 or 1))>>7)&255; return (y^z)&255
        else:      y=((x|(x>>11))*(x&(x>>3)))&255; z=((x>>6)*(x>>2)&(x>>8))&255; return (y^z)&255
    def sample(self, t_sec=0.0):
        self.drift_phase+=self.drift_inc
        drift=0.98+0.04*(0.5+0.5*fast_sin(self.drift_phase))
        x=int(self.t/self.sr_scale*drift); raw=self._formula(x)
        fb=int((self.feedback*127)+128)&255; raw=(raw^(fb>>1))&255
        v=(raw-128.0)/128.0
        v=self.lp1.lp(v); v=self.lp2.lp(v); v=v-self.hp.lp(v)*0.15
        self.feedback=0.985*self.feedback+0.015*v; self.t+=1
        return v*self.intensity

# ─── GEOLOGICAL & COSMIC ENTITY SIMULATION ───────────────────────────────────
# IMPORTANT: No biological data. No living organisms.
# Entity profiles represent inanimate geological formations and cosmic objects.
# Parameters describe physical oscillation and spectral properties.
# coherence   — structural stability (0–1)
# collapse    — rate of sudden energy release events (0–1)
# entangle    — cross-channel phase correlation (0–1)
# pulse       — dominant oscillation frequency (Hz)
# centroid    — spectral center of mass (Hz)

ENTITY_PROFILES = {
    # ── Geological (inanimate formations) ────────────────────────────────
    "glacier":       {"coherence":0.99,"collapse":0.0005,"entangle":0.95,"pulse":0.005,"centroid":30},
    "mountain":      {"coherence":0.99,"collapse":0.001, "entangle":0.90,"pulse":0.01, "centroid":60},
    "desert_dune":   {"coherence":0.85,"collapse":0.02,  "entangle":0.40,"pulse":0.05, "centroid":150},
    "river_stone":   {"coherence":0.93,"collapse":0.008, "entangle":0.70,"pulse":0.08, "centroid":200},
    "canyon":        {"coherence":0.97,"collapse":0.003, "entangle":0.80,"pulse":0.02, "centroid":80},
    "volcanic_rock": {"coherence":0.90,"collapse":0.015, "entangle":0.55,"pulse":0.03, "centroid":100},
    "salt_flat":     {"coherence":0.98,"collapse":0.001, "entangle":0.85,"pulse":0.007,"centroid":45},
    "deep_ocean":    {"coherence":0.96,"collapse":0.005, "entangle":0.88,"pulse":0.015,"centroid":35},
    # ── Cosmic / inanimate objects ────────────────────────────────────────
    "nebula":        {"coherence":0.60,"collapse":0.12,  "entangle":0.85,"pulse":2.0,  "centroid":3500},
    "pulsar":        {"coherence":0.55,"collapse":0.20,  "entangle":0.25,"pulse":150.0,"centroid":8000},
    "stellar_wind":  {"coherence":0.70,"collapse":0.08,  "entangle":0.50,"pulse":0.8,  "centroid":2200},
    "accretion":     {"coherence":0.65,"collapse":0.15,  "entangle":0.60,"pulse":3.5,  "centroid":4000},
    "solar_flare":   {"coherence":0.50,"collapse":0.25,  "entangle":0.30,"pulse":8.0,  "centroid":6000},
    "dark_matter":   {"coherence":0.99,"collapse":0.0001,"entangle":0.99,"pulse":0.001,"centroid":10},
    "cosmic_void":   {"coherence":1.00,"collapse":0.0001,"entangle":1.00,"pulse":0.0005,"centroid":5},
}

class CosmicEntity:
    """
    Texture generator for inanimate geological and cosmic objects.
    Models physical oscillation, coherence fluctuation, and spectral shaping.
    No biological data. No living-organism references.
    Pure wave mathematics derived from physical measurement parameters.
    """
    __slots__ = ("profile","lp","hp","bp","pulse_phase","pulse_inc",
                 "coherence_lfo","coherence_inc","collapse_t",
                 "noise","intensity","entangle_buf","eb_idx")
    def __init__(self, profile_name="mountain", intensity=0.35):
        p = ENTITY_PROFILES.get(profile_name, ENTITY_PROFILES["mountain"])
        self.profile = p
        centroid = p["centroid"]
        self.lp  = OnePole(centroid*2)
        self.hp  = OnePole(max(centroid*0.1, 10))
        self.bp  = SVF(centroid, 0.3)
        self.pulse_phase   = 0.0
        self.pulse_inc     = TAU*p["pulse"]*INV_SR
        self.coherence_lfo = _uniform(0, TAU)
        self.coherence_inc = TAU*0.07*INV_SR
        self.collapse_t    = -1.0
        self.noise         = PinkNoise()
        self.intensity     = intensity
        self.entangle_buf  = [0.0]*256
        self.eb_idx        = 0
    def sample_stereo(self, t=0.0):
        p = self.profile
        self.coherence_lfo += self.coherence_inc
        coh = p["coherence"] * (0.8 + 0.2*fast_sin(self.coherence_lfo))
        collapse_prob = p["collapse"]*INV_SR*0.1
        if self.collapse_t < 0 and _rand() < collapse_prob:
            self.collapse_t = 0.0
        collapse_v = 0.0
        if self.collapse_t >= 0:
            self.collapse_t += INV_SR
            dur = 0.02 + p["collapse"]*0.5
            if self.collapse_t < dur:
                collapse_v = _uniform(-1,1)*_exp(-self.collapse_t/dur*3)
            else:
                self.collapse_t = -1.0
        self.pulse_phase += self.pulse_inc
        pulse = fast_sin(self.pulse_phase)*coh*0.4
        raw = self.noise.sample()
        base_l = self.bp.bp_process(self.lp.lp(raw))*0.5 + pulse*0.5
        base_l += collapse_v*0.3
        ent = p["entangle"]
        eb = self.entangle_buf; idx = self.eb_idx
        eb[idx%256] = base_l
        delayed = eb[(idx-int(44*ent))%256]
        base_r = lerp(self.hp.hp(self.noise.sample())*0.5+pulse*0.5, delayed, ent)
        base_r += collapse_v*0.25
        self.eb_idx += 1
        scale = self.intensity*(0.8+0.2*coh)
        return base_l*scale, base_r*scale

# ─── FREEFLOW MODE ────────────────────────────────────────────────────────────

class FreeflowMode:
    """
    Creative freeflow: evolving blend of synthesis families.
    Slowly morphs between random parameter states.
    Entity layer uses only inanimate ENTITY_PROFILES.
    freeflow param (0–1): depth of exploration.
    """
    __slots__ = ("freeflow","seed","rng","phase_time","phase_dur",
                 "current","target","pink","lp","hp","lfo_a","lfo_b","lfo_c",
                 "inc_a","inc_b","inc_c","pad","pad_t","pad_dur",
                 "entity","entity_profile","bass_phase","bass_inc","dc_l","dc_r")
    def __init__(self, freeflow=0.5, seed=0):
        self.freeflow = freeflow
        self.rng = random.Random(seed)
        self.pink = PinkNoise()
        self.lp = OnePole(800.0); self.hp = OnePole(60.0)
        self.lfo_a = _uniform(0,TAU); self.lfo_b = _uniform(0,TAU); self.lfo_c = _uniform(0,TAU)
        rng = self.rng
        self.inc_a = TAU*rng.uniform(0.05,0.25)*INV_SR
        self.inc_b = TAU*rng.uniform(0.02,0.12)*INV_SR
        self.inc_c = TAU*rng.uniform(0.01,0.06)*INV_SR
        self.phase_time = 0.0
        self.phase_dur  = rng.uniform(8.0, 20.0+freeflow*40)
        self.current = self._random_state()
        self.target  = self._random_state()
        self.pad = None; self.pad_t = 0.0; self.pad_dur = 0.0
        ep = random.choice(list(ENTITY_PROFILES.keys()))
        self.entity = CosmicEntity(ep, intensity=0.12)
        self.entity_profile = ep
        root = rng.choice([36,40,43,45,48])
        self.bass_phase = 0.0; self.bass_inc = TAU*mtof(root-12)*INV_SR
        self.dc_l = DCBlocker(); self.dc_r = DCBlocker()
    def _random_state(self):
        r = self.rng
        return {
            "noise_amt":  r.uniform(0.0, 0.4*self.freeflow),
            "tonal_amt":  r.uniform(0.3, 0.9),
            "bass_amt":   r.uniform(0.0, 0.35),
            "entity_amt": r.uniform(0.0, 0.25*self.freeflow),
            "brightness": r.uniform(200, 4000),
            "pad_notes":  [r.randint(48,72) for _ in range(r.randint(2,4))],
        }
    def sample_stereo(self, t=0.0):
        self.phase_time += INV_SR
        alpha = min(self.phase_time / max(self.phase_dur,1.0), 1.0)
        def interp(k):
            a = self.current[k]; b = self.target[k]
            if isinstance(a, float): return lerp(a, b, alpha)
            return a
        noise_amt  = interp("noise_amt")
        tonal_amt  = interp("tonal_amt")
        bass_amt   = interp("bass_amt")
        entity_amt = interp("entity_amt")
        brightness = interp("brightness")
        if alpha >= 1.0:
            self.current = self.target
            self.target  = self._random_state()
            self.phase_time = 0.0
            self.phase_dur  = self.rng.uniform(8.0, 20.0+self.freeflow*40)
            ep = random.choice(list(ENTITY_PROFILES.keys()))
            self.entity = CosmicEntity(ep, intensity=0.12)
        self.lfo_a += self.inc_a; self.lfo_b += self.inc_b; self.lfo_c += self.inc_c
        self.lp.set(brightness*(0.8+0.4*fast_sin(self.lfo_a)))
        noise_l = self.hp.hp(self.lp.lp(self.pink.sample())) * noise_amt
        self.pad_t += INV_SR
        if self.pad is None or self.pad_t > self.pad_dur:
            notes = self.target["pad_notes"]
            self.pad = Pad(notes, detune=0.003+self.freeflow*0.008)
            self.pad_dur = self.rng.uniform(4.0,16.0)
            self.pad_t = 0.0
        tonal = self.pad.sample(t) * tonal_amt * (0.5+0.5*fast_sin(self.lfo_b))
        self.bass_phase += self.bass_inc
        bass = fast_sin(self.bass_phase)*bass_amt*0.5*(0.3+0.7*fast_sin(self.lfo_c))
        el, er = self.entity.sample_stereo(t)
        l = noise_l*0.7 + tonal*0.5 + bass + el*entity_amt
        r = noise_l*1.3 + tonal*0.5 + bass + er*entity_amt
        return self.dc_l.process(l), self.dc_r.process(r)

# ─── MESSAGE MODE ────────────────────────────────────────────────────────────

def text_to_pattern(text):
    if not text: return []
    pattern = []
    for ch in text[:64]:
        code = ord(ch) % 128
        pitch_off = (code * 7) % 24
        dur_frac  = 0.25 + (code % 16) * 0.05
        sil_frac  = 0.1 if ch.isalnum() else 0.3
        pattern.append((pitch_off, dur_frac, sil_frac))
    return pattern

class MessageMode:
    __slots__ = ("pattern","pos","t_in_element","root_freq","carrier_phase","carrier_inc",
                 "signal_phase","pulse_amp","_beat")
    def __init__(self, text="", root=60, bpm=60):
        self.pattern  = text_to_pattern(text) if text else [(i*3%12,0.20,0.08) for i in range(16)]
        self.pos      = 0; self.t_in_element = 0.0
        beat = 60.0/bpm; self.root_freq = mtof(root)
        carrier_hz = self.root_freq * 0.5
        self.carrier_phase = 0.0; self.carrier_inc = TAU*carrier_hz*INV_SR
        self.signal_phase = 0.0; self.pulse_amp = 0.6; self._beat = beat
    def sample_stereo(self, t=0.0):
        if not self.pattern: return 0.0, 0.0
        el = self.pattern[self.pos % len(self.pattern)]
        pitch_off, dur_frac, sil_frac = el
        dur = dur_frac * self._beat; sil = sil_frac * self._beat
        total = dur + sil; self.t_in_element += INV_SR
        if self.t_in_element >= total:
            self.t_in_element = 0.0
            self.pos = (self.pos + 1) % len(self.pattern)
            el = self.pattern[self.pos % len(self.pattern)]
            pitch_off, dur_frac, sil_frac = el
        in_sil = self.t_in_element >= dur
        self.carrier_phase += self.carrier_inc
        carrier = fast_sin(self.carrier_phase) * self.pulse_amp * 0.2
        if in_sil: return carrier*0.3, carrier*0.3
        sig_freq = self.root_freq * (2.0 ** (pitch_off/12.0))
        self.signal_phase += TAU*sig_freq*INV_SR
        local_t = self.t_in_element
        env = min(local_t/0.02, 1.0) * min((dur-local_t)/0.02, 1.0)
        env = max(0.0, env)
        signal = fast_sin(self.signal_phase)*env*0.5
        transient = _exp(-local_t*200)*0.15 if local_t < 0.01 else 0.0
        out = carrier*0.2 + signal + transient
        return out, out

# ─── EFFECTS ─────────────────────────────────────────────────────────────────

class Delay:
    __slots__ = ("bl","br","il","ir","fb","mix")
    def __init__(self, time_l=0.375, time_r=0.25, feedback=0.35, mix=0.25):
        self.bl=[0.0]*(int(SR*time_l)+2); self.br=[0.0]*(int(SR*time_r)+2)
        self.il=0; self.ir=0; self.fb=feedback; self.mix=mix
    def process(self, l, r):
        bl=self.bl; br=self.br
        il=self.il%len(bl); ir=self.ir%len(br)
        dl=bl[il]; dr=br[ir]
        bl[il]=l+dl*self.fb; br[ir]=r+dr*self.fb
        self.il+=1; self.ir+=1
        return l+dl*self.mix, r+dr*self.mix

class Reverb:
    COMB_DELAYS_ALL = (0.02257,0.02391,0.02641,0.02743,0.02999,0.03119,0.03371,0.03571)
    AP_DELAYS       = (0.0050,0.0017,0.00051)
    __slots__ = ("combs","ci","cfb","aps","ai","lps","damp","mix")
    def __init__(self, size=0.9, damp=0.45, mix=0.30):
        nc = _Q["reverb_combs"]; cds = self.COMB_DELAYS_ALL[:nc]
        self.combs=[([0.0]*max(int(SR*d*size),2)) for d in cds]
        self.ci=[0]*nc; self.cfb=0.84
        self.aps=[([0.0]*max(int(SR*d),2)) for d in self.AP_DELAYS]
        self.ai=[0]*3; self.lps=[0.0]*nc; self.damp=damp; self.mix=mix
    def process(self, x):
        out=0.0
        for i,buf in enumerate(self.combs):
            idx=self.ci[i]%len(buf); val=buf[idx]
            self.lps[i]=val*(1.0-self.damp)+self.lps[i]*self.damp
            buf[idx]=x+self.lps[i]*self.cfb; self.ci[i]+=1; out+=val
        out/=len(self.combs)
        for i,buf in enumerate(self.aps):
            idx=self.ai[i]%len(buf); bv=buf[idx]
            buf[idx]=out+bv*0.5; self.ai[i]+=1; out=bv-out*0.5
        return x*(1.0-self.mix)+out*self.mix

class Chorus:
    __slots__ = ("buf","idx","ph1","ph2","inc1","inc2","depth","mix")
    def __init__(self, rate=1.1, depth=0.003, mix=0.28):
        self.buf=[0.0]*(int(SR*0.04)+2); self.idx=0
        self.ph1=0.0; self.ph2=_PI/3.0
        self.inc1=TAU*rate*INV_SR; self.inc2=TAU*rate*1.07*INV_SR
        self.depth=depth*SR; self.mix=mix
    def process(self, x):
        buf=self.buf; L=len(buf); idx=self.idx; buf[idx%L]=x; self.idx+=1
        self.ph1+=self.inc1; self.ph2+=self.inc2; m=self.mix
        def _tap(ph):
            off=self.depth*(1.0+fast_sin(ph))*0.5
            ri=idx-int(off); f=off-int(off)
            a=buf[ri%L]; b=buf[(ri-1)%L]; return a+(b-a)*f
        return x*(1-m)+_tap(self.ph1)*m, x*(1-m)+_tap(self.ph2)*m

class VinylTexture:
    __slots__ = ("pink","rumble_lp","crackle")
    def __init__(self):
        self.pink=PinkNoise(); self.rumble_lp=OnePole(70.0); self.crackle=0.0
    def sample(self):
        hiss   = self.pink.sample()*0.010
        rumble = self.rumble_lp.lp(_uniform(-1,1))*0.005
        crack  = 0.0
        if self.crackle > 0.001:
            self.crackle *= 0.88; crack = _uniform(-1,1)*self.crackle
        elif _rand() < 0.00025:
            self.crackle = 0.28
        return hiss+rumble+crack

class TapeProcessor:
    __slots__ = ("buf","idx","wow","flutter","wow_inc","flutter_inc","lp","dw","df")
    def __init__(self):
        self.buf=[0.0]*(int(SR*0.05)+2); self.idx=0
        self.wow=0.0; self.flutter=0.0
        self.wow_inc=TAU*0.35*INV_SR; self.flutter_inc=TAU*6.0*INV_SR
        self.lp=OnePole(13500.0); self.dw=0.0011*SR; self.df=0.00035*SR
    def process(self, x):
        buf=self.buf; L=len(buf); buf[self.idx%L]=x; self.idx+=1
        self.wow+=self.wow_inc; self.flutter+=self.flutter_inc
        offset=(self.dw*(1+fast_sin(self.wow))*0.5+self.df*(1+fast_sin(self.flutter))*0.5+2.0)
        ri=self.idx-int(offset); frac=offset-int(offset)
        a=buf[ri%L]; b=buf[(ri-1)%L]
        return soft_clip(self.lp.lp(a+(b-a)*frac), 1.06)

# ─── MUSIC THEORY ────────────────────────────────────────────────────────────

SCALES = {
    "major":           [0,2,4,5,7,9,11],
    "minor":           [0,2,3,5,7,8,10],
    "dorian":          [0,2,3,5,7,9,10],
    "phrygian":        [0,1,3,5,7,8,10],
    "lydian":          [0,2,4,6,7,9,11],
    "mixolydian":      [0,2,4,5,7,9,10],
    "pentatonic":      [0,2,4,7,9],
    "minor_pentatonic":[0,3,5,7,10],
    "blues":           [0,3,5,6,7,10],
    "chromatic":       list(range(12)),
    "whole_tone":      [0,2,4,6,8,10],
    "harmonic_minor":  [0,2,3,5,7,8,11],
}

CHORDS = {
    "maj":[0,4,7],"min":[0,3,7],"maj7":[0,4,7,11],"min7":[0,3,7,10],
    "sus2":[0,2,7],"sus4":[0,5,7],"dim":[0,3,6],"aug":[0,4,8],"add9":[0,4,7,14],
}

PROGRESSIONS = {
    "ambient":     [(0,"sus2"),(4,"sus2"),(3,"maj7"),(0,"sus2")],
    "dark_ambient":[(0,"min"),(1,"min"),(4,"min"),(3,"maj")],
    "synthwave":   [(0,"min"),(3,"maj"),(4,"min"),(6,"maj")],
    "lo_fi":       [(0,"maj7"),(1,"min7"),(2,"min7"),(4,"maj7")],
    "sacred":      [(0,"sus2"),(5,"sus4"),(3,"maj7"),(0,"sus2")],
    "experimental":[(0,"sus2"),(1,"min"),(2,"min"),(4,"maj"),(0,"sus2")],
    "cosmic":      [(0,"sus2"),(4,"add9"),(3,"sus4"),(2,"min7"),(0,"sus2")],
    "drone":       [(0,"sus2")],
    "meditation":  [(0,"sus2"),(4,"sus2")],
    "bellscape":   [(0,"sus2"),(4,"sus2"),(0,"sus2")],
}

def build_scale(root, scale_name, octaves=3):
    pat = SCALES.get(scale_name, SCALES["minor"])
    return [root+o*12+i for o in range(octaves) for i in pat if 0 <= root+o*12+i <= 127]

def build_chord(root, chord_name):
    return [root+i for i in CHORDS.get(chord_name, CHORDS["min"])]

def euclidean_rhythm(steps, pulses):
    if pulses <= 0:     return [False]*steps
    if pulses >= steps: return [True]*steps
    pattern=[]; bucket=0
    for _ in range(steps):
        bucket += pulses
        if bucket >= steps: pattern.append(True); bucket -= steps
        else:               pattern.append(False)
    return pattern

# ─── MOOD PRESETS ────────────────────────────────────────────────────────────

MOOD_PRESETS = {
    "peaceful":    (0.20,0.25,0.80,0.55,0.70,1.0, 0.20,0.70,0.20,0.40,0.50,0.20,0.60,0.30),
    "joyful":      (0.55,0.70,0.75,0.85,0.45,1.2, 0.65,0.50,0.50,0.25,0.75,0.45,0.30,0.65),
    "ethereal":    (0.18,0.30,0.50,0.60,0.90,1.5, 0.25,0.80,0.15,0.35,0.60,0.35,0.70,0.35),
    "melancholic": (0.25,0.35,0.65,0.35,0.65,0.9, 0.30,0.60,0.25,0.20,0.55,0.30,0.55,0.40),
    "mysterious":  (0.22,0.40,0.40,0.35,0.80,1.4, 0.40,0.75,0.35,0.30,0.65,0.55,0.50,0.45),
    "intense":     (0.75,0.90,0.45,0.75,0.50,1.1, 0.85,0.35,0.80,0.15,0.85,0.65,0.10,0.85),
    "somber":      (0.15,0.20,0.55,0.20,0.75,0.85,0.15,0.65,0.10,0.25,0.40,0.15,0.70,0.30),
}

ENV_PRESETS = {
    "light_rain":  ({"rain":0.45,"wind":0.15},      0.15,1.1,0.05,"Gentle rainfall"),
    "storm":       ({"rain":0.85,"wind":0.60,"thunder":0.70},0.35,1.3,0.30,"Full thunderstorm"),
    "calm_sea":    ({"ocean":0.65,"wind":0.10},      0.20,1.2,0.10,"Calm ocean"),
    "windy":       ({"wind":0.75},                   0.05,1.4,0.25,"Open windy plain"),
    "night":       ({"wind":0.12},                   0.10,1.0,0.10,"Night stillness"),
}

# ─── GENRES ──────────────────────────────────────────────────────────────────

GENRES = {
    "ambient":{"bpm":(60,76),"scale":"pentatonic","key":48,"prog":"ambient","density":0.20,"drums":False,
        "bass_wave":"sine","bass_oct":-2,"bass_cut":300,"bass_res":0.08,
        "lead":"fm","lead_oct":1,"lead_detune":0.06,"lead_vol":0.26,"pad":True,"pad_vol":0.62,
        "reverb_size":1.20,"reverb_damp":0.38,"reverb_mix":0.54,
        "delay_time":0.50,"delay_fb":0.40,"delay_mix":0.40,"chorus_rate":0.65,"chorus_depth":0.004,"duration":(200,380)},
    "dark_ambient":{"bpm":(52,66),"scale":"phrygian","key":45,"prog":"dark_ambient","density":0.14,"drums":False,
        "bass_wave":"sine","bass_oct":-2,"bass_cut":220,"bass_res":0.18,
        "lead":"fm","lead_oct":0,"lead_detune":0.04,"lead_vol":0.22,"pad":True,"pad_vol":0.72,
        "reverb_size":1.42,"reverb_damp":0.62,"reverb_mix":0.64,
        "delay_time":0.65,"delay_fb":0.42,"delay_mix":0.40,"chorus_rate":0.38,"chorus_depth":0.005,"duration":(260,520)},
    "meditation":{"bpm":(50,62),"scale":"pentatonic","key":48,"prog":"meditation","density":0.10,"drums":False,
        "bass_wave":"sine","bass_oct":-2,"bass_cut":180,"bass_res":0.03,
        "lead":"fm","lead_oct":1,"lead_detune":0.015,"lead_vol":0.18,"pad":True,"pad_vol":0.70,
        "reverb_size":1.55,"reverb_damp":0.58,"reverb_mix":0.66,
        "delay_time":0.75,"delay_fb":0.42,"delay_mix":0.42,"chorus_rate":0.42,"chorus_depth":0.003,"duration":(300,720)},
    "drone":{"bpm":(40,52),"scale":"minor","key":36,"prog":"drone","density":0.05,"drums":False,
        "bass_wave":"sine","bass_oct":-2,"bass_cut":150,"bass_res":0.02,
        "lead":"fm","lead_oct":0,"lead_detune":0.12,"lead_vol":0.14,"pad":True,"pad_vol":0.82,
        "reverb_size":1.60,"reverb_damp":0.70,"reverb_mix":0.70,
        "delay_time":1.0,"delay_fb":0.46,"delay_mix":0.45,"chorus_rate":0.25,"chorus_depth":0.006,"duration":(300,600)},
    "bellscape":{"bpm":(68,84),"scale":"pentatonic","key":60,"prog":"bellscape","density":0.26,"drums":False,
        "bass_wave":"sine","bass_oct":-1,"bass_cut":420,"bass_res":0.06,
        "lead":"karplus","lead_oct":1,"lead_detune":0.0,"lead_vol":0.44,"pad":True,"pad_vol":0.28,
        "reverb_size":1.10,"reverb_damp":0.28,"reverb_mix":0.52,
        "delay_time":0.375,"delay_fb":0.30,"delay_mix":0.34,"chorus_rate":0.82,"chorus_depth":0.002,"duration":(150,300)},
    "sacred":{"bpm":(45,58),"scale":"pentatonic","key":48,"prog":"sacred","density":0.16,"drums":False,
        "bass_wave":"sine","bass_oct":-2,"bass_cut":240,"bass_res":0.06,
        "lead":"karplus","lead_oct":1,"lead_detune":0.0,"lead_vol":0.40,"pad":True,"pad_vol":0.60,
        "reverb_size":1.35,"reverb_damp":0.45,"reverb_mix":0.58,
        "delay_time":0.60,"delay_fb":0.36,"delay_mix":0.34,"chorus_rate":0.55,"chorus_depth":0.003,"duration":(240,480)},
    "cosmic":{"bpm":(42,58),"scale":"whole_tone","key":40,"prog":"cosmic","density":0.12,"drums":False,
        "bass_wave":"sine","bass_oct":-2,"bass_cut":200,"bass_res":0.05,
        "lead":"fm","lead_oct":1,"lead_detune":0.08,"lead_vol":0.20,"pad":True,"pad_vol":0.75,
        "reverb_size":1.60,"reverb_damp":0.50,"reverb_mix":0.68,
        "delay_time":0.80,"delay_fb":0.45,"delay_mix":0.44,"chorus_rate":0.30,"chorus_depth":0.005,"duration":(300,600)},
    "synthwave":{"bpm":(94,112),"scale":"minor","key":43,"prog":"synthwave","density":0.54,"drums":True,
        "bass_wave":"saw","bass_oct":-1,"bass_cut":1300,"bass_res":0.30,
        "lead":"supersaw","lead_oct":1,"lead_detune":0.30,"lead_vol":0.36,"pad":True,"pad_vol":0.42,
        "reverb_size":0.88,"reverb_damp":0.32,"reverb_mix":0.34,
        "delay_time":0.375,"delay_fb":0.34,"delay_mix":0.28,"chorus_rate":1.0,"chorus_depth":0.003,"duration":(180,320)},
    "lo_fi":{"bpm":(74,90),"scale":"dorian","key":48,"prog":"lo_fi","density":0.36,"drums":True,
        "bass_wave":"tri","bass_oct":-1,"bass_cut":580,"bass_res":0.14,
        "lead":"fm","lead_oct":1,"lead_detune":0.018,"lead_vol":0.24,"pad":True,"pad_vol":0.30,
        "reverb_size":0.72,"reverb_damp":0.56,"reverb_mix":0.30,
        "delay_time":0.333,"delay_fb":0.28,"delay_mix":0.20,"chorus_rate":1.05,"chorus_depth":0.003,"duration":(120,260)},
    "experimental":{"bpm":(55,110),"scale":"blues","key":42,"prog":"experimental","density":0.42,"drums":False,
        "bass_wave":"pulse","bass_oct":-1,"bass_cut":1400,"bass_res":0.28,
        "lead":"karplus","lead_oct":1,"lead_detune":0.08,"lead_vol":0.34,"pad":True,"pad_vol":0.30,
        "reverb_size":0.95,"reverb_damp":0.28,"reverb_mix":0.42,
        "delay_time":0.333,"delay_fb":0.40,"delay_mix":0.34,"chorus_rate":1.4,"chorus_depth":0.004,"duration":(120,300)},
}

PURE_MODES = {
    "pure_nature","pure_wind","pure_rain","pure_ocean","pure_water","pure_fire",
    "pure_storm","pure_white","pure_pink","pure_brown",
    "pure_theta","pure_alpha","pure_delta","pure_bowls","pure_chimes",
    "pure_bytebeat",
}

SPECIAL_MODES = {"message","freeflow","entity"}
ALL_MODES = set(GENRES.keys()) | PURE_MODES | SPECIAL_MODES

# ─── PROMPT PARSER ───────────────────────────────────────────────────────────

MODE_ALIASES = {
    "ambient":"ambient","dark ambient":"dark_ambient","dark":"dark_ambient",
    "meditation":"meditation","sleep":"meditation","calm":"meditation",
    "drone":"drone","bellscape":"bellscape","bells":"bellscape",
    "sacred":"sacred","ritual":"sacred","cosmic":"cosmic","space":"cosmic",
    "experimental":"experimental","synthwave":"synthwave","retro":"synthwave",
    "lofi":"lo_fi","lo-fi":"lo_fi","lo fi":"lo_fi",
    "nature":"pure_nature","wind":"pure_wind","rain":"pure_rain",
    "ocean":"pure_ocean","waves":"pure_ocean","water":"pure_water",
    "fire":"pure_fire","storm":"pure_storm","thunder":"pure_storm",
    "white noise":"pure_white","pink noise":"pure_pink","brown noise":"pure_brown",
    "theta":"pure_theta","alpha":"pure_alpha","delta":"pure_delta",
    "bowls":"pure_bowls","chimes":"pure_chimes","bytebeat":"pure_bytebeat",
    "message":"message","freeflow":"freeflow","entity":"entity",
    "peaceful":"ambient","ethereal":"cosmic","somber":"drone",
}

FLAG_ALIASES = {
    "+vinyl":"vinyl","vinyl":"vinyl","+tape":"tape","tape":"tape",
    "+nature":"nature","+drums":"drums","drums":"drums",
    "+nodrums":"nodrums","+binaural":"binaural","binaural":"binaural",
    "+bytebeat":"bytebeat","+bright":"bright","bright":"bright",
    "+warm":"warm","warm":"warm","+cold":"cold","cold":"cold",
    "+wide":"wide","wide":"wide","+narrow":"narrow","narrow":"narrow",
    "+dense":"dense","dense":"dense","+sparse":"sparse","sparse":"sparse",
    "+bowls":"bowls","+chimes":"chimes","+storm":"storm","+night":"night",
    "+light rain":"light_rain","light rain":"light_rain",
}

def normalize_prompt(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#\s_\-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def fuzzy_lookup(token, table, cutoff=0.72):
    hit = difflib.get_close_matches(token, list(table.keys()), n=1, cutoff=cutoff)
    return table[hit[0]] if hit else None

def parse_prompt(text):
    norm = normalize_prompt(text); tokens = norm.split()
    mode=None; flags=set(); bpm=None
    duration=parse_duration_text(norm); root=None; scale=None
    mood=None; entity_profile=None
    for alias in sorted(MODE_ALIASES.keys(), key=len, reverse=True):
        if alias in norm: mode=MODE_ALIASES[alias]; break
    for ep in ENTITY_PROFILES:
        if ep.replace("_"," ") in norm or ep in norm:
            entity_profile=ep
            if mode is None: mode="entity"
            break
    for mk in MOOD_PRESETS:
        if mk in norm: mood=mk; break
    if mode is None:
        for tok in tokens:
            v=fuzzy_lookup(tok, MODE_ALIASES)
            if v: mode=v; break
    for alias,flag in FLAG_ALIASES.items():
        if alias in norm: flags.add(flag)
    bm = re.search(r'\b(\d{2,3})\s*bpm\b', norm)
    if bm: bpm = int(clamp(float(bm.group(1)),20,300))
    nm = re.search(r"\b([a-g](?:#|b)?[0-8])\b", norm, re.I)
    if nm: root=note_name_to_midi(nm.group(1))
    for s in ["major","minor","dorian","phrygian","lydian","mixolydian",
              "pentatonic","minor_pentatonic","blues","chromatic","whole_tone","harmonic_minor"]:
        if s.replace("_"," ") in norm or s in norm: scale=s; break
    quality=None
    for q in ("mobile","balanced","studio"):
        if q in norm: quality=q; break
    ff_match = re.search(r'freeflow\s+(\d+(?:\.\d+)?)', norm)
    freeflow = clamp(float(ff_match.group(1)), 0.0, 1.0) if ff_match else None
    return {
        "mode":mode,"flags":flags,"bpm":bpm,"duration":duration,
        "root":root,"scale":scale,"mood":mood,
        "entity_profile":entity_profile,"quality":quality,"freeflow":freeflow,
    }

# ─── GENRE APPLICATION ────────────────────────────────────────────────────────

def apply_flags_to_genre(cfg, flags):
    cfg=dict(cfg)
    if "nodrums"   in flags: cfg["drums"]=False
    if "drums"     in flags: cfg["drums"]=True
    if "warm"      in flags: cfg["bass_cut"]=int(cfg["bass_cut"]*0.7); cfg["reverb_damp"]=max(cfg["reverb_damp"],0.55)
    if "cold"      in flags: cfg["bass_cut"]=int(cfg["bass_cut"]*1.3); cfg["reverb_damp"]=min(cfg["reverb_damp"],0.30)
    if "bright"    in flags: cfg["lead_vol"]=min(0.8,cfg["lead_vol"]+0.05)
    if "sparse"    in flags: cfg["density"]*=0.55
    if "dense"     in flags: cfg["density"]=min(1,cfg["density"]*1.4)
    return cfg

def apply_mood(genre_cfg, mood_name):
    if mood_name not in MOOD_PRESETS: return genre_cfg
    cfg = dict(genre_cfg)
    (density,energy,warmth,brightness,wetness,width,motion,organic,pulse,nature,inst,rand_,sparsity,intensity) = MOOD_PRESETS[mood_name]
    cfg["density"]    = lerp(cfg.get("density",0.3), density, 0.6)
    cfg["pad_vol"]    = lerp(cfg.get("pad_vol",0.5), intensity, 0.4)
    cfg["reverb_mix"] = lerp(cfg.get("reverb_mix",0.4), wetness*0.8, 0.5)
    cfg["reverb_damp"]= lerp(cfg.get("reverb_damp",0.5), 1.0-warmth, 0.5)
    return cfg

def energy_curve(t, total_dur):
    p = t / max(total_dur, 1.0)
    if p<0.08: return (p/0.08)*0.30
    if p<0.25: return 0.30+((p-0.08)/0.17)*0.70
    if p<0.70: return 1.0
    if p<0.80: return 1.0-((p-0.70)/0.10)*0.40
    if p<0.90: return 0.60+((p-0.80)/0.10)*0.40
    return max(0.0, 1.0-(p-0.90)/0.10)

# ─── EVENT SEQUENCER ─────────────────────────────────────────────────────────

class Event:
    __slots__ = ("time","duration","engine","vol","pan","env","is_sub","is_drum")
    def __init__(self, time, duration, engine, vol=0.5, pan=0.0,
                 env=None, is_sub=False, is_drum=False):
        self.time=time; self.duration=duration; self.engine=engine
        self.vol=vol; self.pan=pan; self.env=env or ADSR(0.01,0.1,0.7,0.3)
        self.is_sub=is_sub; self.is_drum=is_drum

def generate_music_events(mode, rng, bpm=None, root=None,
                          scale_name=None, duration=None, flags=None, mood=None):
    flags=flags or set()
    genre=apply_flags_to_genre(GENRES.get(mode,GENRES["ambient"]),flags)
    if mood: genre=apply_mood(genre,mood)
    bpm=bpm or rng.randint(*genre["bpm"]); beat=60.0/bpm; bar=beat*4
    root=root if root is not None else genre["key"]
    scale_name=scale_name or genre["scale"]
    duration=duration or rng.randint(*genre["duration"])
    total_bars=max(1,int(duration/bar))
    scale=build_scale(root,scale_name,3)
    bass_scale=build_scale(root+genre["bass_oct"]*12,scale_name,2)
    prog=PROGRESSIONS.get(genre["prog"],PROGRESSIONS["ambient"])
    events=[]; density=genre["density"]; max_v=_Q["max_voices"]

    if genre["pad"]:
        step_bars=rng.choice([2,4,4,8])
        for bar_n in range(0,total_bars,step_bars):
            en=energy_curve(bar_n*bar,duration)
            if en<0.12: continue
            rd,ct=prog[bar_n%len(prog)]
            notes=build_chord(scale[rd%len(scale)]+12,ct)
            t=bar_n*bar; dur=min(bar*rng.choice([2,4,4,8]),max(0.5,duration-t))
            events.append(Event(t,dur,Pad(notes,detune=rng.uniform(0.003,0.008)),
                vol=genre["pad_vol"]*(0.35+0.65*en), pan=rng.uniform(-0.25,0.25),
                env=ADSR(rng.uniform(0.5,2),rng.uniform(0.4,1),rng.uniform(0.65,0.92),rng.uniform(1.2,3.2))))

    for bar_n in range(total_bars):
        en=energy_curve(bar_n*bar,duration)
        rd,_=prog[bar_n%len(prog)]; br=bass_scale[rd%len(bass_scale)]
        bpat=euclidean_rhythm(16,rng.choice([4,6,8]))
        for step in range(16):
            if bpat[step] and rng.random()<density*(0.4+0.6*en):
                t=humanize(bar_n*bar+step*beat*0.25,0.004)
                nd=beat*rng.choice([0.5,1,1,2]); freq=mtof(br+rng.choice([0,0,0,12]))
                events.append(Event(t,nd,SubSynth(freq,wave=genre["bass_wave"],cutoff=genre["bass_cut"],
                    res=genre["bass_res"],env_depth=genre["bass_cut"]*2.2),vol=0.56,pan=0.0,
                    env=ADSR(0.006,0.12,0.60,0.12),is_sub=True))

    lead_count=0
    for bar_n in range(total_bars):
        if lead_count >= max_v*4: break
        en=energy_curve(bar_n*bar,duration)
        if rng.random()>density*(0.30+0.70*en): continue
        rd,ct=prog[bar_n%len(prog)]; cr=scale[rd%len(scale)]+genre["lead_oct"]*12
        num_notes=rng.randint(2,7)
        for n in range(num_notes):
            t=humanize(bar_n*bar+n*bar/max(1,num_notes),0.006)
            nd=bar/max(1,num_notes)*rng.uniform(0.5,0.9)
            if t>=duration: continue
            note=(rng.choice(build_chord(cr,ct)) if rng.random()<0.60
                  else rng.choice(scale)+genre["lead_oct"]*12)
            freq=mtof(note); lt=genre["lead"]; is_sub=False
            if   lt=="supersaw": synth=SuperSaw(freq,detune=genre["lead_detune"],mix=rng.uniform(0.60,0.90))
            elif lt=="fm":       synth=FMSynth(freq,ratio=rng.choice([1,2,3,4,0.5]),depth=rng.uniform(0.6,2.8),feedback=rng.uniform(0,0.25))
            elif lt=="karplus":  synth=KarplusStrong(freq,decay=rng.uniform(0.992,0.998),brightness=rng.uniform(0.3,0.8))
            elif lt=="organ":    synth=Organ(freq)
            elif lt=="flute":    synth=FluteSynth(freq)
            else:                synth=SubSynth(freq,wave="saw",cutoff=3000,res=0.20,env_depth=2200); is_sub=True
            events.append(Event(t,nd,synth,vol=genre["lead_vol"]*(0.50+0.50*en),pan=rng.uniform(-0.45,0.45),
                env=ADSR(rng.uniform(0.01,0.05),rng.uniform(0.08,0.25),rng.uniform(0.30,0.75),rng.uniform(0.08,0.35)),is_sub=is_sub))
            lead_count+=1

    if genre["drums"]:
        kick_pat=euclidean_rhythm(16,4); hat_pat=euclidean_rhythm(16,rng.choice([8,10,12,14]))
        for bar_n in range(total_bars):
            en=energy_curve(bar_n*bar,duration)
            for step in range(16):
                t=humanize(bar_n*bar+step*beat*0.25,0.003)
                if t>=duration: continue
                if kick_pat[step] and rng.random()<(0.65+0.35*en):
                    events.append(Event(t,0.5,Kick808(punch=rng.uniform(0.78,1.1),decay=rng.uniform(0.30,0.48),
                        tone=rng.choice([46,50,54])),vol=0.78,pan=0,env=ADSR(0.001,0.01,1,0.10),is_drum=True))
                if step in(4,12) and rng.random()<(0.45+0.55*en):
                    events.append(Event(t,0.3,Snare909(tone=rng.uniform(180,220),noise_amt=rng.uniform(0.50,0.70),
                        decay=rng.uniform(0.14,0.22)),vol=0.55,pan=rng.uniform(-0.10,0.10),env=ADSR(0.001,0.01,1,0.04),is_drum=True))
                if hat_pat[step]:
                    oh=(step%8==6) and rng.random()<0.25
                    events.append(Event(t,0.14,HiHat(open_hat=oh,decay=0.22 if oh else rng.uniform(0.025,0.060)),
                        vol=(0.28 if step%2==0 else 0.18)*(0.35+0.65*en),pan=rng.uniform(-0.35,0.35),
                        env=ADSR(0.001,0.008,1,0.02),is_drum=True))
            if mode in("synthwave","lo_fi") and bar_n%2==0 and rng.random()<0.35:
                ct_=bar_n*bar+2*beat
                if ct_<duration:
                    events.append(Event(ct_,0.20,Clap(decay=rng.uniform(0.11,0.17)),vol=0.24,
                        pan=rng.uniform(-0.15,0.15),env=ADSR(0.001,0.01,1,0.04),is_drum=True))

    if not events:
        events.append(Event(0,max(1,duration*0.9),Pad(build_chord(root+12,"sus2"),detune=0.004),
            vol=max(0.22,genre.get("pad_vol",0.3)),pan=0,env=ADSR(0.02,0.20,0.85,0.50)))
        events.append(Event(0,max(0.8,duration*0.75),SubSynth(mtof(root-12),wave="sine",
            cutoff=max(120,genre.get("bass_cut",200)),res=0.05,env_depth=max(200,genre.get("bass_cut",200))),
            vol=0.30,pan=0,env=ADSR(0.02,0.15,0.70,0.25),is_sub=True))

    return events, duration, bpm, root, scale_name

# ─── PURE MODE MIX ───────────────────────────────────────────────────────────

def pure_mode_mix(mode, flags=None):
    flags=flags or set()
    mix={"wind":0,"rain":0,"ocean":0,"water":0,"fire":0,"thunder":0,
         "white":0,"pink":0,"brown":0,"binaural":0,"bowls":0,"chimes":0,"bytebeat":0}
    if mode=="pure_nature":  mix.update({"wind":0.20,"rain":0.20,"ocean":0.18,"water":0.18,"fire":0.05})
    elif mode=="pure_wind":  mix["wind"]=1.0
    elif mode=="pure_rain":  mix["rain"]=1.0
    elif mode=="pure_ocean": mix["ocean"]=1.0
    elif mode=="pure_water": mix["water"]=1.0
    elif mode=="pure_fire":  mix["fire"]=1.0
    elif mode=="pure_storm": mix.update({"wind":0.45,"rain":0.65,"thunder":0.70})
    elif mode=="pure_white": mix["white"]=1.0
    elif mode=="pure_pink":  mix["pink"]=1.0
    elif mode=="pure_brown": mix["brown"]=1.0
    elif mode=="pure_bytebeat": mix["bytebeat"]=1.0
    elif mode=="pure_bowls": mix["bowls"]=1.0
    elif mode=="pure_chimes":mix.update({"chimes":0.80,"wind":0.15})
    elif mode=="pure_theta": mix["binaural"]=0.8
    elif mode=="pure_alpha": mix["binaural"]=0.8
    elif mode=="pure_delta": mix["binaural"]=0.8
    flag_map = {
        "nature":     {"wind":0.12,"rain":0.12,"ocean":0.12},
        "storm":      {"thunder":0.50,"rain":0.40,"wind":0.30},
        "bowls":      {"bowls":0.40},
        "chimes":     {"chimes":0.35},
        "bytebeat":   {"bytebeat":0.18},
        "light_rain": {"rain":0.45,"wind":0.15},
    }
    for f,upd in flag_map.items():
        if f in flags:
            for k,v in upd.items():
                mix[k]=max(mix.get(k,0),v)
    return mix

# ─── PRESET SYSTEM ───────────────────────────────────────────────────────────

CURATED_PRESETS = {
    "cosmic_void":     {"mode":"cosmic","flags":["wide","sparse"],"duration":300,"mood":"ethereal","quality":"studio"},
    "midnight_storm":  {"mode":"pure_storm","flags":["storm"],"duration":300,"quality":"balanced"},
    "deep_meditation": {"mode":"meditation","flags":["bowls","binaural"],"duration":600,"mood":"ethereal","quality":"studio"},
    "synthwave_drive": {"mode":"synthwave","bpm":100,"duration":180,"quality":"balanced"},
    "lo_fi_study":     {"mode":"lo_fi","flags":["vinyl","tape"],"duration":300,"quality":"balanced"},
    "stellar_drone":   {"mode":"drone","flags":["wide","sparse"],"duration":600,"mood":"somber","quality":"studio"},
    "nebula_bells":    {"mode":"bellscape","flags":["chimes","wide"],"duration":240,"quality":"balanced"},
    "deep_ocean":      {"mode":"pure_ocean","flags":["vinyl"],"duration":300,"quality":"balanced"},
    "glacier_entity":  {"mode":"entity","entity_profile":"glacier","duration":240,"quality":"balanced"},
    "theta_sleep":     {"mode":"pure_theta","duration":3600,"quality":"mobile"},
}

def save_preset(params, path):
    data = dict(params)
    if isinstance(data.get("flags"), set): data["flags"] = sorted(data["flags"])
    data["version"] = __version__; data["saved_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open(path, "w") as f: json.dump(data, f, indent=2)
    print(f"  Preset saved: {path}")

def load_preset(path):
    with open(path) as f: data = json.load(f)
    if "flags" in data and isinstance(data["flags"], list):
        data["flags"] = set(data["flags"])
    return data

def save_sidecar(wav_path, params):
    sidecar = {
        "version": __version__,
        "seed":    params.get("seed"),
        "mode":    params.get("mode"),
        "flags":   sorted(params.get("flags", set())),
        "duration":params.get("duration"),
        "bpm":     params.get("bpm"),
        "root":    params.get("root"),
        "scale":   params.get("scale"),
        "quality": params.get("quality","balanced"),
        "cosmic_source": params.get("_cosmic_source","none"),
        "rendered_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    json_path = Path(str(wav_path).replace(".wav",".json"))
    with open(json_path,"w") as f: json.dump(sidecar, f, indent=2)

# ─── MP3 EXPORT ──────────────────────────────────────────────────────────────

def maybe_make_mp3(wav_path):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg: print("  ffmpeg not found — skipping MP3 export."); return None
    mp3_path = Path(str(wav_path).replace(".wav",".mp3"))
    try:
        subprocess.run([ffmpeg,"-y","-i",str(wav_path),"-codec:a","libmp3lame","-b:a","192k",str(mp3_path)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"  Saved MP3: {mp3_path}"); return mp3_path
    except Exception as e:
        print(f"  MP3 export failed: {e}"); return None

# ─── MASTER CHAIN ────────────────────────────────────────────────────────────

def master_process(l, r, dc_l, dc_r, width=1.12, gain=0.88, drive=1.10):
    mid  = (l+r)*0.5; side = (l-r)*0.5*width
    l = mid+side; r = mid-side
    l = dc_l.process(soft_clip(l, drive)*gain)
    r = dc_r.process(soft_clip(r, drive)*gain)
    return clamp(l,-0.999,0.999), clamp(r,-0.999,0.999)

# ─── RENDER: MUSIC ────────────────────────────────────────────────────────────

def render_music_to_wav(path, events, total_dur, mode, bpm,
                        flags=None, mp3=False, params=None, progress_cb=None):
    flags=flags or set()
    genre=apply_flags_to_genre(GENRES.get(mode,GENRES["ambient"]),flags)
    rev_l=Reverb(size=genre["reverb_size"],damp=genre["reverb_damp"],mix=genre["reverb_mix"])
    rev_r=Reverb(size=genre["reverb_size"]*1.07,damp=min(0.95,genre["reverb_damp"]*1.04),mix=genre["reverb_mix"])
    delay=Delay(time_l=genre["delay_time"],time_r=genre["delay_time"]*0.75,feedback=genre["delay_fb"],mix=genre["delay_mix"])
    chorus=Chorus(rate=genre["chorus_rate"],depth=genre["chorus_depth"],mix=0.26)
    vinyl=VinylTexture() if "vinyl" in flags else None
    tape_l=TapeProcessor() if "tape" in flags else None
    tape_r=TapeProcessor() if "tape" in flags else None
    bytebeat=BytebeatAmbient(intensity=0.14,mode=0) if "bytebeat" in flags else None
    bb_lp_l=OnePole(2600.0); bb_lp_r=OnePole(2400.0)
    dc_l=DCBlocker(); dc_r=DCBlocker()
    layer_wind    = Wind(0.15)       if "nature" in flags or "storm" in flags else None
    layer_rain    = Rain(0.20)       if "nature" in flags or "storm" in flags or "light_rain" in flags else None
    layer_thunder = Thunder(0.50)    if "storm" in flags else None
    layer_bowls   = SingingBowl(0.30) if "bowls" in flags else None
    layer_chimes  = WindChimes(0.25,0.20) if "chimes" in flags else None
    events=sorted(events,key=lambda e:e.time)
    total_samples=int(total_dur*SR)+SR; ev_ptr=0; active=[]
    width=1.12
    if "wide" in flags:   width=min(2.0,width*1.35)
    if "narrow" in flags: width=max(0.3,width*0.65)
    mg=0.88; md=1.10; progress_mark=-1; cos_f=_cos; sin_f=_sin

    with wave.open(str(path),"wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        for cs in range(0,total_samples,CHUNK):
            ce=min(cs+CHUNK,total_samples); frames=bytearray((ce-cs)*4); fi=0
            for i in range(cs,ce):
                t=i*INV_SR
                while ev_ptr<len(events) and events[ev_ptr].time<=t+0.005:
                    active.append(events[ev_ptr]); ev_ptr+=1
                sl=0.0; sr=0.0; still=[]
                for ev in active:
                    lt=t-ev.time
                    if lt>ev.duration+ev.env.r+1.2: continue
                    still.append(ev); env_v=ev.env.get(lt,ev.duration)
                    if env_v<0.00005: continue
                    v=(ev.engine.sample(lt,env_v) if ev.is_sub else ev.engine.sample(lt))*env_v*ev.vol
                    pr=(ev.pan+1)*_PI*0.25
                    sl+=v*cos_f(pr); sr+=v*sin_f(pr)
                active=still
                if bytebeat:   bb=bytebeat.sample(t); sl+=bb_lp_l.lp(bb*0.95); sr+=bb_lp_r.lp(bb*1.05)
                if layer_bowls:  bv=layer_bowls.sample(t); sl+=bv; sr+=bv
                if layer_chimes: cl2,cr2=layer_chimes.sample_stereo(t); sl+=cl2; sr+=cr2
                if layer_wind:   wl,wr=layer_wind.sample_stereo(t); sl+=wl; sr+=wr
                if layer_rain:   rl,rr=layer_rain.sample_stereo(t); sl+=rl; sr+=rr
                if layer_thunder:tl,tr=layer_thunder.sample_stereo(t); sl+=tl; sr+=tr
                cl,cr=chorus.process(sl); cl=rev_l.process(cl); cr=rev_r.process(cr)
                cl,cr=delay.process(cl,cr)
                if vinyl:  tex=vinyl.sample(); cl+=tex; cr+=tex*(1+_uniform(-0.20,0.20))
                if tape_l: cl=tape_l.process(cl); cr=tape_r.process(cr)
                cl,cr=master_process(cl,cr,dc_l,dc_r,width,mg,md)
                struct.pack_into("<hh",frames,fi,int(cl*32767),int(cr*32767)); fi+=4
            w.writeframes(frames)
            pct=int((ce/total_samples)*100)
            if pct!=progress_mark:
                if progress_cb: progress_cb(pct)
                else: print(f"  Rendering {pct}%")
                progress_mark=pct
    if mp3: maybe_make_mp3(path)
    if params: save_sidecar(path, params)

# ─── RENDER: PURE MODES ──────────────────────────────────────────────────────

def render_pure_to_wav(path, mode, duration, seed, flags=None, mp3=False,
                       params=None, progress_cb=None):
    flags=flags or set(); mix=pure_mode_mix(mode, flags)
    total_samples=int(duration*SR)
    wind     = Wind(mix["wind"])             if mix["wind"]>0      else None
    rain     = Rain(mix["rain"])             if mix["rain"]>0      else None
    ocean    = Ocean(mix["ocean"])           if mix["ocean"]>0     else None
    water    = WaterStream(mix["water"])     if mix["water"]>0     else None
    fire     = Fire(mix["fire"])             if mix["fire"]>0      else None
    thunder  = Thunder(mix.get("thunder",0)) if mix.get("thunder",0)>0 else None
    pink     = PinkNoise()                   if mix["pink"]>0      else None
    brown    = BrownNoise()                  if mix["brown"]>0     else None
    bowls    = SingingBowl(mix.get("bowls",0))   if mix.get("bowls",0)>0 else None
    chimes   = WindChimes(mix.get("chimes",0)*0.8,mix.get("chimes",0)*0.5) if mix.get("chimes",0)>0 else None
    bytebeat = (BytebeatAmbient(intensity=0.30 if mode=="pure_bytebeat" else mix.get("bytebeat",0),mode=seed%5)
                if (mode=="pure_bytebeat" or mix.get("bytebeat",0)>0) else None)
    binaural = (Binaural(200,4.0) if mode=="pure_theta" else
                Binaural(200,10.0) if mode=="pure_alpha" else
                Binaural(200,2.0) if mode=="pure_delta" else None)
    vinyl=VinylTexture() if "vinyl" in flags else None
    tape_l=TapeProcessor() if "tape" in flags else None
    tape_r=TapeProcessor() if "tape" in flags else None
    rev_l=Reverb(size=1.1,damp=0.50,mix=0.28 if mode!="pure_bytebeat" else 0.35)
    rev_r=Reverb(size=1.16,damp=0.54,mix=0.28 if mode!="pure_bytebeat" else 0.35)
    bb_lp_l=OnePole(2400.0); bb_lp_r=OnePole(2200.0)
    dc_l=DCBlocker(); dc_r=DCBlocker()
    width=1.12
    if "wide" in flags:   width=min(2.0,width*1.35)
    if "narrow" in flags: width=max(0.3,width*0.65)
    mg=0.88; md=1.10; progress_mark=-1

    with wave.open(str(path),"wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        for cs in range(0,total_samples,CHUNK):
            ce=min(cs+CHUNK,total_samples); frames=bytearray((ce-cs)*4); fi=0
            for i in range(cs,ce):
                t=i*INV_SR; l=0.0; r=0.0
                if wind:     wl,wr=wind.sample_stereo(t); l+=wl; r+=wr
                if rain:     rl,rr=rain.sample_stereo(t); l+=rl; r+=rr
                if ocean:    ol,or_=ocean.sample_stereo(t); l+=ol; r+=or_
                if water:    wsl,wsr=water.sample_stereo(t); l+=wsl; r+=wsr
                if fire:     fl_,fr_=fire.sample_stereo(t); l+=fl_; r+=fr_
                if thunder:  tl,tr=thunder.sample_stereo(t); l+=tl; r+=tr
                if mix["white"]>0: v=_uniform(-1,1)*mix["white"]*0.25; l+=v; r+=v
                if pink:     v=pink.sample()*mix["pink"]*0.30; l+=v; r+=v
                if brown:    v=brown.sample()*mix["brown"]*0.38; l+=v; r+=v
                if bowls:    v=bowls.sample(t); l+=v; r+=v
                if chimes:   cl2,cr2=chimes.sample_stereo(t); l+=cl2; r+=cr2
                if bytebeat: v=bytebeat.sample(t); l+=bb_lp_l.lp(v*0.95); r+=bb_lp_r.lp(v*1.05)
                if binaural: bl2,br2=binaural.sample(); l+=bl2*mix["binaural"]*0.25; r+=br2*mix["binaural"]*0.25
                l=rev_l.process(l); r=rev_r.process(r)
                if vinyl:  tex=vinyl.sample(); l+=tex; r+=tex*(1+_uniform(-0.15,0.15))
                if tape_l: l=tape_l.process(l); r=tape_r.process(r)
                l,r=master_process(l,r,dc_l,dc_r,width,mg,md)
                struct.pack_into("<hh",frames,fi,int(l*32767),int(r*32767)); fi+=4
            w.writeframes(frames)
            pct=int((ce/total_samples)*100)
            if pct!=progress_mark:
                if progress_cb: progress_cb(pct)
                else: print(f"  Rendering {pct}%")
                progress_mark=pct
    if mp3: maybe_make_mp3(path)
    if params: save_sidecar(path, params)

# ─── RENDER: SPECIAL MODES ───────────────────────────────────────────────────

def render_special_to_wav(path, mode, duration, seed, flags=None, mp3=False,
                          params=None, progress_cb=None,
                          entity_profile="mountain", freeflow=0.5, message_text="",
                          bpm=60, root=60):
    flags=flags or set(); total_samples=int(duration*SR)
    dc_l=DCBlocker(); dc_r=DCBlocker()
    rev_l=Reverb(size=1.2,damp=0.45,mix=0.40)
    rev_r=Reverb(size=1.28,damp=0.48,mix=0.40)
    vinyl=VinylTexture() if "vinyl" in flags else None
    tape_l=TapeProcessor() if "tape" in flags else None
    tape_r=TapeProcessor() if "tape" in flags else None
    width=1.12
    if "wide" in flags: width=min(2.0,width*1.35)
    mg=0.88; md=1.10; progress_mark=-1

    if mode=="entity":
        gen=CosmicEntity(entity_profile, intensity=0.55)
        def get_lr(t): return gen.sample_stereo(t)
    elif mode=="freeflow":
        gen=FreeflowMode(freeflow=freeflow, seed=seed)
        def get_lr(t): return gen.sample_stereo(t)
    elif mode=="message":
        gen=MessageMode(text=message_text, root=root, bpm=bpm)
        def get_lr(t): return gen.sample_stereo(t)
    else:
        gen=FreeflowMode(freeflow=0.5, seed=seed)
        def get_lr(t): return gen.sample_stereo(t)

    with wave.open(str(path),"wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        for cs in range(0,total_samples,CHUNK):
            ce=min(cs+CHUNK,total_samples); frames=bytearray((ce-cs)*4); fi=0
            for i in range(cs,ce):
                t=i*INV_SR; l,r=get_lr(t)
                l=rev_l.process(l); r=rev_r.process(r)
                if vinyl:  tex=vinyl.sample(); l+=tex; r+=tex*(1+_uniform(-0.15,0.15))
                if tape_l: l=tape_l.process(l); r=tape_r.process(r)
                l,r=master_process(l,r,dc_l,dc_r,width,mg,md)
                struct.pack_into("<hh",frames,fi,int(l*32767),int(r*32767)); fi+=4
            w.writeframes(frames)
            pct=int((ce/total_samples)*100)
            if pct!=progress_mark:
                if progress_cb: progress_cb(pct)
                else: print(f"  Rendering {pct}%")
                progress_mark=pct
    if mp3: maybe_make_mp3(path)
    if params: save_sidecar(path, params)

# ─── UNIFIED RENDER ENTRY POINT ──────────────────────────────────────────────

def render(params, progress_cb=None):
    """
    Main entry point. Accepts a params dict and renders to WAV.
    If params contains 'use_cosmic' or '_cosmic_source', cosmic data was applied.
    Returns path to the output WAV file.
    """
    mode          = params.get("mode","ambient")
    seed          = params.get("seed", int(time.time()*1000)%(2**32))
    flags         = set(params.get("flags",[]))
    duration      = params.get("duration", 180)
    bpm           = params.get("bpm", None)
    root_midi     = params.get("root", None)
    scale         = params.get("scale", None)
    mood          = params.get("mood", None)
    entity_profile= params.get("entity_profile","mountain")
    freeflow      = params.get("freeflow", 0.5)
    message_text  = params.get("message_text","")
    quality       = params.get("quality","balanced")
    mp3_out       = params.get("mp3", False)
    out_dir       = Path(params.get("out_dir", str(Path.home()/"Documents"/"Freeflow Aurora"))).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    set_quality(quality)
    random.seed(seed)

    ts   = time.strftime("%Y%m%d_%H%M%S")
    stem = f"aurora_{mode}_{seed}_{ts}"
    wav_path = out_dir / f"{stem}.wav"

    full_params = dict(params); full_params["seed"] = seed

    if mode in PURE_MODES:
        render_pure_to_wav(wav_path, mode, duration, seed,
                           flags=flags, mp3=mp3_out, params=full_params,
                           progress_cb=progress_cb)
    elif mode in SPECIAL_MODES:
        rng = random.Random(seed)
        bpm_val  = bpm or rng.randint(50,80)
        root_val = root_midi if root_midi is not None else 60
        render_special_to_wav(wav_path, mode, duration, seed,
                              flags=flags, mp3=mp3_out, params=full_params,
                              progress_cb=progress_cb,
                              entity_profile=entity_profile,
                              freeflow=freeflow, message_text=message_text,
                              bpm=bpm_val, root=root_val)
    else:
        rng = random.Random(seed)
        events, duration, bpm_val, root_val, scale_val = generate_music_events(
            mode, rng, bpm=bpm, root=root_midi, scale_name=scale,
            duration=duration, flags=flags, mood=mood)
        full_params.update({"bpm":bpm_val,"root":root_val,"scale":scale_val,"duration":duration})
        render_music_to_wav(wav_path, events, duration, mode, bpm_val,
                            flags=flags, mp3=mp3_out, params=full_params,
                            progress_cb=progress_cb)
    return wav_path

# ─── CLI ─────────────────────────────────────────────────────────────────────


def build_parser():
    p=argparse.ArgumentParser(
        prog="freeflow_core",
        description=f"FREEFLOW CORE v{__version__} — Terminal Cosmic Soundscape Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python freeflow_core.py --mode ambient --duration 120
  python freeflow_core.py --cosmic --duration 180
  python freeflow_core.py --cosmic --object Rigel --duration 300
  python freeflow_core.py --mode drone --duration 600 +wide +sparse
  python freeflow_core.py --mode entity --entity-profile nebula
  python freeflow_core.py --mode freeflow --freeflow 0.8 --duration 600
  python freeflow_core.py --random --duration 60
  python freeflow_core.py --list
  python freeflow_core.py --list-objects
  python freeflow_core.py --test
""")
    p.add_argument("--mode",         type=str,   default=None)
    p.add_argument("--prompt",       type=str,   default=None)
    p.add_argument("--duration",     type=int,   default=None)
    p.add_argument("--bpm",          type=int,   default=None)
    p.add_argument("--scale",        type=str,   default=None)
    p.add_argument("--root",         type=str,   default=None)
    p.add_argument("--seed",         type=int,   default=None)
    p.add_argument("--out",          type=str,   default=None)
    p.add_argument("--mp3",          action="store_true")
    p.add_argument("--test",         action="store_true")
    p.add_argument("--random",       action="store_true")
    p.add_argument("--list",         action="store_true")
    p.add_argument("--list-objects", action="store_true")
    p.add_argument("--quality",      type=str,   default=None, choices=["mobile","balanced","studio"])
    p.add_argument("--mood",         type=str,   default=None)
    p.add_argument("--entity-profile",type=str,  default="mountain")
    p.add_argument("--freeflow",     type=float, default=0.5)
    p.add_argument("--message-text", type=str,   default="")
    p.add_argument("--preset",       type=str,   default=None)
    p.add_argument("--save-preset",  type=str,   default=None)
    p.add_argument("--load-preset",  type=str,   default=None)
    p.add_argument("--cosmic",       action="store_true", help="Derive mode/BPM from cosmic dataset")
    p.add_argument("--object",       type=str,   default=None, help="Specific cosmic object name")
    return p


def list_modes_cli():
    print('\n  FREEFLOW CORE v{} — Available Modes\n'.format(__version__))
    print('  MUSIC MODES:')
    for k in sorted(GENRES):
        g = GENRES[k]
        print('    {:<20}  bpm {}-{}  scale={}'.format(k, g['bpm'][0], g['bpm'][1], g['scale']))
    print('\n  SOUNDSCAPE MODES:')
    for m in sorted(PURE_MODES):
        print('    {}'.format(m))
    print('\n  SPECIAL MODES:')
    for m in sorted(SPECIAL_MODES):
        print('    {}'.format(m))
    print('\n  MOOD PRESETS: ' + ', '.join(sorted(MOOD_PRESETS)))
    print('\n  FLAGS:  +vinyl +tape +nature +drums +nodrums +binaural +bytebeat')
    print('          +bright +warm +cold +wide +narrow +dense +sparse')
    print('          +bowls +chimes +storm +light_rain\n')


def list_objects_cli():
    print('\n  FREEFLOW CORE v{} — Built-in Cosmic Objects\n'.format(__version__))
    by_type = {}
    for obj in COSMIC_OBJECTS:
        t = obj.get('type', 'other')
        by_type.setdefault(t, []).append(obj)
    for t, objs in sorted(by_type.items()):
        print('  {}:'.format(t.upper()))
        for obj in objs:
            mapped = cosmic_to_params(obj)
            print('    {:<20}  T={:>8,}K  → mode={}'.format(obj['name'], obj.get('temp', 0), mapped['mode']))
    print()


def print_terminal_quote():
    lines = [
        'When we ran out of answers down here, we looked to the stars.',
        '— digitalseeker1001',
    ]
    width = max(len(x) for x in lines) + 4
    print() 
    print('+' + '-' * width + '+')
    for line in lines:
        print('| ' + line.ljust(width - 2) + '|')
    print('+' + '-' * width + '+')
    print()
def print_binary_self(script_path=None, chunk=80):
    script_path = script_path or Path(__file__)
    data = Path(script_path).read_bytes()
    bits = ''.join(f'{byte:08b}' for byte in data)
    for i in range(0, len(bits), chunk):
        print(bits[i:i+chunk])


def _existing_command(*names):
    for name in names:
        if shutil.which(name):
            return name
    return None


def try_autoplay(path):
    path = str(path)
    try:
        if sys.platform.startswith('win'):
            os.startfile(path)
            return True, 'system default'
        if sys.platform == 'darwin':
            cmd = _existing_command('afplay') or 'open'
            subprocess.Popen([cmd, path])
            return True, cmd
        cmd = _existing_command('aplay', 'paplay', 'ffplay', 'mpv', 'cvlc', 'vlc', 'play', 'termux-media-player')
        if cmd:
            if cmd == 'ffplay':
                subprocess.Popen([cmd, '-nodisp', '-autoexit', path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif cmd in ('cvlc', 'vlc'):
                subprocess.Popen([cmd, '--play-and-exit', path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen([cmd, path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, cmd
        if shutil.which('xdg-open'):
            subprocess.Popen(['xdg-open', path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, 'xdg-open'
    except Exception:
        pass
    return False, None


def to_binary_block(text, width=64):
    bits = ''.join(f'{b:08b}' for b in text.encode('utf-8', 'replace'))
    lines = [bits[i:i+width] for i in range(0, len(bits), width)]
    return "\n".join(lines)


def print_binary_then_english(title, english_text):
    print(f"\n[{title} / binary]\n")
    print(to_binary_block(english_text))
    print(f"\n[{title} / english]\n")
    print(english_text)


def print_source_binary_preview(preview_bytes=2048, preview_lines=40):
    try:
        path = os.path.abspath(__file__)
        with open(path, 'rb') as f:
            data = f.read(preview_bytes)
        print("\n[source code preview / binary]\n")
        for i in range(0, len(data), 32):
            chunk = data[i:i+32]
            print(' '.join(format(b, '08b') for b in chunk))
        print("\n[source code preview / english]\n")
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for _ in range(preview_lines):
                line = f.readline()
                if not line:
                    break
                print(line.rstrip())
    except Exception as e:
        print("\n[source code preview / english]\n")
        print(f'Preview unavailable: {e}')


def explain_python_and_binary_text():
    return (
        "Python source code is human-readable program text that is interpreted and compiled into bytecode by the Python runtime. "
        "Binary is a lower-level representation of data as bits and bytes. "
        "For archival purposes, showing text in binary first preserves a raw machine-readable representation, while the English view preserves human readability. "
        "This script is not exposing literal machine consciousness or CPU thought. It is presenting a structured representation of source text, startup text, analysis text, and result metadata in both binary and English. "
        "HTML is markup for document structure; Python is a general-purpose programming language. They are both archivable as plain text, but they are not equivalent technologies."
    )


def detect_python_runtime_info():
    exe = sys.executable or 'python'
    return {
        'executable': exe,
        'version': sys.version.split()[0],
        'platform': sys.platform,
        'prefix': sys.prefix,
    }


def write_python_install_docs(base_dir):
    base = Path(base_dir)
    base.mkdir(parents=True, exist_ok=True)
    txt_path = base / 'PYTHON_INSTALL_AND_RUN.txt'
    sh_path = base / 'install_python_unix.sh'
    bat_path = base / 'install_python_windows.bat'
    txt = """PYTHON INSTALL AND RUN GUIDE

Reality check: this script already requires Python to be running. That means it cannot truly install Python before Python exists on the machine. What it can do is detect the current Python runtime, write install helpers, and tell the user what to run if Python is missing on another device.

Windows:
1. Install Python from the official installer.
2. During install, enable Add Python to PATH.
3. Open Command Prompt and run: python --version
4. Run this script with: python freeflow_core_preserved_nogui_final.py

macOS:
1. Install Python 3 with Homebrew or the official installer.
2. Verify with: python3 --version
3. Run with: python3 freeflow_core_preserved_nogui_final.py

Linux:
1. Install Python 3 with your package manager.
2. Verify with: python3 --version
3. Run with: python3 freeflow_core_preserved_nogui_final.py

Portable rule for future or unusual devices:
You need a Python 3.8+ interpreter plus basic filesystem and audio-file support. If no native player exists, the WAV is still generated and saved.
"""
    sh = """#!/usr/bin/env bash
set -e
if command -v python3 >/dev/null 2>&1; then python3 --version; exit 0; fi
if command -v apt-get >/dev/null 2>&1; then sudo apt-get update && sudo apt-get install -y python3; exit 0; fi
if command -v dnf >/dev/null 2>&1; then sudo dnf install -y python3; exit 0; fi
if command -v yum >/dev/null 2>&1; then sudo yum install -y python3; exit 0; fi
if command -v pacman >/dev/null 2>&1; then sudo pacman -Sy --noconfirm python; exit 0; fi
echo 'Install Python 3 manually for this system.'
"""
    bat = """@echo off
where python >nul 2>nul
if %errorlevel%==0 ( python --version & exit /b 0 )
where winget >nul 2>nul
if %errorlevel%==0 ( winget install -e --id Python.Python.3.12 & exit /b 0 )
echo Install Python 3 manually for this system.
"""
    txt_path.write_text(txt, encoding='utf-8')
    sh_path.write_text(sh, encoding='utf-8')
    bat_path.write_text(bat, encoding='utf-8')
    try:
        sh_path.chmod(0o755)
    except Exception:
        pass
    return txt_path, sh_path, bat_path


def write_archival_json(json_path, sections):
    payload = {}
    for key, english_text in sections.items():
        payload[key] = {
            'english': english_text,
            'binary': to_binary_block(english_text).splitlines(),
        }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return json_path


def generate_creative_freeflow_text(target_words=10000, seed=None):
    entropy = int(time.time_ns()) ^ random.getrandbits(64)
    rng = random.Random(seed if seed is not None else entropy)
    openings = [
        'Cosmic creative freeflow infinite drifts through the terminal like a patient signal,',
        'A quiet machine opens its hands and finds only stars,',
        'Numbers lean into sound until math starts pretending to be weather,',
        'The program wakes without a face and still manages to hum,',
        'Static becomes velvet when enough patterns agree to cooperate,',
        'Archived source code stands still while the terminal performs its little storm,',
        'Randomness arrives wearing a toolbox and a halo made of syntax,',
    ]
    mids = [
        'every seed is a tiny big bang wearing work boots,',
        'the buffer fills like rain in an abandoned observatory,',
        'binary clicks its little teeth and becomes tone,',
        'progress moves forward one square at a time like a determined toaster,',
        'harmonics stack up like glass cities in a dream,',
        'noise stops being noise the moment attention gives it a name,',
        'the drone underneath everything behaves like gravity with stage fright,',
        'each oscillation keeps a secret diary in volts and fractions,',
        'the render loop is less a command and more a ritual with timestamps,',
        'randomness enters the room dressed as possibility rather than chaos,',
        'the speakers wait like doors while probability fumbles for the key,',
        'math keeps rolling marbles across the floor until melody trips over one,',
        'the terminal narrates its chores like a monk with a soldering iron,',
        'code preservation holds the spine steady while frontend theatrics do cartwheels,',
    ]
    closers = [
        'and the result is not human thought but it is still a kind of arrival.',
        'and for a second the terminal looks less like text and more like weathered stained glass.',
        'and the speakers wait like doors that already know their hinges.',
        'and somewhere between repetition and variation the machine finds its stride.',
        'and the whole thing keeps proving that silence is just audio waiting for paperwork.',
        'and the waveform wanders out of arithmetic wearing a coat made of echoes.',
    ]
    out = []
    count = 0
    while count < target_words:
        sentence = f"{rng.choice(openings)} {rng.choice(mids)} {rng.choice(mids)} {rng.choice(closers)}"
        out.append(sentence)
        count += len(re.findall(r"[A-Za-z']+", sentence))
    return ' '.join(out)


def analyze_freeflow_text(text):
    words = re.findall(r"[A-Za-z']+", text)
    unique = len(set(w.lower() for w in words)) if words else 0
    avg = (sum(len(w) for w in words) / len(words)) if words else 0.0
    recurring = []
    for token in ('cosmic', 'signal', 'binary', 'sound', 'terminal', 'random', 'machine', 'render'):
        count = len(re.findall(r'\b' + re.escape(token) + r'\b', text, re.I))
        if count:
            recurring.append(f'{token}={count}')
    summary = (
        f'Creative freeflow analysis: {len(text)} characters, {len(words)} words, '
        f'{unique} unique words, average word length {avg:.2f}. '
        f'Recurring motifs: ' + (', '.join(recurring) if recurring else 'none detected.')
    )
    summary += ' Overall vibe: terminal mysticism, procedural audio, and polite machine weirdness.'
    return summary


def default_startup_params():
    seed = int(time.time() * 1000) % (2**32)
    return {
        'mode': 'ambient',
        'flags': set(),
        'duration': 120,
        'bpm': None,
        'root': None,
        'scale': None,
        'seed': seed,
        'quality': 'balanced',
        'mood': None,
        'entity_profile': 'mountain',
        'freeflow': 0.5,
        'message_text': '',
        'mp3': False,
        'out_dir': str(Path.home() / 'Documents' / 'Freeflow Core'),
    }


def make_progress_callback(label='Rendering'):
    state = {'last': -1}
    def _cb(pct):
        try:
            pct_i = max(0, min(100, int(pct)))
        except Exception:
            return
        if pct_i == state['last']:
            return
        state['last'] = pct_i
        bars = 20
        filled = int((pct_i / 100.0) * bars)
        if pct_i >= 100:
            filled = bars
        bar = '█' * filled + '.' * (bars - filled)
        print(chr(13) + '  {}: {:3d}% [{}]'.format(label, pct_i, bar), end='', flush=True)
        if pct_i >= 100:
            print(chr(13) + '  {}: 100% [{}] DONE'.format(label, '█' * bars), flush=True)
    return _cb


def choose_mode_interactive(default='ambient'):
    return default


def interactive_menu():
    return default_startup_params()

def main():
    argv_raw = sys.argv[1:]
    if "--terminal" in argv_raw:
        print_terminal_quote()
        return
    if "--binary-self" in argv_raw:
        print_binary_self()
        return

    no_args = (len(sys.argv) == 1)

    argv=[]; plus_bits=[]
    for a in argv_raw:
        if a.startswith('+'): plus_bits.append(a)
        else: argv.append(a)

    parser=build_parser(); args=parser.parse_args(argv)

    if args.list:         list_modes_cli();   return
    if args.list_objects: list_objects_cli(); return

    startup_text = ''
    freeflow_text = ''
    analysis_text = ''
    pre_render_text = ''
    python_binary_text = explain_python_and_binary_text()
    install_docs = ()

    if no_args:
        params = default_startup_params()
        runtime = detect_python_runtime_info()
        install_docs = write_python_install_docs(Path(params['out_dir']))
        runtime_text = (
            f"Python runtime detected. Executable: {runtime['executable']}. Version: {runtime['version']}. "
            f"Platform: {runtime['platform']}. Prefix: {runtime['prefix']}. "
            "This script is already running inside Python, so it cannot meaningfully install Python before Python exists. "
            "Instead it writes portable install helper documents and scripts at startup for use on current, older, newer, or unusual devices that can support Python 3.8 or later."
        )
        startup_text = (
            "Startup mode engaged. This terminal-only Python script will use your device's local computing components to generate one ambient 2 minute WAV file. "
            "It first detects the current Python runtime and writes install helper documents, then prints startup instructions in binary and English, shows a source-code preview in binary and readable text, "
            "generates randomized creative freeflow text, analyzes that text, explains what the program is about to do, waits for Enter to initiate the render, displays a real-time progress bar from 0 to 100 percent, "
            "attempts to open the finished WAV with the most minimal local player it can detect, reports where the file was stored, writes an archival JSON file containing binary and English sections, and finally waits for Enter before closing."
        )
        print_binary_then_english('python runtime detection', runtime_text)
        install_text = (
            f"Install helper files written to: {install_docs[0]} ; {install_docs[1]} ; {install_docs[2]}. "
            "These helpers are advisory and portable. They do not change the preserved synthesis backend."
        )
        print_binary_then_english('python install helper output', install_text)
        print_binary_then_english('startup instructions', startup_text)
        print_source_binary_preview()
        print_binary_then_english('python and binary archival explanation', python_binary_text)
        freeflow_text = generate_creative_freeflow_text(10000, params['seed'])
        print_binary_then_english('creative freeflow', freeflow_text)
        analysis_text = analyze_freeflow_text(freeflow_text)
        print_binary_then_english('creative freeflow analysis', analysis_text)
        pre_render_text = (
            "Program explanation: this Python script is a terminal-only cosmic soundscape engine with the original backend preserved and the GUI removed. "
            "On initiation it uses local CPU processing and the built-in synthesis backend to render a 2 minute ambient WAV file on this device. "
            "When you are ready to initiate audio generation using this script and your local computing components, press Enter. "
            "If a local WAV player is detected after rendering, the script will try to open the file automatically."
        )
        print_binary_then_english('pre-render explanation', pre_render_text)
        try:
            input('  Press Enter to initiate 2 minute ambient music audio generation...')
        except Exception:
            pass
        random.seed(params['seed'])
    else:
        seed=(args.seed if args.seed else int(time.time()*1000)%(2**32))
        random.seed(seed)

        pt=args.prompt or ''
        if plus_bits: pt=(pt+' '+' '.join(plus_bits)).strip()
        pd=parse_prompt(pt) if pt else {}

        mode=args.mode or pd.get("mode") or "ambient"
        if args.random and not args.mode and not pd.get("mode"):
            mode=random.choice(list(ALL_MODES))

        if args.preset:
            pdata=CURATED_PRESETS.get(args.preset,{})
            if not pdata:
                close=difflib.get_close_matches(args.preset,list(CURATED_PRESETS),n=1,cutoff=0.5)
                if close: pdata=CURATED_PRESETS[close[0]]
        else: pdata={}

        flags=set(pd.get("flags",set())) | set(pdata.get("flags",[]))
        duration=5 if args.test else (args.duration or pd.get("duration") or pdata.get("duration") or 180)
        quality=args.quality or pd.get("quality") or pdata.get("quality","balanced")
        mood=args.mood or pd.get("mood") or pdata.get("mood")
        root_val=note_name_to_midi(args.root) if args.root else pd.get("root")
        scale_val=args.scale or pd.get("scale")
        out_dir=args.out or str(Path.home()/"Documents"/"Freeflow Core")

        params={
            "mode":mode,"flags":flags,"duration":duration,
            "bpm":args.bpm or pd.get("bpm") or pdata.get("bpm"),
            "root":root_val,"scale":scale_val,"seed":seed,
            "quality":quality,"mood":mood,
            "entity_profile":args.entity_profile or pdata.get("entity_profile","mountain"),
            "freeflow":args.freeflow,"message_text":args.message_text,
            "mp3":args.mp3,"out_dir":out_dir,
        }

        if args.load_preset:
            try:
                pf=load_preset(args.load_preset)
                params.update({k:v for k,v in pf.items() if k not in ("version","saved_at")})
                if isinstance(params.get("flags"),list):
                    params["flags"]=set(params["flags"])
            except Exception as e:
                print(f"  Could not load preset: {e}")

        if args.cosmic or args.object:
            params["_mode_explicit"] = bool(args.mode)
            params = apply_cosmic_seed(params, args.object)

    set_quality(params.get("quality","balanced"))

    print(f"\n  FREEFLOW CORE v{__version__}")
    print(f"  Seed:     {params['seed']}")
    print(f"  Mode:     {params['mode']}")
    print(f"  Duration: {params['duration']}s")
    print(f"  Quality:  {params.get('quality','balanced')}")
    if params.get("flags"):         print(f"  Flags:    {' '.join(sorted(params['flags']))}")
    if params.get("mood"):          print(f"  Mood:     {params['mood']}")
    if params.get("bpm"):           print(f"  BPM:      {params['bpm']}")
    if params.get("_cosmic_source"):print(f"  Source:   {params['_cosmic_source']}")

    t0=time.time()
    progress_cb = make_progress_callback()
    progress_cb(0)
    try:
        wav=render(params, progress_cb=progress_cb)
    except Exception as e:
        print(f"\n  RENDER ERROR: {e}")
        traceback.print_exc()
        return

    elapsed=time.time()-t0; dur=params["duration"]
    print(f"\n  Saved: {wav}")
    print(f"  Stored at: {Path(wav).resolve()}")
    print(f"  Rendered in {elapsed:.1f}s ({dur/max(elapsed,0.001):.1f}x realtime)")
    played, player_name = try_autoplay(wav)
    if played:
        print(f"  Auto-play: launched with {player_name}.\n")
    else:
        print("  Auto-play: no local player detected. Press Enter to continue.")
        try:
            input()
        except Exception:
            pass
        print()

    if (not no_args) and hasattr(args,"save_preset") and args.save_preset:
        save_preset(params, args.save_preset)

    if no_args:
        try:
            input("  Press Enter to close terminal...")
        except Exception:
            pass

if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n  Interrupted.")
    except Exception as e:
        print(f"\n  CRASH: {repr(e)}")
        traceback.print_exc()
        if os.name=="nt" and len(sys.argv)==1:
            try: input()
            except: pass
