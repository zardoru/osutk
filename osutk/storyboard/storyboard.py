__author__ = 'Agka'

from .constants import *


class Storyboard(object):
    _sprites = []

    @staticmethod
    def add_sprite(sprite):
        Storyboard._sprites.append(sprite)

    @staticmethod
    def export(filename="output.osb"):
        with open(filename, "w") as out:
            background_sprites = list(filter(lambda obj: obj.layer == Layer.Background, Storyboard._sprites))
            pass_sprites = list(filter(lambda obj: obj.layer == Layer.Pass, Storyboard._sprites))
            fail_sprites = list(filter(lambda obj: obj.layer == Layer.Fail, Storyboard._sprites))
            fg_sprites = list(filter(lambda obj: obj.layer == Layer.Foreground, Storyboard._sprites))

            bg_out = "//Storyboard Layer 0 (Background)"
            if len(background_sprites):
                bg_out += "\n" + "\n".join(str(x) for x in background_sprites)

            fail_out = "//Storyboard Layer 1 (Fail)"
            if len(fail_sprites):
                fail_out += "\n" + "\n".join(str(x) for x in fail_sprites)

            pass_out = "//Storyboard Layer 2 (Pass)"
            if len(pass_sprites):
                pass_out += "\n" + "\n".join(str(x) for x in pass_sprites)

            fg_out = "//Storyboard Layer 3 (Foreground)"
            if len(fg_sprites):
                fg_out += "\n" + "\n".join(str(x) for x in fg_sprites)

            output = "[Events]\n//Background and Video events\n" + "\n".join([bg_out, fail_out, pass_out, fg_out])
            print(output, file=out)
            pass


class SpriteEvent(object):
    def __init__(self, command):
        self.command = command

        # How many of these are valid depend on the command.
        self.start_time = 0
        self.end_time = 0
        self.start_value = 0
        self.end_value = 0
        self.ease = Ease.Linear

    def __str__(self):
        cmd = self.command
        if cmd == Command.Move:
            dic = {'ease': self.ease,
                   'start_time': self.start_time,
                   'end_time': self.end_time,
                   'sx': self.start_value[0],
                   'sy': self.start_value[1],
                   'ex': self.end_value[0],
                   'ey': self.end_value[1]}
            return "M,{ease},{start_time},{end_time},{sx},{sy},{ex},{ey}".format(**dic)
        elif cmd == Command.MoveX:
            dic = {'ease': self.ease,
                   'start_time': self.start_time,
                   'end_time': self.end_time,
                   'sx': self.start_value,
                   'ex': self.end_value}

            return "MX,{ease},{start_time},{end_time},{sx},{ex}".format(**dic)
        elif cmd == Command.MoveY:
            dic = {'ease': self.ease,
                   'start_time': self.start_time,
                   'end_time': self.end_time,
                   'sy': self.start_value,
                   'ey': self.end_value}

            return "MY,{ease},{start_time},{end_time},{sy},{ey}".format(**dic)
        elif cmd == Command.Scale:
            dic = {'ease': self.ease,
                   'start_time': self.start_time,
                   'end_time': self.end_time,
                   'sv': self.start_value,
                   'ev': self.end_value}
            return "S,{ease},{start_time},{end_time},{sv},{ev}".format(**dic)
        elif cmd == Command.VectorScale:
            dic = {'ease': self.ease,
                   'start_time': self.start_time,
                   'end_time': self.end_time,
                   'sx': self.start_value[0],
                   'sy': self.start_value[1],
                   'ex': self.end_value[0],
                   'ey': self.end_value[1]}
            return "V,{ease},{start_time},{end_time},{sx},{sy},{ex},{ey}".format(**dic)
        elif cmd == Command.Rotate:
            dic = {'ease': self.ease,
                   'start_time': self.start_time,
                   'end_time': self.end_time,
                   'sv': self.start_value,
                   'ev': self.end_value}
            return "R,{ease},{start_time},{end_time},{sv},{ev}".format(**dic)
        elif cmd == Command.Color:
            dic = {'ease': self.ease,
                   'start_time': self.start_time,
                   'end_time': self.end_time,
                   'sr': self.start_value[0], 'sg': self.start_value[1], 'sb': self.start_value[2],
                   'er': self.end_value[0], 'er': self.end_value[1], 'eb': self.end_value[2]}
            return "C,{ease},{start_time},{end_time},{sr},{sg},{sb},{er},{eg},{eb}".format(**dic)
        elif cmd == Command.FlipHorizontally:
            dic = {'ease': self.ease,
                   'start_time': self.start_time,
                   'end_time': self.end_time}
            return "P,{ease},{start_time},{end_time},H".format(**dic)
        elif cmd == Command.FlipVertically:
            dic = {'ease': self.ease,
                   'start_time': self.start_time,
                   'end_time': self.end_time}
            return "P,{ease},{start_time},{end_time},V".format(**dic)
        elif cmd == Command.MakeAdditive:
            dic = {'ease': self.ease,
                   'start_time': self.start_time,
                   'end_time': self.end_time}
            return "P,{ease},{start_time},{end_time},A".format(**dic)


def create_event(command, **args):
    evt = SpriteEvent(command)
    if 'start_time' in args:
        evt.start_time = args['start_time']
    if 'end_time' in args:
        evt.end_time = args['end_time']
    if 'ease' in args:
        evt.ease = args['ease']
    if 'start_value' in args:
        evt.start_value = args['start_value']
    if 'end_value' in args:
        evt.end_value = args['end_value']
    return evt


class CommandList(object):
    def __init__(self):
        self._events = []

    def add_event(self, event):
        self._events.append(event)

    def move(self, _ease, _st, _et, _sx, _sy, _ex, _ey):
        self.add_event(create_event(Command.Move,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=[_sx, _sy],
                                    end_value=[_ex, _ey]))
        return self

    def move_x(self, _ease, _st, _et, _sx, _ex):
        self.add_event(create_event(Command.MoveX,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=_sx,
                                    end_value=_ex))
        return self

    def move_y(self, _ease, _st, _et, _sy, _ey):
        self.add_event(create_event(Command.MoveY,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=_sy,
                                    end_value=_ey))
        return self

    def scale(self, _ease, _st, _et, _ss, _es):
        self.add_event(create_event(Command.Scale,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=_ss,
                                    end_value=_es))
        return self

    def vector_scale(self, _ease, _st, _et, _sx, _sy, _ex, _ey):
        self.add_event(create_event(Command.VectorScale,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=[_sx, _sy],
                                    end_value=[_ex, _ey]))
        return self

    def rotate(self, _ease, _st, _et, _sr, _er):
        self.add_event(create_event(Command.Rotate,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=_sr,
                                    end_value=_er))
        return self

    def colour(self, _ease, _st, _et, _sr, _sg, _sb, _er, _eg, _eb):
        self.add_event(create_event(Command.Color,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=[_sr, _sg, _sb],
                                    end_value=[_er, _eg, _eb]))
        return self

    def color(self, _ease, _st, _et, _sr, _sg, _sb, _er, _eg, _eb):
        self.colour(_ease, _st, _et, _sr, _sg, _sb, _er, _eg, _eb)
        return self

    def flip_horizontally(self, _st, _et):
        self.add_event(create_event(Command.FlipHorizontally, start_time=_st, end_time=_et))
        return self

    def flip_vertically(self, _st, _et):
        self.add_event(create_event(Command.FlipVertically, start_time=_st, end_time=_et))
        return self

    def additive(self, _st, _et):
        self.add_event(create_event(Command.MakeAdditive, start_time=_st, end_time=_et))
        return self

    def loop(self, _st, _lc):
        return_loop = SpriteEventLoop(_st, _lc)
        self.add_event(return_loop)
        return return_loop


class SpriteEventLoop(CommandList):
    def __init__(self, start_time=0, loops=1):
        CommandList.__init__(self)
        self.start_time = start_time
        self.loops = loops

    def __str__(self):
        dic = {'st': self.start_time, "lc": self.loops}
        return "L,{st},{lc}\n".format(**dic) + "\n".join("__" + str(x) for x in self._events)


class Sprite(CommandList):
    def __init__(self, layer=Layer.Background, origin=Origin.TopLeft, file="", location=[0, 0]):
        CommandList.__init__(self)

        if file == "":
            raise ValueError("The sprite's file can't be empty!")

        self.file = file
        self.location = location
        self.origin = origin
        self.layer = layer
        Storyboard.add_sprite(self)

    def __str__(self):
        dic = {'layer': self.layer,
               'origin': self.origin,
               'file': self.file,
               'sx': self.location[0],
               'sy': self.location[1]}
        return 'Sprite,{layer},{origin},"{file}",{sx},{sy}\n'.format(**dic) + \
               "\n".join(["_" + str(x) for x in self._events])


class Sample(object):
    def __init__(self, time, layer, file, volume):
        self.file = file
        self.time = time
        self.layer = layer
        self.volume = volume

    def __str__(self):
        return 'Sample,{time},{layer},"{file}",volume'.format(time=self.time,
                                                              layer=self.layer,
                                                              file=self.file,
                                                              volume=self.volume)
