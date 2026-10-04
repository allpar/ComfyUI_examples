"""Music edit + synthesized sound design for the 15s reel.
Music: 'Release the Hybrids' (FreePD, CC0) from 68.70s; hard cut on the bar at END.
All SFX are generated here (no third-party samples)."""
import numpy as np, subprocess, sys
from scipy.signal import butter, sosfilt, fftconvolve
import soundfile as sf

SR = 48000
DUR = 15.0
DROP, PULSE = 3.97, 0.3245
BAR = PULSE * 6
BARS = [DROP + i * BAR for i in range(6)]
END = BARS[5]
N = int(DUR * SR)
rng = np.random.default_rng(3)
music_src = sys.argv[1]

def tt(n): return np.arange(n) / SR
def bp(x, lo, hi, order=2): return sosfilt(butter(order, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f, order=2): return sosfilt(butter(order, f, 'lowpass', fs=SR, output='sos'), x)
def hp(x, f, order=2): return sosfilt(butter(order, f, 'highpass', fs=SR, output='sos'), x)
def place(buf, sig, at, gain=1.0):
    i = int(at * SR); j = min(len(buf), i + len(sig))
    if i < 0: sig = sig[-i:]; i = 0
    buf[i:j] += sig[: j - i] * gain
def stereo(m, width=0.0, delay_ms=0.0):
    d = int(delay_ms * SR / 1000)
    L = m.copy(); R = np.concatenate([np.zeros(d), m[: len(m) - d]]) if d else m.copy()
    return np.stack([L * (1 + width), R * (1 - width)], 1)

# ---------------- music ----------------
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "68.70", "-t", f"{END + 0.05:.3f}", "-i", music_src,
                      "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
mus = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
cut = int(END * SR)
mus = mus[:cut]
fade = int(0.012 * SR); mus[-fade:] *= np.linspace(1, 0, fade)[:, None]
mus[: int(.01 * SR)] *= np.linspace(0, 1, int(.01 * SR))[:, None]
music = np.zeros((N, 2)); music[: len(mus)] = mus

sfx = np.zeros((N, 2))

# ---------------- riser into the drop ----------------
rl = 0.75; n = int(rl * SR); x = tt(n)
noise = rng.standard_normal(n)
k = x / rl
riser = np.zeros(n)
# swept band-pass noise (process in short blocks with rising centre freq)
blk = 1024
for s in range(0, n, blk):
    c = 500 * (16 ** (s / n))
    seg = bp(noise[max(0, s - 4096): s + blk], c * 0.7, min(c * 1.6, 20000))[-min(blk, n - s):]
    riser[s: s + len(seg)] = seg
riser *= k ** 2.2
tone = np.sin(2 * np.pi * np.cumsum(180 * (4 ** k)) / SR) * 0.25 * k ** 3
place(sfx, stereo(riser * 0.55 + tone, delay_ms=6), DROP - rl)

# ---------------- impact generator ----------------
def impact(length, f0, f1, sub=1.0, crack=0.5, tail=0.0):
    n = int(length * SR); x = tt(n)
    f = f1 + (f0 - f1) * np.exp(-x / 0.08)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / (length * 0.35)) * sub
    cr = hp(rng.standard_normal(n), 1200) * np.exp(-x / 0.03) * crack
    thud = lp(rng.standard_normal(n), 300) * np.exp(-x / 0.12) * 0.6
    s = body + cr + thud
    if tail > 0:   # synthetic hall reverb
        ir_n = int(tail * SR); ir = rng.standard_normal(ir_n) * np.exp(-tt(ir_n) / (tail * 0.28))
        ir = lp(ir, 6000)
        wet = fftconvolve(s, ir)[:n] / np.sqrt(ir_n) * 6
        s = s + wet
    return s

place(sfx, stereo(impact(1.6, 120, 38, sub=.9, crack=.35, tail=1.5), delay_ms=9), DROP, 0.22)

# ---------------- whoosh for the tram whip (bar 4) ----------------
def whoosh(length, up=False):
    n = int(length * SR); x = tt(n); noise = rng.standard_normal(n); out = np.zeros(n)
    for s in range(0, n, 512):
        p = s / n; c = (300 * 20 ** p) if up else (6000 * 0.06 ** p)
        seg = bp(noise[max(0, s - 2048): s + 512], c * .6, min(c * 1.8, 20000))[-min(512, n - s):]
        out[s: s + len(seg)] = seg
    env = np.sin(np.pi * np.clip(x / length, 0, 1)) ** 1.5
    return out * env
place(sfx, stereo(whoosh(.45), width=.25), BARS[3] - .2, .5)
place(sfx, stereo(whoosh(.3), width=-.25), BARS[3] + 3 * PULSE - .12, .32)

# ---------------- logo bar: soft hit + reverse swell into the final impact ----------------
place(sfx, stereo(impact(1.2, 90, 45, sub=.7, crack=.25, tail=1.2), delay_ms=7), BARS[4], .2)
sw_n = int(0.6 * SR); swell = lp(rng.standard_normal(sw_n), 4000) * np.linspace(0, 1, sw_n) ** 3
place(sfx, stereo(swell, delay_ms=11), END - 0.6, .35)

# ---------------- final impact + long tail ----------------
fin = impact(3.2, 140, 30, sub=1.1, crack=.6, tail=2.8)
place(sfx, stereo(fin, delay_ms=13), END, .22)
# airy shimmer tail (filtered noise, not tonal, so nothing clashes)
sh_n = int(1.3 * SR); sh = hp(rng.standard_normal(sh_n), 5000) * np.exp(-tt(sh_n) / .45) * .08
place(sfx, stereo(sh, delay_ms=17), END + .02)

mix = music * 0.9 + sfx
# end fade (match video fade)
fo0 = int((DUR - .35) * SR); mix[fo0:] *= np.linspace(1, 0, N - fo0)[:, None] ** 1.5
peak = np.abs(mix).max(); mix = mix / peak * 0.89
sf.write("mix_pre.wav", mix.astype(np.float32), SR)
print("peak before norm", peak, "music peak", np.abs(music).max(), "sfx peak", np.abs(sfx).max())
for a,b in [(0,4),(4,13.7),(13.7,15)]:
    i,j=int(a*SR),int(b*SR); print(a,b,"music rms %.3f sfx rms %.3f"%(np.sqrt((music[i:j]**2).mean()),np.sqrt((sfx[i:j]**2).mean())))
