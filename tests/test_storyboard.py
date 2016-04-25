import math

from osutk.storyboard import *
from osutk.translate import from_osu_time_notation, bpm_to_beatspace

__author__ = 'Agka'

# initializing a sprite
# only the sprite uses the [] form of vectors.
# roll your own if you want to for events ;)
s = Sprite(file="Welcome.png", location=[Screen.Width / 2, Screen.Height / 2], origin=Origin.Center)


# Full form
s.move(Ease.Linear, 0, 1000, 0, 100, 0, 100)


# merely display this sprite for this time - super short!
# defaults to fade value 1.
# note: recall that sprites are only displayed as long as commands are
# active, so merely displaying is setting fade to 1 for some duration.
s.fade(_st=1000, _et=3000)


# keyword form
# note that the keyword names vary according to the event type
# check the docs for more info
s.vector_scale(_ease=Ease.Linear,
               _st=0, _et=1000,  # Time
               _sx=1, _sy=1,  # X/Y start
               _ex=2, _ey=2)  # X/Y end


# parameters example
s.flip_horizontally(1000, 2000)  # flip from 1s to 2s


# keyword arguments form
s.scale(_st=3000, _ss=2)  # Time 3s, scale = 2

# duration form + osu time notation example
# starts at 2000, ends at 2500 (set _dur on all events except loop but do not set _et to use this)
s.fade(_st=2000, _dur=from_osu_time_notation("00:00:500"))


# rotate example:
# for 4 beats of 135 bpm
# starting at 6000ms
# rotate 4 times a full circle
s.rotate(_st=6000, _dur=bpm_to_beatspace(135) * 4, _sr=0, _er=math.pi * 2 * 4)


# all default parameters but file
# background layer, position (0,0), TL origin.
l = Sprite(file="lol.png")

# chain several events together, looped or not
l.loop(0, 10)\
    .scale(Ease.In, 0, 500, 1, 0.5)\
    .move_x(Ease.Linear, 500, 1000, 200, 400)


# with x as y form
with s.loop(0, 3) as loop:
    loop.move_y(Ease.Linear, 0, 200, 1, 100)

    # sub-loops that I don't even know if they actually are a thing
    with loop.loop(10, 3) as sub_loop:
        sub_loop.move_y(Ease.Linear, 0, 200, 1, 100)

# perform the storyboard export (required)
# only parameter is output filename
Storyboard.export()
