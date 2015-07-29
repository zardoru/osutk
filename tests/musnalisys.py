__author__ = 'Agka'

# this code is terrible - and it doesn't even work
# but I'm leaving it on the open for the record if I ever come back to it.

from osutk.storyboard import *
from numpy.fft import fft, fftfreq
from osutk.translate import *
from struct import unpack
import math
import numpy
import wave

framerate = 60  # n visual frames per second
sample_rate = 44100.0
audioframes_per_videoframe = int(sample_rate / framerate)  # audio frames per video frame
objects = 20
size = Screen.Width / objects
offset = 0
max_scale = 1
min_scale = 0.1

# internals ahead
divisor = 1.0 / 0x7FFF
apv = audioframes_per_videoframe  # alias
frame_fft = []
min_power = 0
max_power = -10000000


sprites = [Sprite(file="circle.png", location=[int(x*size + size / 2), int(Screen.Height + 20)], origin=Origin.BottomCenter)
           for x in range(objects)]
prev_fft = [0 for x in range(objects)]

for x in sprites:
    x.fade(Ease.Linear, 0, from_osu_time_notation("05:29:302 - "), 1, 1)

def put_fft(octs, start, end):
    global prev_fft
    hmax = (-min_power + max_power)
    for n in range(len(octs)):
        lerp_prev = (prev_fft[n] - min_power) / abs(hmax)
        lerp_next = (octs[n] - min_power) / abs(hmax)
        sprites[n].vector_scale(Ease.Linear, int(start + offset), int(end + offset),
                                0.5, lerp_prev * max_scale,
                                0.5, lerp_next * max_scale)

    prev_fft = octs

def hamming(wnd):
    for i in range(len(wnd)):
        wnd[i] *= 0.5 - 0.5 * math.cos(2 * math.pi * i / (len(wnd) - 1))


def average(bts):
    # separate interleaved data
    bts = unpack("%ih" % (len(bts) / 2), bts)
    left_ch = [v * divisor for v in bts[::2]]
    right_ch = [v * divisor for v in bts[1::2]]

    rt = []
    for u in range(len(left_ch)):
        # average and normalize both channels into -1.0 <-> 1.0 space
        rt.append((left_ch[u] + right_ch[u]) / 2)

    return left_ch

# assumptions: input.wav is stereo int16 data @ 44100Hz.
with wave.open("input.wav") as wav:
    duration = wav.getnframes()
    print("Audio lasts for {} frames. {} audio frames per video frame".format(duration, audioframes_per_videoframe))
    print("Total time: {}".format(duration / wav.getframerate()))
    print("Channels: {}, Bytes/Sample: {} Framerate: {}".format(wav.getnchannels(),
                                                                wav.getsampwidth(),
                                                                wav.getframerate()))

    ftfq = fftfreq(audioframes_per_videoframe, 1.0 / sample_rate)
    print("Frequencies: {} len: {}, max: {}".format(ftfq, len(ftfq), max(ftfq)))
    binlen = int(audioframes_per_videoframe / objects)
    print("avg bin size: {}".format(binlen))

    binsizes = []
    bin_frequencies = ftfq[1:(len(ftfq)/2)]
    lenbf = len(bin_frequencies)
    for x in range(objects):
        avg = 0
        for n in range(int(x * lenbf / objects), int((x+1) * lenbf / objects)):
            avg += bin_frequencies[n]
        avg /= float(lenbf)
        binsizes.append(avg)

    print("bin sizes for the objects: {}".format(binsizes))
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
        l, r = fftval[unique_pts:], fftval[1:unique_pts]
        # fftval = numpy.add(l, r[::-1])
        fftval = r
        # get length of each point

        octs = []
        binlen = int(len(fftval) / objects)
        for n in range(objects):
            binavg = 0
            # get average power of bin
            try:
                for binv in range(n * binlen, (n+1) * binlen):
                    binavg += 10 * math.log10(fftval[binv] ** 2)
                binavg /= float(binlen)
            except IndexError:
                print ("bin size {} for fft sized {}".format(binlen, len(fftval)))

            # maximum changed?
            if max_power < binavg or min_power > binavg:
                print("amplitude changed: {}".format(binavg))

            max_power = max(max_power, binavg)
            min_power = min(min_power, binavg)
            # add to set of bins this audio frame
            octs.append(binavg)

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
