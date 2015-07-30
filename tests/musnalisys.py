__author__ = 'Agka'

from osutk.storyboard import *
from osutk.translate import *

# File to open and do the analysis on. Note that python only has support for wav.
input_file = "input.wav"

# File to output the OSB to.
output_file = "fft.osb"

# Pick the octave thirds centers to draw. One object per frequency. Adjust accordingly with framerate.
octavecenters = [31.5, 63, 80, 100, 125,
                 160, 200, 315, 400, 500, 630, 800, 1000, 1250,
                 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000]

# How many frames per second to render the FFT.
framerate = 30

# Audio sampling rate. Adjust properly.
sample_rate = 44100.0

# How large can the objects grow
max_scale = 0.55

# When to fade out (in ms) the objects.
fadeout_start = from_osu_time_notation("04:32:695 - ")

# For how long to fade out
fade_threshold = 1000  # 1 sec

# Whether to use the hann window on the samples
use_window = 1

# In the strange case your mp3 and your wav differ, adjust this. Otherwise leave as-is.
offset = 0

# INTERNALS
##############################################################################################
import numpy
import math
import wave
from numpy.fft import fft, fftfreq
from struct import unpack

divisor = 1.0 / 0x7FFF
frame_fft = []
objects = len(octavecenters)
min_power = [0 for x in octavecenters]
max_power = [-10000000 for x in octavecenters]
size = Screen.Width / objects
samples_per_frame = int(sample_rate / framerate)  # audio frames per video frame

# Music precalculations.

print("{} octave centers".format(objects))

# Calculate upper and lower bounds of every octave.
base_round = lambda val, base: int(base * round(float(val)/base))
fft_frequencies = [x for x in fftfreq(samples_per_frame, 1.0 / sample_rate)]
difference = fft_frequencies[1] - fft_frequencies[0]

upper_octaves = [base_round(x * 2.0 ** (1.0 / (2.0 ** (1 / (2 * 3)))), difference) for x in octavecenters]
lower_octaves = [base_round(x / 2.0 ** (1.0 / (2.0 ** (1 / (2 * 3)))), difference) for x in octavecenters]

print("Octave bounds: \n\tLow: {} \n\tHigh: {}".format(lower_octaves, upper_octaves))

# Now we'll have the FFT frequencies for what we're getting from the audio.
upper_index = [fft_frequencies.index(x) if x in fft_frequencies else len(fft_frequencies)-1 for x in upper_octaves]
lower_index = [fft_frequencies.index(x) if x in fft_frequencies else len(fft_frequencies)-1 for x in lower_octaves]

print("Octave indices: \n\tLow: {} \n\tHigh: {}".format(lower_index, upper_index))

# SB output. Adjust this if you'd rather have different parameters
###############################################################################
sprites = [Sprite(file="circle.png", location=[int(x*size + size / 2), int(Screen.Height / 2)], origin=Origin.Center)
           for x in range(objects)]

# Fade out. Recommended that you adjust the parameters instead.
for x in sprites:
    x.fade(Ease.Linear, 0, fadeout_start, 1, 1)
    x.fade(Ease.Linear, fadeout_start, fadeout_start + fade_threshold, 1, 0)

prev_fft = [0 for x in range(objects)]
# FFT scaling. Don't touch this.
def put_fft(fft_tuples, start, end):
    global prev_fft

    normal_amt = abs(max(max_power))
    for n in range(len(fft_tuples)):
        if fft_tuples[n] == prev_fft[n]:
            continue  # don't be redundant.
        # normal_amt = max_power[n]
        # Don't allow negative values. Normalize power to usable boundaries.
        lerp_prev = max((prev_fft[n]) / normal_amt, 0)
        lerp_next = max((fft_tuples[n]) / normal_amt, 0)

        # Do the vector scaling for the sprites.
        sprites[n].vector_scale(Ease.Linear, int(start + offset), int(end + offset),
                                0.45, lerp_prev * max_scale,
                                0.45, lerp_next * max_scale)

    prev_fft = fft_tuples

# FFT and Audio Processing
###############################################################################

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
with wave.open(input_file) as wav:
    duration = wav.getnframes()
    print("Audio lasts for {} frames. {} audio frames per video frame".format(duration, samples_per_frame))
    print("Total time: {}".format(duration / wav.getframerate()))
    print("Channels: {}, Bytes/Sample: {} Framerate: {}".format(wav.getnchannels(),
                                                                wav.getsampwidth(),
                                                                wav.getframerate()))

    freq_center = len(fft_frequencies) // 2
    print("Frequencies: {} len: {}, max: {}".format(fft_frequencies[:freq_center], freq_center, max(fft_frequencies)))
    binlen = int(samples_per_frame / objects)
    print("avg bin size: {}".format(binlen))

    x = 0
    while x < duration:
        frames = wav.readframes(samples_per_frame)
        frames = average(frames)

        if use_window:
            hamming(frames)

        if len(frames) == 0:
            print("read 0 frames D:")
            break
        fft_values = fft(frames)
        fft_values = abs(fft_values)

        unique_pts = len(fft_values) / 2
        l, r = numpy.split(fft_values, 2)
        fft_values = numpy.add(l, r[::-1])

        octs = []
        for n in range(objects):
            binavg = 0
            # get average power of bin. first get the range of frequencies for this bin
            range_len = upper_index[n] - lower_index[n]
            if range_len != 0:
                for binv in range(lower_index[n], upper_index[n]):
                    if binv < len(fft_values):
                        binavg = max(10 * math.log10(fft_values[binv] ** 2), binavg)
                # There's several ways of doing this; raw amplitude, power, decibel scale
                # you could take the average or the maximum, I settle for the max.
                # binavg /= float(range_len)

                max_power[n] = max(max_power[n], binavg)
                min_power[n] = min(min_power[n], binavg)

                # add to set of bins this audio frame
                octs.append(binavg)
            else:
                raise ValueError("The framerate is too high for the frequency {} to be properly represented".format(n))

        # output to storyboard
        # add bins to fft analysis data
        frame_fft.append(((x - samples_per_frame) * 1000 / wav.getframerate(),
                          x * 1000 / wav.getframerate(), octs))
        x += samples_per_frame
        print(" Processed: {:.0f} second(s)".format(x / wav.getframerate()), end='\r')

print("\n")

# Final output.
###############################################################################
print("Power: \n\tMin: {} \n\tMax: {}".format(min_power, max_power))

print("Generating events.")
for x in frame_fft:
    put_fft(x[2], x[0], x[1])

print("Exporting osb.")
Storyboard.export("fft.osb")
