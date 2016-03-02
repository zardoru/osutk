__author__ = 'Agka'

# osu!tk + numpy based spectrum analyzer
# generates osb with spectrum based off wav files

from osutk.storyboard import *

# File to open and do the analysis on. Note that python only has support for wav.
input_file = "input.wav"

# File to output the OSB to.
output_file = "fft.osb"

# Whether to make the storyboard widescreen.
widescreen = 1

# How many frames per second to render the FFT.
framerate = 30

# Audio sampling rate. Adjust properly.
sample_rate = 44100.0

# How large can the objects grow
max_scale = 0.8

# How small the objects should be at least
min_scale = 0.1

# Horizontal scale
h_scale = 0.708333333333333333

# Origin of the bars
bar_origin = Origin.BC

# Location of the bars (y axis
bar_loc = Screen.Height

# For how long to fade out
fade_threshold = 500  # 0.5 sec

# Bar filename
bar_fn = "bar.png"

# Advanced

# Whether to use the hann window on the samples
use_window = 1

# In the strange case your mp3 and your wav differ, adjust this. Otherwise leave as-is.
offset = 0

# repeat fft twice instead of reducing it
symmetrical = 0

# use center as low frequencies and edges as high if symmetrical
sym_reverse = 0

# INTERNALS
##############################################################################################
from time import time
import math
import wave
import numpy
from numpy.fft import fft, fftfreq
from struct import unpack

process_time = time()

# Pick the octave thirds centers to draw. One object per requency. Adjust accordingly with framerate.
octave_third_centers = [50, 80, 100, 125,
                 160, 200, 315, 400, 500, 630, 800, 1000, 1250,
                 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000]

if symmetrical:
    if sym_reverse:
        octave_third_centers = octave_third_centers[::-1] + octave_third_centers
    else:
        octave_third_centers = octave_third_centers + octave_third_centers[::-1]

divisor = 1.0 / 0x7FFF
frame_fft = []
objects = len(octave_third_centers)
min_power = [0] * objects
max_power = [-10000000] * objects

if not widescreen:
    size = Screen.Width / objects
else:
    size = Screen.WidthWidescreen / objects

# audio frames per video frame
samples_per_frame = int(sample_rate / framerate)

# Music precalculations.
print("{} sub-octave centers".format(objects))

# Calculate upper and lower bounds of every octave.
base_round = lambda val, base: int(base * round(float(val)/base))
fft_frequencies = [int(x) for x in fftfreq(samples_per_frame, 1.0 / sample_rate)]
difference = fft_frequencies[1] - fft_frequencies[0]

upper_octaves = [base_round(x * (2.0 ** (1.0 / (2 * 3))), difference) for x in octave_third_centers]
lower_octaves = [base_round(x / (2.0 ** (1.0 / (2 * 3))), difference) for x in octave_third_centers]

print("Octave bounds: \n\tLow: {} \n\tHigh: {}".format(lower_octaves, upper_octaves))

# Now we'll have the FFT frequencies for what we're getting from the audio.
upper_index = [fft_frequencies.index(x) if x in fft_frequencies else len(fft_frequencies)-1 for x in upper_octaves]
lower_index = [fft_frequencies.index(x) if x in fft_frequencies else len(fft_frequencies)-1 for x in lower_octaves]

print("Octave indices: \n\tLow: {} \n\tHigh: {}".format(lower_index, upper_index))

# FFT and Audio Processing
###############################################################################

def average(bts):
    # separate interleaved s16 data, and then normalize to float
    bts = unpack("%ih" % (len(bts) / 2), bytes(bts))
    left_ch = [v * divisor for v in bts[::2]]
    right_ch = [v * divisor for v in bts[1::2]]

    return numpy.multiply(numpy.add(left_ch, right_ch), 0.5)

# because it matters: this is -way- faster than getting
# the window from numpy every single time.
from numpy import hanning

def apply_hanning_window(wnd):
    return numpy.multiply(wnd, hanning(len(wnd)))

def do_fft():
    # assumptions: input.wav is stereo int16 data @ 44100Hz.
    with wave.open(input_file) as wav:
        global fadeout_start
        duration = wav.getnframes() / wav.getframerate()
        frames_total = wav.getnframes()
        fadeout_start = round(duration * 1000)
        print("Audio lasts for {} frames. {} audio frames per video frame".format(frames_total, samples_per_frame))
        print("Total time: {}".format(duration))
        print("Channels: {}, Bytes/Sample: {} Framerate: {}".format(wav.getnchannels(),
                                                                    wav.getsampwidth(),
                                                                    wav.getframerate()))

        freq_center = len(fft_frequencies) // 2
        print("Frequencies: {} len: {}, max: {}".format(
            fft_frequencies[:freq_center], freq_center, max(fft_frequencies)))

        current_frame = 0
        while current_frame < frames_total:
            frames = wav.readframes(samples_per_frame)
            frames = average(frames)
            if use_window:
                frames = apply_hanning_window(frames)

            if len(frames) == 0:
                print("read 0 frames D:")
                break
            fft_values = fft(frames)
            fft_values = numpy.abs(fft_values)

            unique_pts = len(fft_values) / 2
            # l, r = fft_values[:unique_pts], fft_values[unique_pts:]
            l = fft_values[:unique_pts]
            if not symmetrical:  # repeat FFT twice or not?
                fft_values = l
            else:
                if sym_reverse:
                    fft_values = l[::-1] + l
                else:
                    fft_values = l + l[::-1]

            bins_this_frame = []
            for fft_bin in range(objects):
                bin_max = 0
                range_len = upper_index[fft_bin] - lower_index[fft_bin]
                if range_len != 0:
                    for frequency_value in range(lower_index[fft_bin], upper_index[fft_bin]):
                        if frequency_value < len(fft_values):
                            bin_max = max(10 * math.log10(fft_values[frequency_value] ** 2), bin_max)
                    # There's several ways of doing this; raw amplitude, power, decibel scale
                    # you could take the average or the maximum, I settle for the max.

                    max_power[fft_bin] = max(max_power[fft_bin], bin_max)
                    min_power[fft_bin] = min(min_power[fft_bin], bin_max)

                    # add to set of bins this audio frame
                    bins_this_frame.append(bin_max)
                else:
                    raise ValueError("The framerate is too high for the frequency {} to be properly represented"\
                                     .format(octave_third_centers[fft_bin]))

            # add bins to fft analysis data
            frame_fft.append(((current_frame - samples_per_frame) * 1000 / wav.getframerate(),
                              current_frame * 1000 / wav.getframerate(), bins_this_frame))
            current_frame += samples_per_frame
            print(" Processed: {:.0f} second(s)".format(current_frame / wav.getframerate()), end='\r')


# Final output.
###############################################################################

prev_fft = [0 for x in range(objects)]
# FFT scaling and output events. Don't touch this.
def put_fft(fft_tuples, start, end):
    global prev_fft

    normal_amt = abs(max(max_power))
    for n in range(len(fft_tuples)):
        if fft_tuples[n] == prev_fft[n]:
            continue  # don't be redundant.

        # Uncommenting the next line means that each bin from the spectrum will
        # instead of using the max. power in general, it'll use the max. power of this bin.
        # normal_amt = max_power[n]
        # Don't allow negative values. Normalize power to usable boundaries.
        lerp_prev = max((prev_fft[n]) / normal_amt, 0)
        lerp_next = max((fft_tuples[n]) / normal_amt, 0)

        # Do the vector scaling for the sprites.
        sprites[n].vector_scale(Ease.Linear, int(start + offset), int(end + offset),
                                h_scale, lerp_prev * (max_scale - min_scale) + min_scale,
                                h_scale, lerp_next * (max_scale - min_scale) + min_scale)

    prev_fft = fft_tuples


def perform_fft_storyboard():
    do_fft()
    print("\nPower: \n\tMin: {} \n\tMax: {}".format(min_power, max_power))
    print("Generating events.")

    x_offset = 0
    if widescreen:
        x_offset = Screen.StartWidescreen

    sprites = [Sprite(file=bar_fn, location=[x*size + size / 2 + x_offset, bar_loc], origin=bar_origin)
               for x in range(objects)]

    # Fade out. Recommended that you adjust the parameters instead.
    for x in sprites:
        x.fade(Ease.Linear, 0, fadeout_start, 1, 1)
        x.fade(Ease.Linear, fadeout_start, fadeout_start + fade_threshold, 1, 0)
    for x in frame_fft:
        put_fft(x[2], x[0], x[1])

    print("Exporting osb.")
    Storyboard.export("fft.osb")

    print("Processing took {:.2f} seconds.".format(time() - process_time))


# Now, everything's pretty much ready. Do it.
if __name__ == "__main__":
    perform_fft_storyboard()
