"""A small Ricoh 2A03 (NES APU) emulation for writing music frame by frame (numpy only).

Four channels, nothing else:
  p1, p2  pulse: duty 12.5 / 25 / 50 / 75 %, 4-bit volume, 11-bit period
  tri     triangle: the 32-step, 4-bit stepped wave, no volume control (on or halted;
          a halted triangle freezes at its current step, as the chip does)
  noise   15-bit LFSR, long or short (93-step "metallic") mode, 16 periods, 4-bit volume
Every parameter is set once per 60 Hz frame (as a sound driver does); pitches are
quantised to the chip's period registers (NTSC CPU clock). The channels are rendered at
4 x 48 kHz, mixed through the 2A03's own non-linear DAC formulas, then low-passed and
decimated to 48 kHz, with the console's fixed output filtering (first-order high-pass
37 Hz, low-pass 14 kHz, Famicom-like). Mono.
"""
import numpy as np

SR = 48000
OS = 4
SRO = SR * OS
FPS = 60
SPF = SRO // FPS                     # samples (oversampled) per frame
CPU = 1789773.0
DUTY = np.array([[0, 1, 0, 0, 0, 0, 0, 0], [0, 1, 1, 0, 0, 0, 0, 0],
                 [0, 1, 1, 1, 1, 0, 0, 0], [1, 0, 0, 1, 1, 1, 1, 1]], dtype=np.float32)
TRI = np.array(list(range(15, -1, -1)) + list(range(16)), dtype=np.float32)
NOISE_PERIOD = [4, 8, 16, 32, 64, 96, 128, 160, 202, 254, 380, 508, 762, 1016, 2034, 4068]


def _lfsr(short):
    reg, out = 1, np.empty(32767, dtype=np.float32)
    tap = 6 if short else 1
    for i in range(32767):
        fb = (reg & 1) ^ ((reg >> tap) & 1)
        reg = (reg >> 1) | (fb << 14)
        out[i] = 1 - (reg & 1)        # the channel outputs its volume while bit 0 is clear
    return out


LFSR = [_lfsr(False), _lfsr(True)]


def mtof(m):
    return 440.0 * 2.0 ** ((np.asarray(m, dtype=float) - 69.0) / 12.0)


def pulse_freq(m):
    t = np.clip(np.round(CPU / (16 * mtof(m)) - 1), 8, 2047)
    return CPU / (16 * (t + 1))


def tri_freq(m):
    t = np.clip(np.round(CPU / (32 * mtof(m)) - 1), 2, 2047)
    return CPU / (32 * (t + 1))


class APU:
    def __init__(self, seconds):
        self.nf = int(round(seconds * FPS))
        nan = np.full(self.nf, np.nan)
        self.p = [dict(m=nan.copy(), v=np.zeros(self.nf, int), d=np.zeros(self.nf, int)) for _ in range(2)]
        self.t = dict(m=nan.copy())
        self.n = dict(v=np.zeros(self.nf, int), per=np.zeros(self.nf, int), mode=np.zeros(self.nf, int),
                      set=np.zeros(self.nf, bool))

    # ---- writing, one frame at a time (a later write steals the channel)
    def pulse(self, ch, f, m, v, d, weak=False):
        if 0 <= f < self.nf:
            c = self.p[ch]
            if weak and not np.isnan(c['m'][f]):
                return
            c['m'][f], c['v'][f], c['d'][f] = m, int(np.clip(round(v), 0, 15)), d

    def triangle(self, f, m, weak=False):
        if 0 <= f < self.nf:
            if weak and not np.isnan(self.t['m'][f]):
                return
            self.t['m'][f] = m

    def tri_halt(self, f):
        if 0 <= f < self.nf:
            self.t['m'][f] = np.nan

    def noise(self, f, v, per, mode=0, weak=False):
        if 0 <= f < self.nf:
            if weak and self.n['set'][f]:
                return
            self.n['v'][f], self.n['per'][f], self.n['mode'][f] = int(np.clip(round(v), 0, 15)), per, mode
            self.n['set'][f] = True

    # ---- rendering
    def render(self):
        nf, S = self.nf, SPF
        rep = lambda a: np.repeat(a, S)
        outs = []
        for c in self.p:
            on = ~np.isnan(c['m']) & (c['v'] > 0)
            fr = np.where(on, pulse_freq(np.nan_to_num(c['m'], nan=60.0)), 0.0)
            ph = np.cumsum(rep(fr) / SRO)
            step = (np.floor(ph * 8) % 8).astype(np.int64)
            outs.append(DUTY[rep(c['d']), step] * rep(np.where(on, c['v'], 0)).astype(np.float32))
        p1, p2 = outs
        tm = self.t['m']
        fr = np.where(np.isnan(tm), 0.0, tri_freq(np.nan_to_num(tm, nan=60.0)))
        ph = np.cumsum(rep(fr) / SRO) + 0.5 / 32         # start mid-wave (step 15 -> 0 ramp)
        tri = TRI[(np.floor(ph * 32) % 32).astype(np.int64)]
        per = np.array(NOISE_PERIOD)[self.n['per']]
        clk = np.cumsum(rep(CPU / per) / SRO)
        idx = (np.floor(clk) % 32767).astype(np.int64)
        mode = rep(self.n['mode'])
        bit = np.where(mode == 1, LFSR[1][idx], LFSR[0][idx])
        nz = bit * rep(self.n['v']).astype(np.float32)
        del outs, ph, clk, idx, mode, bit
        ps = p1 + p2
        pulse_out = np.where(ps > 0, 95.88 / (8128.0 / np.maximum(ps, 1e-9) + 100.0), 0.0)
        tn = tri / 8227.0 + nz / 12241.0
        tnd_out = np.where(tn > 0, 159.79 / (1.0 / np.maximum(tn, 1e-12) + 100.0), 0.0)
        x = (pulse_out + tnd_out).astype(np.float64)
        del pulse_out, tnd_out, ps, tn, p1, p2, tri, nz
        # anti-alias low-pass and decimation to 48 kHz
        taps = 95
        k = np.arange(taps) - (taps - 1) / 2
        h = np.sinc(2 * 0.45 / OS * k) * np.hanning(taps)
        h /= h.sum()
        y = np.convolve(x, h, mode='same')[::OS]
        # console output stage: first-order high-pass 37 Hz and low-pass 14 kHz
        nfft = 1 << int(np.ceil(np.log2(len(y) + SR)))
        Y = np.fft.rfft(y, nfft)
        f = np.fft.rfftfreq(nfft, 1 / SR)
        H = (1j * f / 37.0) / (1 + 1j * f / 37.0) / (1 + 1j * f / 14000.0)
        return np.fft.irfft(Y * H, nfft)[:len(y)]
