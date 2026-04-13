#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════╗
║  FREEFLOW AMBIENT ∞                                                 ║
║  Cosmic algorithmic music — pure Python stdlib, zero dependencies.  ║
║  Double-click to run. Offline. Infinite. Forever.                   ║
║  MIT License · 2025 FREEFLOW Project                                ║
╚══════════════════════════════════════════════════════════════════════╝

Works on: Windows · macOS · Linux · Android (Pydroid 3 / Termux+tkinter)
Python 3.8+, stdlib only. No pip. No internet. No samples. Just math.
"""

import tkinter as tk
from tkinter import ttk
import threading, queue, os, sys, time, random
import wave, tempfile, subprocess, shutil
from pathlib import Path

# ══════════════════════════════════════════════════════════════════════
#  EMBEDDED FREEFLOW CORE ENGINE  (full source — do not edit below)
# ══════════════════════════════════════════════════════════════════════
FREEFLOW_CORE_SOURCE = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, difflib, json, math, os, random, re, shutil, struct
import subprocess, sys, time, traceback, wave
from pathlib import Path

__version__ = "1.0.0"
__author__  = "FREEFLOW Project"

COSMIC_OBJECTS = [
    {"name":"Sirius A",      "type":"star",   "temp":9940,   "lum":25.4,    "dist":8.6,    "mass":2.02},
    {"name":"Vega",          "type":"star",   "temp":9600,   "lum":40.1,    "dist":25.0,   "mass":2.14},
    {"name":"Arcturus",      "type":"star",   "temp":4286,   "lum":170.0,   "dist":36.7,   "mass":1.08},
    {"name":"Rigel",         "type":"star",   "temp":12100,  "lum":120000,  "dist":860.0,  "mass":21.0},
    {"name":"Betelgeuse",    "type":"star",   "temp":3500,   "lum":126000,  "dist":700.0,  "mass":16.5},
    {"name":"Antares",       "type":"star",   "temp":3660,   "lum":75900,   "dist":550.0,  "mass":12.4},
    {"name":"Polaris",       "type":"star",   "temp":6015,   "lum":2500,    "dist":433.0,  "mass":5.4},
    {"name":"Deneb",         "type":"star",   "temp":8525,   "lum":196000,  "dist":2600.0, "mass":19.0},
    {"name":"Canopus",       "type":"star",   "temp":7400,   "lum":10700,   "dist":310.0,  "mass":8.5},
    {"name":"Aldebaran",     "type":"star",   "temp":3910,   "lum":518.0,   "dist":65.0,   "mass":1.16},
    {"name":"Spica",         "type":"star",   "temp":25300,  "lum":20500,   "dist":250.0,  "mass":11.4},
    {"name":"Fomalhaut",     "type":"star",   "temp":8590,   "lum":16.6,    "dist":25.1,   "mass":1.92},
    {"name":"Proxima Cen",   "type":"star",   "temp":3042,   "lum":0.0017,  "dist":4.24,   "mass":0.12},
    {"name":"Tau Ceti",      "type":"star",   "temp":5344,   "lum":0.52,    "dist":11.9,   "mass":0.78},
    {"name":"Epsilon Eri",   "type":"star",   "temp":5084,   "lum":0.34,    "dist":10.5,   "mass":0.82},
    {"name":"61 Cygni A",    "type":"star",   "temp":4526,   "lum":0.15,    "dist":11.4,   "mass":0.70},
    {"name":"Barnards Star", "type":"star",   "temp":3134,   "lum":0.0035,  "dist":5.96,   "mass":0.17},
    {"name":"Altair",        "type":"star",   "temp":7550,   "lum":10.6,    "dist":16.7,   "mass":1.79},
    {"name":"Procyon A",     "type":"star",   "temp":6530,   "lum":6.93,    "dist":11.5,   "mass":1.50},
    {"name":"Castor A",      "type":"star",   "temp":8840,   "lum":34.0,    "dist":51.5,   "mass":2.76},
    {"name":"Orion Nebula",  "type":"nebula", "temp":10000,  "lum":400000,  "dist":1344,   "mass":2000},
    {"name":"Helix Nebula",  "type":"nebula", "temp":120000, "lum":300,     "dist":650,    "mass":0.6},
    {"name":"Crab Nebula",   "type":"nebula", "temp":11000,  "lum":100000,  "dist":6500,   "mass":10},
    {"name":"Ring Nebula",   "type":"nebula", "temp":120000, "lum":200,     "dist":2300,   "mass":1.1},
    {"name":"Eagle Nebula",  "type":"nebula", "temp":30000,  "lum":300000,  "dist":7000,   "mass":5000},
    {"name":"Lagoon Nebula", "type":"nebula", "temp":8500,   "lum":280000,  "dist":4100,   "mass":500},
    {"name":"Rosette Nebula","type":"nebula", "temp":35000,  "lum":500000,  "dist":5200,   "mass":10000},
    {"name":"Pillars Creat", "type":"nebula", "temp":8000,   "lum":200000,  "dist":7000,   "mass":900},
    {"name":"Andromeda",     "type":"galaxy", "temp":5000,   "lum":2.6e10,  "dist":2537000,"mass":1.5e12},
    {"name":"Whirlpool",     "type":"galaxy", "temp":7000,   "lum":2.5e10,  "dist":23000000,"mass":1.6e11},
    {"name":"Sombrero",      "type":"galaxy", "temp":5500,   "lum":8e10,    "dist":28000000,"mass":8e11},
    {"name":"Vela Pulsar",   "type":"remnant","temp":1000000,"lum":11000,   "dist":1000,   "mass":1.86},
    {"name":"Crab Pulsar",   "type":"remnant","temp":2000000,"lum":200000,  "dist":6500,   "mass":1.4},
    {"name":"Cassiopeia A",  "type":"remnant","temp":20000,  "lum":10000,   "dist":11000,  "mass":5},
]

SR = 44100; INV_SR = 1.0/SR; TAU = math.tau; _PI = math.pi
NYQUIST = SR*0.5; CHUNK = SR*10
_sin=math.sin; _cos=math.cos; _exp=math.exp; _tanh=math.tanh
_sqrt=math.sqrt; _rand=random.random; _gauss=random.gauss; _uniform=random.uniform

_SIN_N=4096
_SIN_T=[math.sin(i*TAU/_SIN_N) for i in range(_SIN_N)]

def fast_sin(phase):
    p=(phase%TAU)*(_SIN_N/TAU); i=int(p)&(_SIN_N-1); f=p-int(p)
    return _SIN_T[i]+(_SIN_T[(i+1)&(_SIN_N-1)]-_SIN_T[i])*f

QUALITY={
    "mobile":  {"max_voices":4, "reverb_combs":4,"max_chimes":6, "bytebeat_sr":4000,"label":"Mobile"},
    "balanced":{"max_voices":12,"reverb_combs":6,"max_chimes":10,"bytebeat_sr":8000,"label":"Balanced"},
    "studio":  {"max_voices":32,"reverb_combs":8,"max_chimes":12,"bytebeat_sr":8000,"label":"Studio"},
}
_Q=dict(QUALITY["balanced"])

def set_quality(name): global _Q; _Q=dict(QUALITY.get(name,QUALITY["balanced"]))
def clamp(x,lo=-1.0,hi=1.0): return lo if x<lo else(hi if x>hi else x)
def soft_clip(x,drive=1.10): d=_tanh(drive); return _tanh(x*drive)/d if d else x
def lerp(a,b,t): return a+(b-a)*t
def mtof(note): return 440.0*(2.0**((note-69.0)/12.0))
def humanize(t,amt=0.004): return t+_gauss(0.0,amt)

class DCBlocker:
    __slots__=("xm1","ym1","R")
    def __init__(self,R=0.995): self.xm1=0.0;self.ym1=0.0;self.R=R
    def process(self,x):
        y=x-self.xm1+self.R*self.ym1; self.xm1=x;self.ym1=y; return y

class SVF:
    __slots__=("lp","bp","hp","_f","_q")
    def __init__(self,cutoff=1000.0,res=0.0):
        self.lp=self.bp=self.hp=0.0;self._f=0.0;self._q=1.0;self.set(cutoff,res)
    def set(self,cutoff,res=None):
        cutoff=min(max(20.0,cutoff),NYQUIST*0.95)
        self._f=2.0*_sin(_PI*cutoff*INV_SR)
        if res is not None: self._q=1.0-min(max(0.0,res),0.97)
    def lp_process(self,x):
        hp=x-self.lp-self._q*self.bp;self.bp+=self._f*hp;self.lp+=self._f*self.bp;self.hp=hp;return self.lp
    def hp_process(self,x): self.lp_process(x);return self.hp
    def bp_process(self,x): self.lp_process(x);return self.bp

class OnePole:
    __slots__=("a","z")
    def __init__(self,cutoff=1000.0): self.z=0.0;self.set(cutoff)
    def set(self,cutoff): self.a=1.0-_exp(-TAU*min(max(cutoff,1.0),NYQUIST*0.99)*INV_SR)
    def lp(self,x): self.z+=self.a*(x-self.z);return self.z
    def hp(self,x): return x-self.lp(x)

class ADSR:
    __slots__=("a","d","s","r")
    def __init__(self,a=0.01,d=0.1,s=0.7,r=0.3):
        self.a=max(a,0.001);self.d=max(d,0.001);self.s=s;self.r=max(r,0.001)
    def get(self,t,dur):
        if t<0: return 0.0
        if t<self.a: return t/self.a
        if t<self.a+self.d: return 1.0-(1.0-self.s)*((t-self.a)/self.d)
        if t<dur: return self.s
        rt=t-dur
        if rt<self.r: return self.s*(1.0-rt/self.r)
        return 0.0

def osc_tri(phase):
    p=(phase%TAU)/TAU; return 4.0*abs(p-0.5)-1.0
def osc_pulse(phase,pw=0.5):
    return 1.0 if ((phase%TAU)/TAU)<pw else -1.0
def osc_saw_blep(phase,freq):
    t=(phase%TAU)/TAU;v=2.0*t-1.0;dt=freq*INV_SR
    if dt<=0: return v
    if t<dt: x=t/dt;v-=x+x-x*x-1.0
    elif t>1.0-dt: x=(t-1.0)/dt;v-=x+x+x*x+1.0
    return v
def osc_square_blep(phase,freq):
    t=(phase%TAU)/TAU;v=1.0 if t<0.5 else -1.0;dt=freq*INV_SR
    if dt<=0: return v
    if t<dt: x=t/dt;v+=x+x-x*x-1.0
    elif t>1.0-dt: x=(t-1.0)/dt;v-=x+x+x*x+1.0
    t2=(t+0.5)%1.0
    if t2<dt: x=t2/dt;v-=x+x-x*x-1.0
    elif t2>1.0-dt: x=(t2-1.0)/dt;v+=x+x+x*x+1.0
    return v

class SuperSaw:
    __slots__=("phases","incs","mix","freq")
    def __init__(self,freq,detune=0.30,mix=0.82):
        spreads=[-0.03,-0.02,-0.01,0.0,0.01,0.02,0.03]
        self.phases=[_uniform(0,TAU) for _ in range(7)]
        self.incs=[TAU*freq*(1.0+detune*s)*INV_SR for s in spreads]
        self.mix=mix/7.0;self.freq=freq
    def sample(self,t=0.0,env=1.0):
        v=0.0;ph=self.phases;inc=self.incs;fr=self.freq
        for i in range(7): ph[i]+=inc[i];v+=osc_saw_blep(ph[i],fr)
        return v*self.mix

class FMSynth:
    __slots__=("car_inc","mod_inc","depth","fb","pc","pm","prev")
    def __init__(self,freq,ratio=2.0,depth=1.4,feedback=0.12):
        self.car_inc=TAU*freq*INV_SR;self.mod_inc=TAU*freq*ratio*INV_SR
        self.depth=depth;self.fb=feedback;self.pc=0.0;self.pm=0.0;self.prev=0.0
    def sample(self,t=0.0,env=1.0):
        mod=fast_sin(self.pm+self.prev*self.fb)*self.depth;self.pm+=self.mod_inc
        out=fast_sin(self.pc+mod);self.pc+=self.car_inc;self.prev=out;return out

class SubSynth:
    __slots__=("phase","inc","wave","filt","env_depth","base_cut","freq")
    def __init__(self,freq,wave="saw",cutoff=2000.0,res=0.22,env_depth=2500.0):
        self.phase=_uniform(0,TAU);self.inc=TAU*freq*INV_SR;self.wave=wave
        self.filt=SVF(cutoff,res);self.env_depth=env_depth;self.base_cut=cutoff;self.freq=freq
    def sample(self,t=0.0,env=1.0):
        self.phase+=self.inc;w=self.wave
        if w=="saw": v=osc_saw_blep(self.phase,self.freq)
        elif w=="square": v=osc_square_blep(self.phase,self.freq)
        elif w=="tri": v=osc_tri(self.phase)
        elif w=="pulse": v=osc_pulse(self.phase,0.35+0.15*fast_sin(TAU*0.45*t))
        else: v=fast_sin(self.phase)
        self.filt.set(min(self.base_cut+self.env_depth*env,NYQUIST*0.95))
        return self.filt.lp_process(v)

class KarplusStrong:
    __slots__=("buf","idx","decay","bright")
    def __init__(self,freq,decay=0.996,brightness=0.55):
        period=max(int(SR/max(freq,24.0)),2)
        self.buf=[_uniform(-1,1) for _ in range(period)]
        self.idx=0;self.decay=decay;self.bright=1.0-brightness*0.7
    def sample(self,t=0.0,env=1.0):
        buf=self.buf;L=len(buf);i=self.idx%L;j=(i+1)%L
        out=buf[i];buf[i]=(buf[i]+buf[j])*0.5*self.bright*self.decay
        self.idx+=1;return out

class Pad:
    __slots__=("phases","incs","lfo","lfo_inc","n")
    def __init__(self,notes,detune=0.005):
        phases=[];incs=[]
        for n in notes:
            f=mtof(n)
            for d in (-detune,0.0,detune):
                phases.append(_uniform(0,TAU));incs.append(TAU*f*(1.0+d)*INV_SR)
        self.phases=phases;self.incs=incs
        self.lfo=_uniform(0,TAU);self.lfo_inc=TAU*0.16*INV_SR;self.n=len(phases)
    def sample(self,t=0.0,env=1.0):
        self.lfo+=self.lfo_inc;mod=0.7+0.3*(0.5+0.5*fast_sin(self.lfo))
        v=0.0;ph=self.phases;inc=self.incs
        for i in range(self.n): ph[i]+=inc[i];v+=fast_sin(ph[i])
        return (v/self.n)*mod if self.n else 0.0

class Organ:
    __slots__=("phase","inc")
    def __init__(self,freq): self.phase=0.0;self.inc=TAU*freq*INV_SR
    def sample(self,t=0.0,env=1.0):
        self.phase+=self.inc;p=self.phase
        return 0.60*fast_sin(p)+0.22*fast_sin(p*2)+0.10*fast_sin(p*3)+0.06*fast_sin(p*4)

class FluteSynth:
    __slots__=("phase","inc","vib_phase","vib_inc","breath_lp","freq")
    def __init__(self,freq):
        self.phase=_uniform(0,TAU);self.inc=TAU*freq*INV_SR
        self.vib_phase=0.0;self.vib_inc=TAU*5.5*INV_SR
        self.breath_lp=OnePole(4000.0);self.freq=freq
    def sample(self,t=0.0,env=1.0):
        self.vib_phase+=self.vib_inc;vib=fast_sin(self.vib_phase)*0.012*min(t*4,1.0)
        self.phase+=self.inc*(1.0+vib);breath=self.breath_lp.lp(_uniform(-1,1))*0.08
        return fast_sin(self.phase)*0.85+breath

class Kick808:
    __slots__=("punch","decay","tone")
    def __init__(self,punch=1.0,decay=0.40,tone=50.0): self.punch=punch;self.decay=decay;self.tone=tone
    def sample(self,t=0.0,env=1.0):
        if t<0: return 0.0
        pitch=self.tone+190.0*self.punch*_exp(-30.0*t); amp=_exp(-t/max(self.decay,0.001))
        click=_exp(-150.0*t)*0.40*self.punch
        return soft_clip((_sin(TAU*pitch*t)*amp+click)*0.95,1.25)

class Snare909:
    __slots__=("tone","noise_amt","decay","hpf")
    def __init__(self,tone=195.0,noise_amt=0.62,decay=0.18):
        self.tone=tone;self.noise_amt=noise_amt;self.decay=decay;self.hpf=SVF(2200.0,0.04)
    def sample(self,t=0.0,env=1.0):
        if t<0: return 0.0
        te=_exp(-18.0*t);ne=_exp(-t/max(self.decay,0.001))
        tonal=_sin(TAU*self.tone*t)*te*(1.0-self.noise_amt)
        noise=self.hpf.hp_process(_uniform(-1,1))*ne*self.noise_amt
        return soft_clip((tonal+noise)*0.82,1.35)

class HiHat:
    __slots__=("decay","hpf","phases","incs")
    RATIOS=(1.0,1.342,1.2312,1.6532,1.9523,2.1523)
    def __init__(self,open_hat=False,decay=0.045):
        self.decay=0.22 if open_hat else decay;self.hpf=SVF(7800.0,0.05)
        self.phases=[0.0]*6;self.incs=[TAU*420.0*r*INV_SR for r in self.RATIOS]
    def sample(self,t=0.0,env=1.0):
        if t<0: return 0.0
        amp=_exp(-t/max(self.decay,0.001));v=0.0
        for i in range(6): self.phases[i]+=self.incs[i];v+=1.0 if(self.phases[i]%TAU)<_PI else -1.0
        return self.hpf.hp_process(v/6.0)*amp*0.48

class Clap:
    __slots__=("decay","bpf")
    def __init__(self,decay=0.14): self.decay=decay;self.bpf=SVF(1600.0,0.55)
    def sample(self,t=0.0,env=1.0):
        if t<0: return 0.0
        amp=_exp(-t/max(self.decay,0.001));burst=0.0
        for off in(0.0,0.010,0.021,0.031):
            bt=t-off
            if bt>=0: burst+=_exp(-90.0*bt)*_uniform(-1,1)
        return self.bpf.bp_process(burst*amp*0.45)

class PinkNoise:
    __slots__=("b",)
    def __init__(self): self.b=[0.0]*6
    def sample(self):
        b=self.b;w=_uniform(-1,1)
        b[0]=0.99886*b[0]+w*0.0555179;b[1]=0.99332*b[1]+w*0.0750759
        b[2]=0.96900*b[2]+w*0.1538520;b[3]=0.86650*b[3]+w*0.3104856
        b[4]=0.55000*b[4]+w*0.5329522;b[5]=-0.7616*b[5]-w*0.0168980
        return(b[0]+b[1]+b[2]+b[3]+b[4]+b[5]+w*0.5362)*0.11

class BrownNoise:
    __slots__=("z",)
    def __init__(self): self.z=0.0
    def sample(self): self.z=0.98*self.z+0.03*_uniform(-1,1);return clamp(self.z)

class Wind:
    __slots__=("pink","pink2","lfo_b","lfo_g","lfo_s","inc_b","inc_g","inc_s","lp1","hp","bp","intensity")
    def __init__(self,intensity=0.4):
        self.pink=PinkNoise();self.pink2=PinkNoise()
        self.lfo_b=_uniform(0,TAU);self.lfo_g=_uniform(0,TAU);self.lfo_s=_uniform(0,TAU)
        self.inc_b=TAU*0.12*INV_SR;self.inc_g=TAU*0.025*INV_SR;self.inc_s=TAU*0.004*INV_SR
        self.lp1=OnePole(1200.0);self.hp=OnePole(60.0);self.bp=SVF(800.0,0.15)
        self.intensity=intensity
    def sample_stereo(self,t=0.0):
        self.lfo_b+=self.inc_b;self.lfo_g+=self.inc_g;self.lfo_s+=self.inc_s
        breath=0.5+0.5*fast_sin(self.lfo_b);gust=max(0,fast_sin(self.lfo_g)**3)
        mod=0.15+0.45*breath+0.35*gust
        v1=self.pink.sample();v2=self.pink2.sample()
        cut=600.0+1400.0*gust+400.0*breath
        self.lp1.set(cut);self.bp.set(cut*0.7,0.12+0.15*gust)
        l=self.hp.hp(self.lp1.lp(v1)+self.bp.bp_process(v1)*0.3*gust)
        r=self.hp.hp(self.lp1.lp(v2)+self.bp.bp_process(v2)*0.25*gust)
        s=mod*self.intensity;return l*s,r*s*0.93

class Rain:
    __slots__=("bed","small_lp","med_lp","heavy_lp","hp","intensity")
    def __init__(self,intensity=0.45):
        self.bed=PinkNoise();self.small_lp=OnePole(8000.0)
        self.med_lp=OnePole(3500.0);self.heavy_lp=OnePole(1800.0)
        self.hp=OnePole(200.0);self.intensity=intensity
    def sample_stereo(self,t=0.0):
        inten=self.intensity
        bed=self.hp.hp(self.bed.sample())*0.08*inten
        small=self.small_lp.lp(_uniform(-1,1))*_uniform(0.02,0.06)*inten if _rand()<inten*0.06 else 0.0
        med=self.med_lp.lp(_uniform(-1,1))*_uniform(0.08,0.18)*inten if _rand()<inten*0.012 else 0.0
        heavy=self.heavy_lp.lp(_uniform(-1,1))*_uniform(0.15,0.30)*inten if _rand()<inten*0.003 else 0.0
        mono=bed+small+med+heavy
        pan=_uniform(-0.4,0.4);pr=(pan+1.0)*_PI*0.25
        return mono*_cos(pr),mono*_sin(pr)

class Ocean:
    __slots__=("pink1","pink2","pink3","foam","lfo1","lfo2","lfo3","inc1","inc2","inc3",
               "lp1","lp2","lp3","hp","foam_lp","crash_t","crash_amp","crash_dur","intensity")
    def __init__(self,intensity=0.5):
        self.pink1=PinkNoise();self.pink2=PinkNoise()
        self.pink3=PinkNoise();self.foam=PinkNoise()
        self.lfo1=_uniform(0,TAU);self.lfo2=_uniform(0,TAU);self.lfo3=_uniform(0,TAU)
        self.inc1=TAU*0.045*INV_SR;self.inc2=TAU*0.11*INV_SR;self.inc3=TAU*0.28*INV_SR
        self.lp1=OnePole(400.0);self.lp2=OnePole(900.0);self.lp3=OnePole(2200.0)
        self.hp=OnePole(25.0);self.foam_lp=OnePole(6000.0)
        self.crash_t=-1.0;self.crash_amp=0.0;self.crash_dur=0.0;self.intensity=intensity
    def sample_stereo(self,t=0.0):
        self.lfo1+=self.inc1;self.lfo2+=self.inc2;self.lfo3+=self.inc3
        swell=max(0,fast_sin(self.lfo1))**1.5;wave2=0.5+0.5*fast_sin(self.lfo2)
        ripple=0.5+0.5*fast_sin(self.lfo3)
        v1=self.lp1.lp(self.pink1.sample())*swell*0.55
        v2=self.lp2.lp(self.pink2.sample())*wave2*0.28
        v3=self.lp3.lp(self.pink3.sample())*ripple*0.12
        base=self.hp.hp(v1+v2+v3)
        if self.crash_t<0 and swell>0.85 and _rand()<0.02:
            self.crash_t=0.0;self.crash_amp=_uniform(0.3,0.7);self.crash_dur=_uniform(1.5,3.5)
        crash=0.0
        if self.crash_t>=0:
            self.crash_t+=INV_SR
            if self.crash_t<self.crash_dur:
                ce=_exp(-self.crash_t*2.0/self.crash_dur)
                crash=self.foam_lp.lp(self.foam.sample())*ce*self.crash_amp*0.4
            else: self.crash_t=-1.0
        mono=(base+crash)*self.intensity*0.75
        sp=0.5+0.15*fast_sin(self.lfo1*0.3)
        return mono*sp,mono*(1.0-sp)

class WaterStream:
    __slots__=("pink","hpf","lpf","bubble_lp","intensity")
    def __init__(self,intensity=0.35):
        self.pink=PinkNoise();self.hpf=OnePole(500.0);self.lpf=OnePole(4500.0)
        self.bubble_lp=OnePole(2800.0);self.intensity=intensity
    def sample_stereo(self,t=0.0):
        v=self.hpf.hp(self.lpf.lp(self.pink.sample()))*0.18
        bub=self.bubble_lp.lp(_uniform(-1,1))*_uniform(0.1,0.35) if _rand()<self.intensity*0.008 else 0.0
        splash=_uniform(0.15,0.4) if _rand()<self.intensity*0.0015 else 0.0
        mono=(v+bub*0.3+splash*0.15)*self.intensity
        pan=_uniform(-0.5,0.5);pr=(pan+1)*_PI*0.25
        return mono*_cos(pr),mono*_sin(pr)

class Fire:
    __slots__=("roar_lp","crackle_lp","crackle_hp","pop_hp","ember_bp","lfo","lfo_inc","intensity")
    def __init__(self,intensity=0.35):
        self.roar_lp=OnePole(250.0);self.crackle_lp=OnePole(2500.0)
        self.crackle_hp=OnePole(400.0);self.pop_hp=OnePole(1500.0)
        self.ember_bp=SVF(4500.0,0.3);self.lfo=_uniform(0,TAU);self.lfo_inc=TAU*0.07*INV_SR
        self.intensity=intensity
    def sample_stereo(self,t=0.0):
        self.lfo+=self.lfo_inc;breath=0.6+0.4*(0.5+0.5*fast_sin(self.lfo))
        roar=self.roar_lp.lp(_uniform(-1,1))*0.12*breath
        crack=self.crackle_hp.hp(self.crackle_lp.lp(_uniform(-1,1)))*_uniform(0.2,0.5) if _rand()<self.intensity*0.015 else 0.0
        pop=self.pop_hp.hp(_uniform(-1,1))*_uniform(0.3,0.7) if _rand()<self.intensity*0.004 else 0.0
        mono=(roar+crack*0.25+pop*0.15)*self.intensity
        pan=_uniform(-0.3,0.3);pr=(pan+1)*_PI*0.25
        return mono*_cos(pr),mono*_sin(pr)

class Thunder:
    __slots__=("active","stage","stage_t","amp","distance","lp1","lp2","lp3","hp","intensity","cooldown")
    def __init__(self,intensity=0.5):
        self.active=False;self.stage=0;self.stage_t=0.0;self.amp=0.0;self.distance=0.5
        self.lp1=OnePole(80.0);self.lp2=OnePole(250.0);self.lp3=OnePole(500.0)
        self.hp=OnePole(20.0);self.intensity=intensity;self.cooldown=0.0
    def sample_stereo(self,t=0.0):
        if self.cooldown>0: self.cooldown-=INV_SR
        if not self.active:
            if self.cooldown<=0 and _rand()<self.intensity*0.00003:
                self.active=True;self.stage=0;self.stage_t=0.0
                self.amp=_uniform(0.5,1.0);self.distance=_uniform(0.2,1.0)
                self.cooldown=_uniform(5.0,15.0)
                self.lp1.set(60+80*(1-self.distance));self.lp2.set(150+200*(1-self.distance))
            return 0.0,0.0
        self.stage_t+=INV_SR;v=0.0
        if self.stage==0:
            if self.stage_t<0.05*(1+self.distance):
                v=self.lp3.lp(_uniform(-1,1))*_exp(-self.stage_t*30)*self.amp*0.6
            else: self.stage=1;self.stage_t=0.0
        elif self.stage==1:
            dur=1.5+1.5*self.distance
            if self.stage_t<dur:
                env=_exp(-self.stage_t*1.5/dur)
                v=(self.lp1.lp(_uniform(-1,1))*0.5+self.lp2.lp(_uniform(-1,1))*0.35*_exp(-self.stage_t*3))*env*self.amp
            else: self.stage=2;self.stage_t=0.0
        elif self.stage==2:
            tail=2.0+4.0*self.distance
            if self.stage_t<tail: v=self.lp1.lp(_uniform(-1,1))*_exp(-self.stage_t*2.0/tail)*self.amp*0.25
            else: self.active=False;return 0.0,0.0
        v=self.hp.hp(v)*self.intensity*0.65
        w=0.4*(1-self.distance)+0.05;return v*(0.5+w),v*(0.5-w)

class SingingBowl:
    __slots__=("partials","decay","t","next_strike","amp","intensity")
    def __init__(self,intensity=0.45):
        self.partials=[];self.decay=0.0;self.t=0.0
        self.next_strike=0.0;self.amp=0.0;self.intensity=intensity;self._new_strike()
    def _new_strike(self):
        base=random.choice([180.0,220.0,260.0,310.0,370.0,440.0])
        ratios=[1.0,2.71,4.77,7.03,9.43];beats=[0.0,0.7,1.2,0.5,0.9]
        self.partials=[]
        for r,b in zip(ratios,beats):
            f=base*r
            if f<NYQUIST*0.9: self.partials.append([_uniform(0,TAU),TAU*f*INV_SR,TAU*b*INV_SR,1.0/(r*r*0.3+1.0)])
        self.decay=_uniform(5.0,12.0);self.t=0.0;self.amp=_uniform(0.5,1.0);self.next_strike=_uniform(6.0,18.0)
    def sample(self,t_sec=0.0):
        self.t+=INV_SR
        if self.t>self.next_strike: self._new_strike()
        env=_exp(-self.t*2.0/max(self.decay,0.01))
        if env<0.001: return 0.0
        v=0.0
        for p in self.partials:
            p[0]+=p[1];v+=fast_sin(p[0])*p[3]*(0.85+0.15*fast_sin(p[0]*0.0001+p[2]*self.t*SR))
        return v*env*self.amp*self.intensity*0.16

class WindChimes:
    __slots__=("density","active_chimes","intensity")
    def __init__(self,density=0.3,intensity=0.30):
        self.density=density;self.active_chimes=[];self.intensity=intensity
    def sample_stereo(self,t=0.0):
        maxc=_Q["max_chimes"]
        if len(self.active_chimes)<maxc and _rand()<self.density*0.0003:
            freq=random.choice([1200,1580,1890,2100,2640,3150,3520])
            self.active_chimes.append([0.0,float(freq),_uniform(3,8),0.0,_uniform(0.3,1.0),_uniform(-0.5,0.5)])
        l=0.0;r=0.0;alive=[]
        for ch in self.active_chimes:
            ch[0]+=TAU*ch[1]*INV_SR;ch[3]+=INV_SR;env=_exp(-ch[3]/ch[2])
            if env<0.001: continue
            alive.append(ch)
            tone=fast_sin(ch[0])*0.6+fast_sin(ch[0]*2.76)*0.25+fast_sin(ch[0]*5.4)*0.12
            v=tone*env*ch[4]*self.intensity*0.12;pr=(ch[5]+1)*_PI*0.25
            l+=v*_cos(pr);r+=v*_sin(pr)
        self.active_chimes=alive;return l,r

class BytebeatAmbient:
    __slots__=("t","sr_scale","lp1","lp2","hp","feedback","mode","intensity","drift_phase","drift_inc")
    def __init__(self,intensity=0.35,mode=0):
        self.t=0;self.sr_scale=max(1,int(SR/max(_Q["bytebeat_sr"],1000)))
        self.lp1=OnePole(1800.0);self.lp2=OnePole(900.0);self.hp=OnePole(40.0)
        self.feedback=0.0;self.mode=mode%5;self.intensity=intensity
        self.drift_phase=_uniform(0,TAU);self.drift_inc=TAU*0.013*INV_SR
    def _formula(self,x):
        m=self.mode
        if m==0: y=((x>>7)|(x>>6)|(x*3))&255;z=((x*((y&31)+1))>>8)&255;return(y^z)&255
        elif m==1: y=(x*((x>>9)|(x>>13)))&255;z=((x>>5)|(x>>8))&255;return(y^z)&255
        elif m==2: y=((x*5&(x>>7))|(x*3&(x>>10)))&255;z=((x>>4)^(x>>6)^(x>>9))&255;return(y+z)&255
        elif m==3: y=((x>>8)|(x>>5)|(x*9))&255;z=((x*((x>>11)&15 or 1))>>7)&255;return(y^z)&255
        else: y=((x|(x>>11))*(x&(x>>3)))&255;z=((x>>6)*(x>>2)&(x>>8))&255;return(y^z)&255
    def sample(self,t_sec=0.0):
        self.drift_phase+=self.drift_inc;drift=0.98+0.04*(0.5+0.5*fast_sin(self.drift_phase))
        x=int(self.t/self.sr_scale*drift);raw=self._formula(x)
        fb=int((self.feedback*127)+128)&255;raw=(raw^(fb>>1))&255
        v=(raw-128.0)/128.0;v=self.lp1.lp(v);v=self.lp2.lp(v);v=v-self.hp.lp(v)*0.15
        self.feedback=0.985*self.feedback+0.015*v;self.t+=1;return v*self.intensity

ENTITY_PROFILES={
    "glacier":      {"coherence":0.99,"collapse":0.0005,"entangle":0.95,"pulse":0.005,"centroid":30},
    "mountain":     {"coherence":0.99,"collapse":0.001, "entangle":0.90,"pulse":0.01, "centroid":60},
    "desert_dune":  {"coherence":0.85,"collapse":0.02,  "entangle":0.40,"pulse":0.05, "centroid":150},
    "canyon":       {"coherence":0.97,"collapse":0.003, "entangle":0.80,"pulse":0.02, "centroid":80},
    "nebula":       {"coherence":0.60,"collapse":0.12,  "entangle":0.85,"pulse":2.0,  "centroid":3500},
    "pulsar":       {"coherence":0.55,"collapse":0.20,  "entangle":0.25,"pulse":150.0,"centroid":8000},
    "stellar_wind": {"coherence":0.70,"collapse":0.08,  "entangle":0.50,"pulse":0.8,  "centroid":2200},
    "dark_matter":  {"coherence":0.99,"collapse":0.0001,"entangle":0.99,"pulse":0.001,"centroid":10},
    "cosmic_void":  {"coherence":1.00,"collapse":0.0001,"entangle":1.00,"pulse":0.0005,"centroid":5},
}

class CosmicEntity:
    __slots__=("profile","lp","hp","bp","pulse_phase","pulse_inc","coherence_lfo","coherence_inc",
               "collapse_t","noise","intensity","entangle_buf","eb_idx")
    def __init__(self,profile_name="mountain",intensity=0.35):
        p=ENTITY_PROFILES.get(profile_name,ENTITY_PROFILES["mountain"])
        self.profile=p;centroid=p["centroid"]
        self.lp=OnePole(centroid*2);self.hp=OnePole(max(centroid*0.1,10));self.bp=SVF(centroid,0.3)
        self.pulse_phase=0.0;self.pulse_inc=TAU*p["pulse"]*INV_SR
        self.coherence_lfo=_uniform(0,TAU);self.coherence_inc=TAU*0.07*INV_SR
        self.collapse_t=-1.0;self.noise=PinkNoise();self.intensity=intensity
        self.entangle_buf=[0.0]*256;self.eb_idx=0
    def sample_stereo(self,t=0.0):
        p=self.profile;self.coherence_lfo+=self.coherence_inc
        coh=p["coherence"]*(0.8+0.2*fast_sin(self.coherence_lfo))
        if self.collapse_t<0 and _rand()<p["collapse"]*INV_SR*0.1: self.collapse_t=0.0
        collapse_v=0.0
        if self.collapse_t>=0:
            self.collapse_t+=INV_SR;dur=0.02+p["collapse"]*0.5
            if self.collapse_t<dur: collapse_v=_uniform(-1,1)*_exp(-self.collapse_t/dur*3)
            else: self.collapse_t=-1.0
        self.pulse_phase+=self.pulse_inc;pulse=fast_sin(self.pulse_phase)*coh*0.4
        raw=self.noise.sample()
        base_l=self.bp.bp_process(self.lp.lp(raw))*0.5+pulse*0.5+collapse_v*0.3
        ent=p["entangle"];eb=self.entangle_buf;idx=self.eb_idx
        eb[idx%256]=base_l;delayed=eb[(idx-int(44*ent))%256]
        base_r=lerp(self.hp.hp(self.noise.sample())*0.5+pulse*0.5,delayed,ent)+collapse_v*0.25
        self.eb_idx+=1;scale=self.intensity*(0.8+0.2*coh)
        return base_l*scale,base_r*scale

class FreeflowMode:
    __slots__=("freeflow","seed","rng","phase_time","phase_dur","current","target","pink","lp","hp",
               "lfo_a","lfo_b","lfo_c","inc_a","inc_b","inc_c","pad","pad_t","pad_dur",
               "entity","entity_profile","bass_phase","bass_inc","dc_l","dc_r")
    def __init__(self,freeflow=0.5,seed=0):
        self.freeflow=freeflow;self.rng=random.Random(seed);self.pink=PinkNoise()
        self.lp=OnePole(800.0);self.hp=OnePole(60.0)
        self.lfo_a=_uniform(0,TAU);self.lfo_b=_uniform(0,TAU);self.lfo_c=_uniform(0,TAU)
        rng=self.rng
        self.inc_a=TAU*rng.uniform(0.05,0.25)*INV_SR
        self.inc_b=TAU*rng.uniform(0.02,0.12)*INV_SR
        self.inc_c=TAU*rng.uniform(0.01,0.06)*INV_SR
        self.phase_time=0.0;self.phase_dur=rng.uniform(8.0,20.0+freeflow*40)
        self.current=self._random_state();self.target=self._random_state()
        self.pad=None;self.pad_t=0.0;self.pad_dur=0.0
        ep=random.choice(list(ENTITY_PROFILES.keys()))
        self.entity=CosmicEntity(ep,intensity=0.12);self.entity_profile=ep
        root=rng.choice([36,40,43,45,48])
        self.bass_phase=0.0;self.bass_inc=TAU*mtof(root-12)*INV_SR
        self.dc_l=DCBlocker();self.dc_r=DCBlocker()
    def _random_state(self):
        r=self.rng
        return{"noise_amt":r.uniform(0.0,0.4*self.freeflow),"tonal_amt":r.uniform(0.3,0.9),
               "bass_amt":r.uniform(0.0,0.35),"entity_amt":r.uniform(0.0,0.25*self.freeflow),
               "brightness":r.uniform(200,4000),"pad_notes":[r.randint(48,72) for _ in range(r.randint(2,4))]}
    def sample_stereo(self,t=0.0):
        self.phase_time+=INV_SR;alpha=min(self.phase_time/max(self.phase_dur,1.0),1.0)
        def interp(k):
            a=self.current[k];b=self.target[k]
            if isinstance(a,float): return lerp(a,b,alpha)
            return a
        noise_amt=interp("noise_amt");tonal_amt=interp("tonal_amt")
        bass_amt=interp("bass_amt");entity_amt=interp("entity_amt");brightness=interp("brightness")
        if alpha>=1.0:
            self.current=self.target;self.target=self._random_state()
            self.phase_time=0.0;self.phase_dur=self.rng.uniform(8.0,20.0+self.freeflow*40)
            ep=random.choice(list(ENTITY_PROFILES.keys()));self.entity=CosmicEntity(ep,intensity=0.12)
        self.lfo_a+=self.inc_a;self.lfo_b+=self.inc_b;self.lfo_c+=self.inc_c
        self.lp.set(brightness*(0.8+0.4*fast_sin(self.lfo_a)))
        noise_l=self.hp.hp(self.lp.lp(self.pink.sample()))*noise_amt
        self.pad_t+=INV_SR
        if self.pad is None or self.pad_t>self.pad_dur:
            notes=self.target["pad_notes"]
            self.pad=Pad(notes,detune=0.003+self.freeflow*0.008)
            self.pad_dur=self.rng.uniform(4.0,16.0);self.pad_t=0.0
        tonal=self.pad.sample(t)*tonal_amt*(0.5+0.5*fast_sin(self.lfo_b))
        self.bass_phase+=self.bass_inc
        bass=fast_sin(self.bass_phase)*bass_amt*0.5*(0.3+0.7*fast_sin(self.lfo_c))
        el,er=self.entity.sample_stereo(t)
        l=noise_l*0.7+tonal*0.5+bass+el*entity_amt
        r=noise_l*1.3+tonal*0.5+bass+er*entity_amt
        return self.dc_l.process(l),self.dc_r.process(r)

class Delay:
    __slots__=("bl","br","il","ir","fb","mix")
    def __init__(self,time_l=0.375,time_r=0.25,feedback=0.35,mix=0.25):
        self.bl=[0.0]*(int(SR*time_l)+2);self.br=[0.0]*(int(SR*time_r)+2)
        self.il=0;self.ir=0;self.fb=feedback;self.mix=mix
    def process(self,l,r):
        bl=self.bl;br=self.br;il=self.il%len(bl);ir=self.ir%len(br)
        dl=bl[il];dr=br[ir];bl[il]=l+dl*self.fb;br[ir]=r+dr*self.fb
        self.il+=1;self.ir+=1;return l+dl*self.mix,r+dr*self.mix

class Reverb:
    COMB_DELAYS_ALL=(0.02257,0.02391,0.02641,0.02743,0.02999,0.03119,0.03371,0.03571)
    AP_DELAYS=(0.0050,0.0017,0.00051)
    __slots__=("combs","ci","cfb","aps","ai","lps","damp","mix")
    def __init__(self,size=0.9,damp=0.45,mix=0.30):
        nc=_Q["reverb_combs"];cds=self.COMB_DELAYS_ALL[:nc]
        self.combs=[([0.0]*max(int(SR*d*size),2)) for d in cds]
        self.ci=[0]*nc;self.cfb=0.84
        self.aps=[([0.0]*max(int(SR*d),2)) for d in self.AP_DELAYS]
        self.ai=[0]*3;self.lps=[0.0]*nc;self.damp=damp;self.mix=mix
    def process(self,x):
        out=0.0
        for i,buf in enumerate(self.combs):
            idx=self.ci[i]%len(buf);val=buf[idx]
            self.lps[i]=val*(1.0-self.damp)+self.lps[i]*self.damp
            buf[idx]=x+self.lps[i]*self.cfb;self.ci[i]+=1;out+=val
        out/=len(self.combs)
        for i,buf in enumerate(self.aps):
            idx=self.ai[i]%len(buf);bv=buf[idx]
            buf[idx]=out+bv*0.5;self.ai[i]+=1;out=bv-out*0.5
        return x*(1.0-self.mix)+out*self.mix

class Chorus:
    __slots__=("buf","idx","ph1","ph2","inc1","inc2","depth","mix")
    def __init__(self,rate=1.1,depth=0.003,mix=0.28):
        self.buf=[0.0]*(int(SR*0.04)+2);self.idx=0
        self.ph1=0.0;self.ph2=_PI/3.0
        self.inc1=TAU*rate*INV_SR;self.inc2=TAU*rate*1.07*INV_SR
        self.depth=depth*SR;self.mix=mix
    def process(self,x):
        buf=self.buf;L=len(buf);idx=self.idx;buf[idx%L]=x;self.idx+=1
        self.ph1+=self.inc1;self.ph2+=self.inc2;m=self.mix
        def _tap(ph):
            off=self.depth*(1.0+fast_sin(ph))*0.5;ri=idx-int(off);f=off-int(off)
            a=buf[ri%L];b=buf[(ri-1)%L];return a+(b-a)*f
        return x*(1-m)+_tap(self.ph1)*m,x*(1-m)+_tap(self.ph2)*m

class VinylTexture:
    __slots__=("pink","rumble_lp","crackle")
    def __init__(self): self.pink=PinkNoise();self.rumble_lp=OnePole(70.0);self.crackle=0.0
    def sample(self):
        hiss=self.pink.sample()*0.010;rumble=self.rumble_lp.lp(_uniform(-1,1))*0.005
        crack=0.0
        if self.crackle>0.001: self.crackle*=0.88;crack=_uniform(-1,1)*self.crackle
        elif _rand()<0.00025: self.crackle=0.28
        return hiss+rumble+crack

class TapeProcessor:
    __slots__=("buf","idx","wow","flutter","wow_inc","flutter_inc","lp","dw","df")
    def __init__(self):
        self.buf=[0.0]*(int(SR*0.05)+2);self.idx=0
        self.wow=0.0;self.flutter=0.0;self.wow_inc=TAU*0.35*INV_SR;self.flutter_inc=TAU*6.0*INV_SR
        self.lp=OnePole(13500.0);self.dw=0.0011*SR;self.df=0.00035*SR
    def process(self,x):
        buf=self.buf;L=len(buf);buf[self.idx%L]=x;self.idx+=1
        self.wow+=self.wow_inc;self.flutter+=self.flutter_inc
        offset=self.dw*(1+fast_sin(self.wow))*0.5+self.df*(1+fast_sin(self.flutter))*0.5+2.0
        ri=self.idx-int(offset);frac=offset-int(offset)
        a=buf[ri%L];b=buf[(ri-1)%L];return soft_clip(self.lp.lp(a+(b-a)*frac),1.06)

SCALES={
    "major":[0,2,4,5,7,9,11],"minor":[0,2,3,5,7,8,10],"dorian":[0,2,3,5,7,9,10],
    "phrygian":[0,1,3,5,7,8,10],"lydian":[0,2,4,6,7,9,11],"mixolydian":[0,2,4,5,7,9,10],
    "pentatonic":[0,2,4,7,9],"minor_pentatonic":[0,3,5,7,10],"blues":[0,3,5,6,7,10],
    "whole_tone":[0,2,4,6,8,10],"harmonic_minor":[0,2,3,5,7,8,11],
}
CHORDS={"maj":[0,4,7],"min":[0,3,7],"maj7":[0,4,7,11],"min7":[0,3,7,10],
        "sus2":[0,2,7],"sus4":[0,5,7],"dim":[0,3,6],"aug":[0,4,8],"add9":[0,4,7,14]}
PROGRESSIONS={
    "ambient":    [(0,"sus2"),(4,"sus2"),(3,"maj7"),(0,"sus2")],
    "dark_ambient":[(0,"min"),(1,"min"),(4,"min"),(3,"maj")],
    "synthwave":  [(0,"min"),(3,"maj"),(4,"min"),(6,"maj")],
    "lo_fi":      [(0,"maj7"),(1,"min7"),(2,"min7"),(4,"maj7")],
    "sacred":     [(0,"sus2"),(5,"sus4"),(3,"maj7"),(0,"sus2")],
    "experimental":[(0,"sus2"),(1,"min"),(2,"min"),(4,"maj"),(0,"sus2")],
    "cosmic":     [(0,"sus2"),(4,"add9"),(3,"sus4"),(2,"min7"),(0,"sus2")],
    "drone":      [(0,"sus2")],
    "meditation": [(0,"sus2"),(4,"sus2")],
    "bellscape":  [(0,"sus2"),(4,"sus2"),(0,"sus2")],
}

def build_scale(root,scale_name,octaves=3):
    pat=SCALES.get(scale_name,SCALES["minor"])
    return[root+o*12+i for o in range(octaves) for i in pat if 0<=root+o*12+i<=127]

def build_chord(root,chord_name):
    return[root+i for i in CHORDS.get(chord_name,CHORDS["min"])]

def euclidean_rhythm(steps,pulses):
    if pulses<=0: return[False]*steps
    if pulses>=steps: return[True]*steps
    pattern=[];bucket=0
    for _ in range(steps):
        bucket+=pulses
        if bucket>=steps: pattern.append(True);bucket-=steps
        else: pattern.append(False)
    return pattern

MOOD_PRESETS={
    "peaceful":   (0.20,0.25,0.80,0.55,0.70,1.0, 0.20,0.70,0.20,0.40,0.50,0.20,0.60,0.30),
    "joyful":     (0.55,0.70,0.75,0.85,0.45,1.2, 0.65,0.50,0.50,0.25,0.75,0.45,0.30,0.65),
    "ethereal":   (0.18,0.30,0.50,0.60,0.90,1.5, 0.25,0.80,0.15,0.35,0.60,0.35,0.70,0.35),
    "melancholic":(0.25,0.35,0.65,0.35,0.65,0.9, 0.30,0.60,0.25,0.20,0.55,0.30,0.55,0.40),
    "mysterious": (0.22,0.40,0.40,0.35,0.80,1.4, 0.40,0.75,0.35,0.30,0.65,0.55,0.50,0.45),
    "intense":    (0.75,0.90,0.45,0.75,0.50,1.1, 0.85,0.35,0.80,0.15,0.85,0.65,0.10,0.85),
    "somber":     (0.15,0.20,0.55,0.20,0.75,0.85,0.15,0.65,0.10,0.25,0.40,0.15,0.70,0.30),
}

GENRES={
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

PURE_MODES={"pure_nature","pure_wind","pure_rain","pure_ocean","pure_water","pure_fire",
            "pure_storm","pure_white","pure_pink","pure_brown","pure_theta","pure_alpha",
            "pure_delta","pure_bowls","pure_chimes","pure_bytebeat"}
SPECIAL_MODES={"message","freeflow","entity"}
ALL_MODES=set(GENRES.keys())|PURE_MODES|SPECIAL_MODES

def cosmic_to_params(obj):
    temp=obj.get("temp",6000);lum=obj.get("lum",1.0)
    dist=obj.get("dist",100.0);mass=obj.get("mass",1.0)
    if temp<100:        mode="drone";       mood="somber"
    elif temp<4000:     mode="dark_ambient";mood="melancholic"
    elif temp<6000:     mode="ambient";     mood="peaceful"
    elif temp<7500:     mode="meditation";  mood="ethereal"
    elif temp<12000:    mode="bellscape";   mood="mysterious"
    elif temp<30000:    mode="cosmic";      mood="ethereal"
    else:               mode="experimental";mood="intense"
    log_lum=math.log10(max(lum,0.0001));density=max(0.05,min(0.90,(log_lum+4)/14.0))
    log_dist=math.log10(max(dist,1.0));width=max(0.6,min(2.0,0.6+log_dist*0.18))
    log_mass=math.log10(max(mass,0.001));bpm=int(max(38,min(120,62-log_mass*4)))
    flags=set()
    if temp<4000: flags.add("sparse")
    if temp>20000: flags.add("bright")
    if lum>10000: flags.add("wide")
    if dist>50000: flags.add("sparse")
    return{"mode":mode,"mood":mood,"bpm":bpm,"flags":flags,
           "_cosmic_source":obj.get("name","unknown"),
           "_cosmic_temp":temp,"_cosmic_lum":lum,"_cosmic_dist":dist}

def apply_cosmic_seed(params,object_name=None):
    from_list=COSMIC_OBJECTS
    obj=None
    if object_name:
        nl=object_name.lower()
        for o in from_list:
            if o["name"].lower()==nl or nl in o["name"].lower(): obj=o;break
    if obj is None: obj=random.choice(from_list)
    mapped=cosmic_to_params(obj)
    if not params.get("_mode_explicit"):
        params["mode"]=mapped["mode"];params["mood"]=mapped["mood"]
    if not params.get("bpm"): params["bpm"]=mapped["bpm"]
    existing_flags=set(params.get("flags",set()))
    params["flags"]=existing_flags|mapped["flags"]
    params["_cosmic_source"]=mapped["_cosmic_source"]
    return params

def apply_flags_to_genre(cfg,flags):
    cfg=dict(cfg)
    if "nodrums" in flags: cfg["drums"]=False
    if "drums"   in flags: cfg["drums"]=True
    if "warm"    in flags: cfg["bass_cut"]=int(cfg["bass_cut"]*0.7);cfg["reverb_damp"]=max(cfg["reverb_damp"],0.55)
    if "cold"    in flags: cfg["bass_cut"]=int(cfg["bass_cut"]*1.3);cfg["reverb_damp"]=min(cfg["reverb_damp"],0.30)
    if "bright"  in flags: cfg["lead_vol"]=min(0.8,cfg["lead_vol"]+0.05)
    if "sparse"  in flags: cfg["density"]*=0.55
    if "dense"   in flags: cfg["density"]=min(1,cfg["density"]*1.4)
    return cfg

def apply_mood(genre_cfg,mood_name):
    if mood_name not in MOOD_PRESETS: return genre_cfg
    cfg=dict(genre_cfg)
    (density,energy,warmth,brightness,wetness,width,motion,organic,pulse,nature,inst,rand_,sparsity,intensity)=MOOD_PRESETS[mood_name]
    cfg["density"]=lerp(cfg.get("density",0.3),density,0.6)
    cfg["pad_vol"]=lerp(cfg.get("pad_vol",0.5),intensity,0.4)
    cfg["reverb_mix"]=lerp(cfg.get("reverb_mix",0.4),wetness*0.8,0.5)
    cfg["reverb_damp"]=lerp(cfg.get("reverb_damp",0.5),1.0-warmth,0.5)
    return cfg

def energy_curve(t,total_dur):
    p=t/max(total_dur,1.0)
    if p<0.08: return(p/0.08)*0.30
    if p<0.25: return 0.30+((p-0.08)/0.17)*0.70
    if p<0.70: return 1.0
    if p<0.80: return 1.0-((p-0.70)/0.10)*0.40
    if p<0.90: return 0.60+((p-0.80)/0.10)*0.40
    return max(0.0,1.0-(p-0.90)/0.10)

class Event:
    __slots__=("time","duration","engine","vol","pan","env","is_sub","is_drum")
    def __init__(self,time,duration,engine,vol=0.5,pan=0.0,env=None,is_sub=False,is_drum=False):
        self.time=time;self.duration=duration;self.engine=engine
        self.vol=vol;self.pan=pan;self.env=env or ADSR(0.01,0.1,0.7,0.3)
        self.is_sub=is_sub;self.is_drum=is_drum

def generate_music_events(mode,rng,bpm=None,root=None,scale_name=None,duration=None,flags=None,mood=None):
    flags=flags or set()
    genre=apply_flags_to_genre(GENRES.get(mode,GENRES["ambient"]),flags)
    if mood: genre=apply_mood(genre,mood)
    bpm=bpm or rng.randint(*genre["bpm"]);beat=60.0/bpm;bar=beat*4
    root=root if root is not None else genre["key"]
    scale_name=scale_name or genre["scale"]
    duration=duration or rng.randint(*genre["duration"])
    total_bars=max(1,int(duration/bar))
    scale=build_scale(root,scale_name,3);bass_scale=build_scale(root+genre["bass_oct"]*12,scale_name,2)
    prog=PROGRESSIONS.get(genre["prog"],PROGRESSIONS["ambient"])
    events=[];density=genre["density"];max_v=_Q["max_voices"]
    if genre["pad"]:
        step_bars=rng.choice([2,4,4,8])
        for bar_n in range(0,total_bars,step_bars):
            en=energy_curve(bar_n*bar,duration)
            if en<0.12: continue
            rd,ct=prog[bar_n%len(prog)];notes=build_chord(scale[rd%len(scale)]+12,ct)
            t=bar_n*bar;dur=min(bar*rng.choice([2,4,4,8]),max(0.5,duration-t))
            events.append(Event(t,dur,Pad(notes,detune=rng.uniform(0.003,0.008)),
                vol=genre["pad_vol"]*(0.35+0.65*en),pan=rng.uniform(-0.25,0.25),
                env=ADSR(rng.uniform(0.5,2),rng.uniform(0.4,1),rng.uniform(0.65,0.92),rng.uniform(1.2,3.2))))
    for bar_n in range(total_bars):
        en=energy_curve(bar_n*bar,duration)
        rd,_=prog[bar_n%len(prog)];br=bass_scale[rd%len(bass_scale)]
        bpat=euclidean_rhythm(16,rng.choice([4,6,8]))
        for step in range(16):
            if bpat[step] and rng.random()<density*(0.4+0.6*en):
                t=humanize(bar_n*bar+step*beat*0.25,0.004)
                nd=beat*rng.choice([0.5,1,1,2]);freq=mtof(br+rng.choice([0,0,0,12]))
                events.append(Event(t,nd,SubSynth(freq,wave=genre["bass_wave"],cutoff=genre["bass_cut"],
                    res=genre["bass_res"],env_depth=genre["bass_cut"]*2.2),vol=0.56,pan=0.0,
                    env=ADSR(0.006,0.12,0.60,0.12),is_sub=True))
    lead_count=0
    for bar_n in range(total_bars):
        if lead_count>=max_v*4: break
        en=energy_curve(bar_n*bar,duration)
        if rng.random()>density*(0.30+0.70*en): continue
        rd,ct=prog[bar_n%len(prog)];cr=scale[rd%len(scale)]+genre["lead_oct"]*12
        num_notes=rng.randint(2,7)
        for n in range(num_notes):
            t=humanize(bar_n*bar+n*bar/max(1,num_notes),0.006)
            nd=bar/max(1,num_notes)*rng.uniform(0.5,0.9)
            if t>=duration: continue
            note=(rng.choice(build_chord(cr,ct)) if rng.random()<0.60 else rng.choice(scale)+genre["lead_oct"]*12)
            freq=mtof(note);lt=genre["lead"];is_sub=False
            if lt=="supersaw":   synth=SuperSaw(freq,detune=genre["lead_detune"],mix=rng.uniform(0.60,0.90))
            elif lt=="fm":       synth=FMSynth(freq,ratio=rng.choice([1,2,3,4,0.5]),depth=rng.uniform(0.6,2.8),feedback=rng.uniform(0,0.25))
            elif lt=="karplus":  synth=KarplusStrong(freq,decay=rng.uniform(0.992,0.998),brightness=rng.uniform(0.3,0.8))
            elif lt=="organ":    synth=Organ(freq)
            elif lt=="flute":    synth=FluteSynth(freq)
            else:                synth=SubSynth(freq,wave="saw",cutoff=3000,res=0.20,env_depth=2200);is_sub=True
            events.append(Event(t,nd,synth,vol=genre["lead_vol"]*(0.50+0.50*en),pan=rng.uniform(-0.45,0.45),
                env=ADSR(rng.uniform(0.01,0.05),rng.uniform(0.08,0.25),rng.uniform(0.30,0.75),rng.uniform(0.08,0.35)),is_sub=is_sub))
            lead_count+=1
    if genre["drums"]:
        kick_pat=euclidean_rhythm(16,4);hat_pat=euclidean_rhythm(16,rng.choice([8,10,12,14]))
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
    if not events:
        events.append(Event(0,max(1,duration*0.9),Pad(build_chord(root+12,"sus2"),detune=0.004),
            vol=max(0.22,genre.get("pad_vol",0.3)),pan=0,env=ADSR(0.02,0.20,0.85,0.50)))
        events.append(Event(0,max(0.8,duration*0.75),SubSynth(mtof(root-12),wave="sine",
            cutoff=max(120,genre.get("bass_cut",200)),res=0.05,env_depth=max(200,genre.get("bass_cut",200))),
            vol=0.30,pan=0,env=ADSR(0.02,0.15,0.70,0.25),is_sub=True))
    return events,duration,bpm,root,scale_name

def pure_mode_mix(mode,flags=None):
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
    return mix

def master_process(l,r,dc_l,dc_r,width=1.12,gain=0.88,drive=1.10):
    mid=(l+r)*0.5;side=(l-r)*0.5*width;l=mid+side;r=mid-side
    l=dc_l.process(soft_clip(l,drive)*gain);r=dc_r.process(soft_clip(r,drive)*gain)
    return clamp(l,-0.999,0.999),clamp(r,-0.999,0.999)

def render_music_to_wav(path,events,total_dur,mode,bpm,flags=None,mp3=False,params=None,progress_cb=None):
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
    bb_lp_l=OnePole(2600.0);bb_lp_r=OnePole(2400.0)
    dc_l=DCBlocker();dc_r=DCBlocker()
    layer_wind=Wind(0.15) if "nature" in flags or "storm" in flags else None
    layer_rain=Rain(0.20) if "nature" in flags or "storm" in flags or "light_rain" in flags else None
    layer_thunder=Thunder(0.50) if "storm" in flags else None
    layer_bowls=SingingBowl(0.30) if "bowls" in flags else None
    layer_chimes=WindChimes(0.25,0.20) if "chimes" in flags else None
    events=sorted(events,key=lambda e:e.time)
    total_samples=int(total_dur*SR)+SR;ev_ptr=0;active=[]
    width=1.12
    if "wide" in flags:   width=min(2.0,width*1.35)
    if "narrow" in flags: width=max(0.3,width*0.65)
    mg=0.88;md=1.10;progress_mark=-1;cos_f=_cos;sin_f=_sin
    with wave.open(str(path),"wb") as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
        for cs in range(0,total_samples,CHUNK):
            ce=min(cs+CHUNK,total_samples);frames=bytearray((ce-cs)*4);fi=0
            for i in range(cs,ce):
                t=i*INV_SR
                while ev_ptr<len(events) and events[ev_ptr].time<=t+0.005:
                    active.append(events[ev_ptr]);ev_ptr+=1
                sl=0.0;sr_=0.0;still=[]
                for ev in active:
                    lt=t-ev.time
                    if lt>ev.duration+ev.env.r+1.2: continue
                    still.append(ev);env_v=ev.env.get(lt,ev.duration)
                    if env_v<0.00005: continue
                    v=(ev.engine.sample(lt,env_v) if ev.is_sub else ev.engine.sample(lt))*env_v*ev.vol
                    pr=(ev.pan+1)*_PI*0.25;sl+=v*cos_f(pr);sr_+=v*sin_f(pr)
                active=still
                if bytebeat:    bb=bytebeat.sample(t);sl+=bb_lp_l.lp(bb*0.95);sr_+=bb_lp_r.lp(bb*1.05)
                if layer_bowls: bv=layer_bowls.sample(t);sl+=bv;sr_+=bv
                if layer_chimes:cl2,cr2=layer_chimes.sample_stereo(t);sl+=cl2;sr_+=cr2
                if layer_wind:  wl,wr=layer_wind.sample_stereo(t);sl+=wl;sr_+=wr
                if layer_rain:  rl,rr=layer_rain.sample_stereo(t);sl+=rl;sr_+=rr
                if layer_thunder:tl,tr=layer_thunder.sample_stereo(t);sl+=tl;sr_+=tr
                cl,cr=chorus.process(sl);cl=rev_l.process(cl);cr=rev_r.process(cr)
                cl,cr=delay.process(cl,cr)
                if vinyl:  tex=vinyl.sample();cl+=tex;cr+=tex*(1+_uniform(-0.20,0.20))
                if tape_l: cl=tape_l.process(cl);cr=tape_r.process(cr)
                cl,cr=master_process(cl,cr,dc_l,dc_r,width,mg,md)
                struct.pack_into("<hh",frames,fi,int(cl*32767),int(cr*32767));fi+=4
            w.writeframes(frames)
            pct=int((ce/total_samples)*100)
            if pct!=progress_mark:
                if progress_cb: progress_cb(pct)
                progress_mark=pct

def render_pure_to_wav(path,mode,duration,seed,flags=None,mp3=False,params=None,progress_cb=None):
    flags=flags or set();mix=pure_mode_mix(mode,flags)
    total_samples=int(duration*SR)
    wind    =Wind(mix["wind"])         if mix["wind"]>0        else None
    rain    =Rain(mix["rain"])         if mix["rain"]>0        else None
    ocean   =Ocean(mix["ocean"])       if mix["ocean"]>0       else None
    water   =WaterStream(mix["water"]) if mix["water"]>0       else None
    fire    =Fire(mix["fire"])         if mix["fire"]>0        else None
    thunder =Thunder(mix.get("thunder",0)) if mix.get("thunder",0)>0 else None
    pink    =PinkNoise()               if mix["pink"]>0        else None
    brown   =BrownNoise()              if mix["brown"]>0       else None
    bowls   =SingingBowl(mix.get("bowls",0)) if mix.get("bowls",0)>0 else None
    chimes  =WindChimes(mix.get("chimes",0)*0.8,mix.get("chimes",0)*0.5) if mix.get("chimes",0)>0 else None
    bytebeat=(BytebeatAmbient(intensity=0.30 if mode=="pure_bytebeat" else mix.get("bytebeat",0),mode=seed%5)
              if(mode=="pure_bytebeat" or mix.get("bytebeat",0)>0) else None)
    from math import pi as _PI2
    binaural_carrier=200.0
    if mode=="pure_theta":   binaural_beat=4.0
    elif mode=="pure_alpha": binaural_beat=10.0
    elif mode=="pure_delta": binaural_beat=2.0
    else:                    binaural_beat=0.0
    bbin_phase=0.0
    rev_l=Reverb(size=1.1,damp=0.50,mix=0.28);rev_r=Reverb(size=1.16,damp=0.54,mix=0.28)
    bb_lp_l=OnePole(2400.0);bb_lp_r=OnePole(2200.0)
    dc_l=DCBlocker();dc_r=DCBlocker()
    width=1.12
    if "wide"   in flags: width=min(2.0,width*1.35)
    if "narrow" in flags: width=max(0.3,width*0.65)
    mg=0.88;md=1.10;progress_mark=-1
    with wave.open(str(path),"wb") as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
        for cs in range(0,total_samples,CHUNK):
            ce=min(cs+CHUNK,total_samples);frames=bytearray((ce-cs)*4);fi=0
            for i in range(cs,ce):
                t=i*INV_SR;l=0.0;r=0.0
                if wind:   wl,wr=wind.sample_stereo(t);l+=wl;r+=wr
                if rain:   rl,rr=rain.sample_stereo(t);l+=rl;r+=rr
                if ocean:  ol,or_=ocean.sample_stereo(t);l+=ol;r+=or_
                if water:  wsl,wsr=water.sample_stereo(t);l+=wsl;r+=wsr
                if fire:   fl_,fr_=fire.sample_stereo(t);l+=fl_;r+=fr_
                if thunder:tl,tr=thunder.sample_stereo(t);l+=tl;r+=tr
                if mix["white"]>0: v=_uniform(-1,1)*mix["white"]*0.25;l+=v;r+=v
                if pink:   v=pink.sample()*mix["pink"]*0.30;l+=v;r+=v
                if brown:  v=brown.sample()*mix["brown"]*0.38;l+=v;r+=v
                if bowls:  v=bowls.sample(t);l+=v;r+=v
                if chimes: cl2,cr2=chimes.sample_stereo(t);l+=cl2;r+=cr2
                if bytebeat: v=bytebeat.sample(t);l+=bb_lp_l.lp(v*0.95);r+=bb_lp_r.lp(v*1.05)
                if binaural_beat>0:
                    bl2=fast_sin(bbin_phase)*mix["binaural"]*0.25
                    br2=fast_sin(bbin_phase+TAU*binaural_beat*t)*mix["binaural"]*0.25
                    l+=bl2;r+=br2;bbin_phase+=TAU*binaural_carrier*INV_SR
                l=rev_l.process(l);r=rev_r.process(r)
                l,r=master_process(l,r,dc_l,dc_r,width,mg,md)
                struct.pack_into("<hh",frames,fi,int(l*32767),int(r*32767));fi+=4
            w.writeframes(frames)
            pct=int((ce/total_samples)*100)
            if pct!=progress_mark:
                if progress_cb: progress_cb(pct)
                progress_mark=pct

def render_special_to_wav(path,mode,duration,seed,flags=None,mp3=False,params=None,progress_cb=None,
                          entity_profile="mountain",freeflow=0.5,message_text="",bpm=60,root=60):
    flags=flags or set();total_samples=int(duration*SR)
    dc_l=DCBlocker();dc_r=DCBlocker()
    rev_l=Reverb(size=1.2,damp=0.45,mix=0.40);rev_r=Reverb(size=1.28,damp=0.48,mix=0.40)
    width=1.12
    if "wide" in flags: width=min(2.0,width*1.35)
    mg=0.88;md=1.10;progress_mark=-1
    if mode=="entity":   gen=CosmicEntity(entity_profile,intensity=0.55)
    elif mode=="freeflow":gen=FreeflowMode(freeflow=freeflow,seed=seed)
    else:                gen=FreeflowMode(freeflow=0.5,seed=seed)
    with wave.open(str(path),"wb") as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
        for cs in range(0,total_samples,CHUNK):
            ce=min(cs+CHUNK,total_samples);frames=bytearray((ce-cs)*4);fi=0
            for i in range(cs,ce):
                t=i*INV_SR;l,r=gen.sample_stereo(t)
                l=rev_l.process(l);r=rev_r.process(r)
                l,r=master_process(l,r,dc_l,dc_r,width,mg,md)
                struct.pack_into("<hh",frames,fi,int(l*32767),int(r*32767));fi+=4
            w.writeframes(frames)
            pct=int((ce/total_samples)*100)
            if pct!=progress_mark:
                if progress_cb: progress_cb(pct)
                progress_mark=pct

def render(params,progress_cb=None):
    mode          =params.get("mode","ambient")
    seed          =params.get("seed",int(time.time()*1000)%(2**32))
    flags         =set(params.get("flags",[]))
    duration      =params.get("duration",180)
    bpm           =params.get("bpm",None)
    root_midi     =params.get("root",None)
    scale         =params.get("scale",None)
    mood          =params.get("mood",None)
    entity_profile=params.get("entity_profile","mountain")
    freeflow      =params.get("freeflow",0.5)
    quality       =params.get("quality","balanced")
    out_dir       =Path(params.get("out_dir",str(Path.home()/"Documents"/"Freeflow"))).expanduser()
    out_dir.mkdir(parents=True,exist_ok=True)
    set_quality(quality);random.seed(seed)
    ts=time.strftime("%Y%m%d_%H%M%S");stem=f"aurora_{mode}_{seed}_{ts}"
    wav_path=out_dir/f"{stem}.wav"
    if mode in PURE_MODES:
        render_pure_to_wav(wav_path,mode,duration,seed,flags=flags,params=params,progress_cb=progress_cb)
    elif mode in SPECIAL_MODES:
        rng=random.Random(seed);bpm_val=bpm or rng.randint(50,80)
        root_val=root_midi if root_midi is not None else 60
        render_special_to_wav(wav_path,mode,duration,seed,flags=flags,params=params,progress_cb=progress_cb,
                              entity_profile=entity_profile,freeflow=freeflow,bpm=bpm_val,root=root_val)
    else:
        rng=random.Random(seed)
        events,duration,bpm_val,root_val,scale_val=generate_music_events(
            mode,rng,bpm=bpm,root=root_midi,scale_name=scale,
            duration=duration,flags=flags,mood=mood)
        render_music_to_wav(wav_path,events,duration,mode,bpm_val,
                            flags=flags,params=params,progress_cb=progress_cb)
    return wav_path
'''

# ══════════════════════════════════════════════════════════════════════
#  CROSS-PLATFORM AUDIO PLAYBACK
# ══════════════════════════════════════════════════════════════════════

def _wav_duration(path):
    try:
        with wave.open(str(path), 'r') as w:
            return w.getnframes() / w.getframerate()
    except Exception:
        return 90.0


def play_wav_blocking(path, stop_event=None):
    """
    Play a WAV file, blocking until done or stop_event fires.
    Uses the best available method for the current platform.
    """
    path = str(path)
    dur  = _wav_duration(path)
    proc = None

    def _wait_proc(p):
        start = time.time()
        while p.poll() is None:
            if stop_event and stop_event.is_set():
                try: p.terminate()
                except Exception: pass
                return
            if time.time() - start > dur + 8:
                try: p.terminate()
                except Exception: pass
                return
            time.sleep(0.08)

    def _time_wait():
        start = time.time()
        while time.time() - start < dur:
            if stop_event and stop_event.is_set(): return
            time.sleep(0.08)

    try:
        # ── Windows ──────────────────────────────────────────────────
        if sys.platform == 'win32':
            try:
                import winsound as _ws
                _ws.PlaySound(path, _ws.SND_FILENAME | _ws.SND_ASYNC)
                start = time.time()
                while time.time() - start < dur + 1:
                    if stop_event and stop_event.is_set():
                        try: _ws.PlaySound(None, _ws.SND_PURGE)
                        except Exception: pass
                        return
                    time.sleep(0.08)
                return
            except Exception:
                pass
            # PowerShell fallback
            if shutil.which('powershell'):
                proc = subprocess.Popen(
                    ['powershell', '-c',
                     f'(New-Object System.Media.SoundPlayer "{path}").PlaySync()'],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                _wait_proc(proc); return

        # ── macOS ─────────────────────────────────────────────────────
        elif sys.platform == 'darwin':
            if shutil.which('afplay'):
                proc = subprocess.Popen(
                    ['afplay', path],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                _wait_proc(proc); return

        # ── Linux / Android / other ───────────────────────────────────
        for player, extra in [
            ('aplay',               []),
            ('paplay',              []),
            ('play',                []),
            ('ffplay',              ['-nodisp', '-autoexit']),
            ('mpv',                 ['--no-video', '--really-quiet']),
            ('cvlc',                ['--play-and-exit', '--intf', 'dummy']),
            ('mplayer',             ['-really-quiet']),
            ('termux-media-player', ['play']),
        ]:
            if shutil.which(player):
                cmd = [player] + extra + [path]
                proc = subprocess.Popen(
                    cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                _wait_proc(proc)
                return

        # No player found — just let the generator keep running
        _time_wait()

    except Exception:
        _time_wait()


def detect_player():
    """Return a short string describing available audio output."""
    if sys.platform == 'win32':
        try: import winsound; return 'winsound'
        except Exception: pass
        if shutil.which('powershell'): return 'powershell'
    elif sys.platform == 'darwin':
        if shutil.which('afplay'): return 'afplay'
    for p in ['aplay','paplay','play','ffplay','mpv','cvlc','mplayer','termux-media-player']:
        if shutil.which(p): return p
    return None


# ══════════════════════════════════════════════════════════════════════
#  INFINITE AMBIENT ENGINE
# ══════════════════════════════════════════════════════════════════════

# Weighted pool: ambient & bellscape get more draws for melody richness
_MUSIC_POOL = [
    'ambient',    'ambient',    'ambient',
    'bellscape',  'bellscape',
    'cosmic',     'cosmic',
    'meditation', 'meditation',
    'sacred',
    'drone',
]

_MOOD_POOL = [
    'ethereal', 'ethereal',
    'peaceful', 'peaceful',
    'mysterious',
    'melancholic',
    None, None, None,   # no mood override most of the time
]


class InfiniteAmbient:
    """
    Generates 90-second musical chunks continuously and feeds them to
    the audio player with a 2-chunk lookahead buffer.
    Each chunk is seeded from a real cosmic object (star, nebula, galaxy).
    """

    def __init__(self):
        self._playing   = False
        self._stop_ev   = threading.Event()
        self._chunk_q   = queue.Queue(maxsize=2)
        self._status_cb = None
        self._prog_cb   = None
        self._play_cb   = None    # called when playback starts (obj, mode)
        self._ns        = {}
        self._loaded    = False
        self._tmp_dir   = None

    # ── setup ─────────────────────────────────────────────────────────

    def _load_engine(self):
        if not self._loaded:
            ns = {'__name__': 'freeflow_core', '__file__': ''}
            exec(FREEFLOW_CORE_SOURCE, ns)   # noqa: S102
            self._ns = ns
            self._loaded = True
        if self._tmp_dir is None:
            self._tmp_dir = Path(tempfile.gettempdir()) / 'freeflow_ambient_chunks'
            self._tmp_dir.mkdir(exist_ok=True)

    def set_callbacks(self, status_cb=None, prog_cb=None, play_cb=None):
        self._status_cb = status_cb
        self._prog_cb   = prog_cb
        self._play_cb   = play_cb

    # ── control ───────────────────────────────────────────────────────

    def start(self):
        if self._playing: return
        self._load_engine()
        self._playing = True
        self._stop_ev.clear()
        threading.Thread(target=self._gen_loop,  daemon=True, name='ff-gen').start()
        threading.Thread(target=self._play_loop, daemon=True, name='ff-play').start()

    def stop(self):
        self._playing = False
        self._stop_ev.set()
        # drain + delete temp files
        for _ in range(self._chunk_q.qsize() + 2):
            try:
                p = self._chunk_q.get_nowait()
                try: os.unlink(p)
                except Exception: pass
            except queue.Empty:
                break

    # ── internal helpers ──────────────────────────────────────────────

    def _emit(self, msg):
        if self._status_cb: self._status_cb(msg)

    def _prog(self, pct):
        if self._prog_cb: self._prog_cb(int(pct))

    # ── generator loop ────────────────────────────────────────────────

    def _gen_loop(self):
        render        = self._ns['render']
        COSMIC_OBJECTS= self._ns['COSMIC_OBJECTS']
        apply_cosmic  = self._ns['apply_cosmic_seed']

        while self._playing:
            obj  = random.choice(COSMIC_OBJECTS)
            mode = random.choice(_MUSIC_POOL)
            mood = random.choice(_MOOD_POOL)
            seed = random.randint(0, 2**32 - 1)

            name_s = obj['name']
            type_s = obj.get('type', '?')
            temp_k = obj.get('temp', 0)

            self._emit(
                f"generating  ·  {name_s}  ({type_s})  "
                f"·  {temp_k:,} K  →  {mode}"
            )
            self._prog(0)

            params = {
                'mode':           mode,
                'duration':       90,
                'seed':           seed,
                'flags':          set(),
                'quality':        'balanced',
                'mp3':            False,
                'out_dir':        str(self._tmp_dir),
                '_mode_explicit': True,   # keep chosen musical mode
                'mood':           mood,
            }

            # Pull BPM, mood-flags, stereo-width hint from cosmic data
            # (mode is locked above so only metadata is inherited)
            try:
                params = apply_cosmic(params, name_s)
                params['mode'] = mode  # restore after apply_cosmic
            except Exception:
                pass

            try:
                path = render(params, progress_cb=self._prog)
            except Exception as e:
                self._emit(f"render error — {e}")
                time.sleep(2)
                continue

            if not self._playing:
                try: os.unlink(path)
                except Exception: pass
                break

            # Put path in queue; blocks if buffer full (2 chunks ahead)
            try:
                self._chunk_q.put(str(path), timeout=120)
            except queue.Full:
                try: os.unlink(path)
                except Exception: pass

    # ── player loop ───────────────────────────────────────────────────

    def _play_loop(self):
        while self._playing:
            try:
                path = self._chunk_q.get(timeout=1)
            except queue.Empty:
                continue

            if not self._playing:
                try: os.unlink(path)
                except Exception: pass
                break

            # Parse back the mode from filename for display
            fname = Path(path).stem  # aurora_<mode>_<seed>_<ts>
            parts = fname.split('_')
            mode_disp = parts[1] if len(parts) > 1 else '?'

            self._prog(100)
            self._emit(f"playing  ·  {mode_disp}")
            if self._play_cb: self._play_cb(mode_disp)

            play_wav_blocking(path, self._stop_ev)
            self._stop_ev.clear()

            try: os.unlink(path)
            except Exception: pass


# ══════════════════════════════════════════════════════════════════════
#  GUI
# ══════════════════════════════════════════════════════════════════════

# ── colour palette ────────────────────────────────────────────────────
BG     = '#07070f'    # deep space black
BG2    = '#0e0e1c'    # slightly lighter panel
ACC    = '#6b5ce7'    # purple accent
TEAL   = '#00d4aa'    # play button colour
RED    = '#ff4466'    # stop button colour
DIM    = '#2a2a44'    # dimmed text
MUTED  = '#484868'    # muted text
BRIGHT = '#d0d0f0'    # bright text
STAR   = '#b0a0ff'    # star info colour


class FreeflowApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('FREEFLOW  ∞')
        self.root.configure(bg=BG)
        self.root.geometry('480x380')
        self.root.resizable(True, True)
        self.root.minsize(360, 300)

        self.engine = InfiniteAmbient()
        self.engine.set_callbacks(
            status_cb=self._on_status,
            prog_cb  =self._on_progress,
            play_cb  =self._on_play,
        )
        self._playing   = False
        self._anim_id   = None
        self._dots      = 0
        self._no_player = (detect_player() is None)

        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────

    def _build_ui(self):
        root = self.root

        # ── top spacer
        tk.Frame(root, bg=BG, height=28).pack()

        # ── title
        tk.Label(root, text='FREEFLOW  ∞',
                 font=('Courier', 28, 'bold'),
                 fg=ACC, bg=BG).pack()

        tk.Label(root, text='cosmic algorithmic soundscapes',
                 font=('Courier', 9),
                 fg=DIM, bg=BG).pack(pady=(3, 0))

        # ── spacer
        tk.Frame(root, bg=BG, height=28).pack()

        # ── AMBIENT button
        self._btn = tk.Button(
            root,
            text='▶    AMBIENT',
            font=('Courier', 17, 'bold'),
            fg=TEAL, bg=BG2,
            activeforeground='#ffffff',
            activebackground='#16162e',
            relief='flat', bd=0,
            padx=52, pady=22,
            cursor='hand2',
            command=self._toggle,
        )
        self._btn.pack()

        # ── spacer
        tk.Frame(root, bg=BG, height=18).pack()

        # ── progress bar
        style = ttk.Style()
        style.theme_use('default')
        style.configure('FF.Horizontal.TProgressbar',
                        troughcolor=BG2, background=ACC,
                        thickness=3, borderwidth=0, relief='flat')
        self._prog_bar = ttk.Progressbar(
            root, style='FF.Horizontal.TProgressbar',
            orient='horizontal', length=360, mode='determinate')
        self._prog_bar.pack()

        # ── status line
        self._status_var = tk.StringVar(value='tap  AMBIENT  to begin')
        self._status_lbl = tk.Label(
            root,
            textvariable=self._status_var,
            font=('Courier', 8),
            fg=MUTED, bg=BG,
            wraplength=460,
            justify='center',
        )
        self._status_lbl.pack(pady=(10, 0))

        # ── no-player warning (hidden by default)
        if self._no_player:
            tk.Label(
                root,
                text='⚠  no audio player found — files saved to system temp folder',
                font=('Courier', 7),
                fg='#885500', bg=BG,
            ).pack(pady=(6, 0))

        # ── footer
        tk.Frame(root, bg=BG).pack(expand=True)
        tk.Label(root,
                 text='pure math  ·  no samples  ·  no internet  ·  forever',
                 font=('Courier', 7), fg='#18182a', bg=BG
                 ).pack(side=tk.BOTTOM, pady=10)

    # ── toggle play/stop ──────────────────────────────────────────────

    def _toggle(self):
        if self._playing:
            self._playing = False
            self.engine.stop()
            self._btn.config(text='▶    AMBIENT', fg=TEAL)
            self._prog_bar.configure(mode='determinate', value=0)
            if self._anim_id:
                self.root.after_cancel(self._anim_id)
                self._anim_id = None
            self._set_status('stopped', MUTED)
        else:
            self._playing = True
            self.engine.start()
            self._btn.config(text='◼    STOP', fg=RED)
            self._set_status('initializing …', MUTED)
            self._start_dot_anim()

    # ── callbacks from engine (called from worker threads) ────────────

    def _on_status(self, msg):
        self.root.after(0, lambda m=msg: self._set_status(m, MUTED))

    def _on_progress(self, pct):
        def _upd(p=pct):
            if self._playing:
                self._prog_bar.configure(mode='determinate', value=p)
        self.root.after(0, _upd)

    def _on_play(self, mode):
        """Called when a chunk starts playing."""
        def _upd(m=mode):
            if self._playing:
                self._prog_bar.configure(mode='indeterminate')
                self._prog_bar.start(30)
                self._set_status(f'♪  playing  ·  {m}', STAR)
        self.root.after(0, _upd)

    # ── dot animation (while generating) ─────────────────────────────

    def _start_dot_anim(self):
        self._dots = 0
        self._tick_dot()

    def _tick_dot(self):
        if not self._playing: return
        # Only animate when in determinate (generating) mode
        try:
            mode = str(self._prog_bar.cget('mode'))
        except Exception:
            mode = 'determinate'
        if mode == 'determinate':
            self._dots = (self._dots + 1) % 4
            dots = '·' * self._dots + '   '[self._dots:]
            # Keep status unchanged but pulse the label colour
        self._anim_id = self.root.after(500, self._tick_dot)

    # ── helpers ───────────────────────────────────────────────────────

    def _set_status(self, text, colour=MUTED):
        self._status_var.set(text)
        self._status_lbl.config(fg=colour)

    # ── run ───────────────────────────────────────────────────────────

    def run(self):
        self.root.protocol('WM_DELETE_WINDOW', self._quit)
        self.root.mainloop()

    def _quit(self):
        self.engine.stop()
        try: self.root.destroy()
        except Exception: pass


# ══════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    app = FreeflowApp()
    app.run()
