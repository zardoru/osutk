__author__ = 'Agka'

import numpy
import math
import wave
from osutk.storyboard import *
from numpy.fft import fft, fftfreq
from osutk.translate import *
from struct import unpack

octavecenters = [25, 31.5, 40, 50, 63, 80, 100, 125,
                 160, 200, 315, 400, 500, 630, 800, 1000, 1250,
                 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000,
                 10000, 12500, 16000]

framerate = 30  # n visual frames per second
sample_rate = 44100.0
audioframes_per_videoframe = int(sample_rate / framerate)  # audio frames per video frame
offset = 0
max_scale = 0.55
fade_threshold = 1000  # 1 sec
fadeout_start = from_osu_time_notation("04:33:750 - ")

# internals ahead
divisor = 1.0 / 0x7FFF
apv = audioframes_per_videoframe  # alias
frame_fft = []
min_power = 0
max_power = -10000000
objects = len(octavecenters)
size = Screen.Width / objects

# Music precalculations.

print("{} octave centers".format(objects))

# Calculate upper and lower bounds of every octave.
base_round = lambda val, base: int(base * round(float(val)/base))
ftfq = [x for x in fftfreq(audioframes_per_videoframe, 1.0 / sample_rate)]
difference = ftfq[1] - ftfq[0]

upper_octaves = []
lower_octaves = []
for x in octavecenters:
    upper_octaves.append(base_round(x * 2.0 ** (1.0 / (2.0 ** (1 / (2 * 3)))), difference))
    lower_octaves.append(base_round(x / 2.0 ** (1.0 / (2.0 ** (1 / (2 * 3)))), difference))

print("Octave bounds: {} {}".format(lower_octaves, upper_octaves))

# Now we'll have the FFT frequencies for what we're getting from the audio.
upper_index = [ftfq.index(x) if x in ftfq else len(ftfq)-1 for x in upper_octaves]
lower_index = [ftfq.index(x) if x in ftfq else len(ftfq)-1 for x in lower_octaves]

print("Octave indices: {} {}".format(lower_index, upper_index))

# SB output
sprites = [Sprite(file="circle.png", location=[int(x*size + size / 2), int(Screen.Height / 2)], origin=Origin.Center)
           for x in range(objects)]
prev_fft = [0 for x in range(objects)]

for x in sprites:
    x.fade(Ease.Linear, 0, fadeout_start, 1, 1)
    x.fade(Ease.Linear, fadeout_start, fadeout_start + fade_threshold, 1, 0)


def put_fft(octs, start, end):
    global prev_fft
    hmax = max(abs(min_power), abs(max_power))
    # hmax = -min_power + max_power
    for n in range(len(octs)):
        lerp_prev = max((prev_fft[n]) / abs(hmax), 0)
        lerp_next = max((octs[n]) / abs(hmax), 0)
        sprites[n].vector_scale(Ease.Linear, int(start + offset), int(end + offset),
                                0.4, lerp_prev * max_scale,
                                0.4, lerp_next * max_scale)

    prev_fft = octs

# FFT and Audio Processing

def hamming(wnd):
    for i in range(len(wnd)):
        wnd[i] *= 0.5 - 0.5 * math.cos(2 * math.pi * i / (len(wnd) - 1))


def average(bts):
    # separate interleaved data and normalize
    bts = unpack("%ih" % (len(bts) / 2), bts)
    left_ch = [v * divisor for v in bts[::2]]
    right_ch = [v * divisor for v in bts[1::2]]

    rt = []
    for u in range(len(left_ch)):
        # average both channels into -1.0 <-> 1.0 space
        rt.append((left_ch[u] + right_ch[u]) / 2)

    return rt

# assumptions: input.wav is stereo int16 data @ 44100Hz.
with wave.open("input.wav") as wav:
    duration = wav.getnframes()
    print("Audio lasts for {} frames. {} audio frames per video frame".format(duration, audioframes_per_videoframe))
    print("Total time: {}".format(duration / wav.getframerate()))
    print("Channels: {}, Bytes/Sample: {} Framerate: {}".format(wav.getnchannels(),
                                                                wav.getsampwidth(),
                                                                wav.getframerate()))

    print("Frequencies: {} len: {}, max: {}".format(ftfq, len(ftfq), max(ftfq)))
    binlen = int(audioframes_per_videoframe / objects)
    print("avg bin size: {}".format(binlen))

    x = 0
    while x < duration:
        frames = wav.readframes(audioframes_per_videoframe)
        frames = average(frames)
        hamming(frames)

        if len(frames) == 0:
            print("read 0 frames D:")
            break
        fftval = fft(frames)
        fftval = abs(fftval)

        unique_pts = len(fftval) / 2

        r, l = fftval[unique_pts:], fftval[:unique_pts]
        fftval = numpy.add(l, r[::-1])
        # get length of each point

        octs = []
        for n in range(objects):
            binavg = 0
            # get average power of bin
            range_len = upper_index[n] - lower_index[n]
            if range_len != 0:
                for binv in range(lower_index[n], upper_index[n]):
                    if binv < len(fftval):
                        binavg += 20 * math.log10(fftval[binv] ** 2)
                binavg /= float(range_len)

                # maximum changed?
                if max_power < binavg or min_power > binavg:
                    print("amplitude changed: {}".format(binavg))

                max_power = max(max_power, binavg)
                min_power = min(min_power, binavg)
                # add to set of bins this audio frame
                octs.append(binavg)
            else:
                raise ValueError("The framerate is too high for the frequency {} to be properly represented".format(n))

        # output to storyboard
        # add bins to fft analysis data
        frame_fft.append((x * 1000 / wav.getframerate(),
                          (x + audioframes_per_videoframe) * 1000 / wav.getframerate(),
                          octs))
        x += audioframes_per_videoframe


print("Min. power: {} Max: {}".format(min_power, max_power))
for x in frame_fft:
    put_fft(x[2], x[0], x[1])

Storyboard.export("fft.osb")
