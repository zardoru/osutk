__author__ = 'Agka'

from osutk.storyboard import *

s = Sprite(file="Welcome.png", location=[Screen.Width / 2, Screen.Height / 2], origin=Origin.Center)

s.move(Ease.Linear, 0, 1000, 0, 100, 0, 100)
s.flip_horizontally(1000, 2000)

l = Sprite(file="lol.png")

l.loop(0, 10).scale(Ease.In, 0, 500, 1, 0.5).move_x(Ease.Linear, 500, 1000, 200, 400)

with s.loop(0, 3) as sl:
    sl.move_x(Ease.Linear, 0, 200, 0, 100)

Storyboard.export()
