__author__ = 'Agka'

from .constants import *

# This function formats decimal storyboard values up to 3 decimals, removing
# any pointless 0s and periods.
def _fmt(val):
    return "{:.3f}".format(float(val)).rstrip("0").rstrip(".")

class Storyboard(object):
    """
    Singleton instance of storyboard.
    You can't make more than one storyboard per script
    for the convenience of being able to not have to specify
    what storyboard to add a sprite to.
    """

    _sprites = []

    @staticmethod
    def add_sprite(sprite):
        """
        Add a sprite to the storyboard instance.
         :param sprite: Storyboard sprite to add.
        """
        Storyboard._sprites.append(sprite)

    @staticmethod
    def export(filename="output.osb"):
        """
        Export the storyboard to a file.
         :param filename: File to export the storyboard to. By default it is 'output.osb'
        """
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
        if cmd == Command.Fade:
            dic = {'ease': self.ease,
                   'start_time': self.start_time,
                   'end_time': self.end_time,
                   'sv': _fmt(self.start_value),
                   'ev': _fmt(self.end_value)}
            return "F,{ease},{start_time:.0f},{end_time:.0f},{sv},{ev}".format(**dic)
        if cmd == Command.Move:
            dic = {'ease': self.ease,
                   'start_time': self.start_time,
                   'end_time': self.end_time,
                   'sx': _fmt(self.start_value[0]),
                   'sy': _fmt(self.start_value[1]),
                   'ex': _fmt(self.end_value[0]),
                   'ey': _fmt(self.end_value[1])}
            return "M,{ease},{start_time:.0f},{end_time:.0f},{sx},{sy},{ex},{ey}".format(**dic)
        elif cmd == Command.MoveX:
            dic = {'ease': self.ease,
                   'start_time': self.start_time,
                   'end_time': self.end_time,
                   'sx': _fmt(self.start_value),
                   'ex': _fmt(self.end_value)}

            return "MX,{ease},{start_time:.0f},{end_time:.0f},{sx},{ex}".format(**dic)
        elif cmd == Command.MoveY:
            dic = {'ease': self.ease,
                   'start_time': self.start_time,
                   'end_time': self.end_time,
                   'sy': _fmt(self.start_value),
                   'ey': _fmt(self.end_value)}

            return "MY,{ease},{start_time:.0f},{end_time:.0f},{sy},{ey}".format(**dic)
        elif cmd == Command.Scale:
            dic = {'ease': self.ease,
                   'start_time': self.start_time,
                   'end_time': self.end_time,
                   'sv': _fmt(self.start_value),
                   'ev': _fmt(self.end_value)}
            return "S,{ease},{start_time:.0f},{end_time:.0f},{sv},{ev}".format(**dic)
        elif cmd == Command.VectorScale:
            dic = {'ease': self.ease,
                   'start_time': self.start_time,
                   'end_time': self.end_time,
                   'sx': _fmt(self.start_value[0]),
                   'sy': _fmt(self.start_value[1]),
                   'ex': _fmt(self.end_value[0]),
                   'ey': _fmt(self.end_value[1])}
            return "V,{ease},{start_time:.0f},{end_time:.0f},{sx},{sy},{ex},{ey}".format(**dic)
        elif cmd == Command.Rotate:
            dic = {'ease': self.ease,
                   'start_time': self.start_time,
                   'end_time': self.end_time,
                   'sv': _fmt(self.start_value),
                   'ev': _fmt(self.end_value)}
            return "R,{ease},{start_time:.0f},{end_time:.0f},{sv},{ev}".format(**dic)
        elif cmd == Command.Color:
            dic = {'ease': self.ease,
                   'start_time': self.start_time,
                   'end_time': self.end_time,
                   'sr': self.start_value[0], 'sg': self.start_value[1], 'sb': self.start_value[2],
                   'er': self.end_value[0], 'er': self.end_value[1], 'eb': self.end_value[2]}
            return "C,{ease},{start_time:.0f},{end_time:.0f},{sr:.0f},{sg:.0f},{sb:.0f},{er:.0f},{eg:.0f},{eb:.0f}" \
                .format(**dic)
        elif cmd == Command.FlipHorizontally:
            dic = {'ease': self.ease,
                   'start_time': self.start_time,
                   'end_time': self.end_time}
            return "P,{ease},{start_time:.0f},{end_time:.0f},H".format(**dic)
        elif cmd == Command.FlipVertically:
            dic = {'ease': self.ease,
                   'start_time': self.start_time,
                   'end_time': self.end_time}
            return "P,{ease},{start_time:.0f},{end_time:.0f},V".format(**dic)
        elif cmd == Command.MakeAdditive:
            dic = {'ease': self.ease,
                   'start_time': self.start_time,
                   'end_time': self.end_time}
            return "P,{ease},{start_time:.0f},{end_time:.0f},A".format(**dic)


def create_event(command, **args):
    """
    Create an event with variable keywords and a type given by
    the Commands enumeration class.
    :param command: The command value as given by the Command class.
    :param args: Keywords.
    :return:
    """
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
        """
        Add an event outputted by create_event.
         :param event: Event to add.
         :return: None
        """
        self._events.append(event)

    def move(self, _ease, _st, _et, _sx, _sy, _ex, _ey):
        """
        Move from point A to point B.
         :param _ease: Easing.
         :param _st: Start time.
         :param _et: End time.
         :param _sx: Start X.
         :param _sy: Start Y.
         :param _ex: End X.
         :param _ey: End Y.
         :return:
        """
        self.add_event(create_event(Command.Move,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=[_sx, _sy],
                                    end_value=[_ex, _ey]))
        return self

    def move_x(self, _ease, _st, _et, _sx, _ex):
        """
        Move across the X axis.
         :param _ease: Easing.
         :param _st: Start time.
         :param _et: End time.
         :param _sx: Start X value.
         :param _ex: End X value.
         :return:
        """
        self.add_event(create_event(Command.MoveX,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=_sx,
                                    end_value=_ex))
        return self

    def move_y(self, _ease, _st, _et, _sy, _ey):
        """
        Move across the Y axis.
         :param _ease: Easing.
         :param _st: Start Time.
         :param _et: End Time.
         :param _sy: Start Y value.
         :param _ey: End Y value.
         :return: self
        """
        self.add_event(create_event(Command.MoveY,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=_sy,
                                    end_value=_ey))
        return self

    def scale(self, _ease, _st, _et, _ss, _es):
        """
        Simultaneous axis scaling. Grow X and Y by a factor.
         :param _ease: Easing.
         :param _st: Start time.
         :param _et: End time.
         :param _ss: Start scale.
         :param _es: End scale.
         :return: self
        """
        self.add_event(create_event(Command.Scale,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=_ss,
                                    end_value=_es))
        return self

    def vector_scale(self, _ease, _st, _et, _sx, _sy, _ex, _ey):
        """
        Vector scaling. Independently grow X and Y axis by a factor of the original size.
         :param _ease: Easing.
         :param _st: Start time.
         :param _et: End time.
         :param _sx: Start X value.
         :param _sy: Start Y value.
         :param _ex: End X value.
         :param _ey: End Y value.
        :return: self
        """
        self.add_event(create_event(Command.VectorScale,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=[_sx, _sy],
                                    end_value=[_ex, _ey]))
        return self

    def fade(self, _ease, _st, _et, _sv, _ev):
        """
        Fade from a value to another value (0 being fully transparent, 1 fully opaque)
         :param _ease: Easing.
         :param _st: Start time.
         :param _et: End time.
         :param _sv: Start fade value.
         :param _ev: End fade value.
         :return: self
        """
        self.add_event(create_event(Command.Fade,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=_sv,
                                    end_value=_ev))
        return self

    def rotate(self, _ease, _st, _et, _sr, _er):
        """
        Rotate from a value to another value in radians.
         :param _ease: Easing.
         :param _st: Start time.
         :param _et: End time.
         param _sr: Start rotation value.
         :param _er: End rotation value.
         :return:
        """

        self.add_event(create_event(Command.Rotate,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=_sr,
                                    end_value=_er))
        return self

    def colour(self, _ease, _st, _et, _sr, _sg, _sb, _er, _eg, _eb):
        """
        Same as color().
        """
        self.add_event(create_event(Command.Color,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=[_sr, _sg, _sb],
                                    end_value=[_er, _eg, _eb]))
        return self

    def color(self, _ease, _st, _et, _sr, _sg, _sb, _er, _eg, _eb):
        """
        Colorize from one RGB to a second RGB
         :param _ease: Easing.
         :param _st: Start time.
         :param _et: End time.
         :param _sr: Start red value.
         :param _sg: Start green value.
         :param _sb: Start blue value.
         :param _er: End red value.
         :param _eg: End green value.
         :param _eb: End blue value.
         :return: self
        """
        self.colour(_ease, _st, _et, _sr, _sg, _sb, _er, _eg, _eb)
        return self

    def flip_horizontally(self, _st, _et):
        """
        Flip sprite horizontally for a specific duration.
         :param _st: Start time.
         :param _et: End time.
         :return: self
        """
        self.add_event(create_event(Command.FlipVertically, start_time=_st, end_time=_et))
        self.add_event(create_event(Command.FlipHorizontally, start_time=_st, end_time=_et))
        return self

    def flip_vertically(self, _st, _et):
        """
        Flip sprite vertically for a specific duration.
         :param _st: Start time.
         :param _et: End time.
         :return: self
        """
        self.add_event(create_event(Command.FlipVertically, start_time=_st, end_time=_et))
        return self

    def additive(self, _st, _et):
        """
        Set additive mode for a specific duration.
         :param _st: Start time.
         :param _et: End time.
         :return: self
        """
        self.add_event(create_event(Command.MakeAdditive, start_time=_st, end_time=_et))
        return self

    def loop(self, _st, _lc):
        """
        Create a loop object.
         :param _st: Start time.
         :param _lc: Loop count.
         :return: A SpriteEventLoop event chained to this object.
        """
        return_loop = SpriteEventLoop(_st, _lc)
        self.add_event(return_loop)
        return return_loop

    def join_sub_events(self):
        return "\n".join(["\n".join(map(lambda x: "_" + x, str(x).split("\n"))) for x in self._events])

class SpriteEventLoop(CommandList):
    """
    Loop events. Transforms parent sprite a number of times from a time.
    Every loop's duration is the furthest end point of the events it contains.
    """
    def __init__(self, start_time=0, loops=1):
        CommandList.__init__(self)
        self.start_time = start_time
        self.loops = loops

    def __str__(self):
        dic = {'st': self.start_time, "lc": self.loops}
        return "L,{st},{lc}\n".format(**dic) + self.join_sub_events()

    # Have a couple empty functions so we can allow the with sprite.loop() as l idiom
    def __enter__(self):
        return self

    def __exit__(self, t, v, tb):
        pass

class Sprite(CommandList):
    def __init__(self, layer=Layer.Background, origin=Origin.TopLeft, file="", location=(0, 0)):
        """
A sprite with only the raw osu! commands.
:param layer: Layer where to place it.
:param origin: Location to use as pivot.
:param file: File to use for sprite.
:param location: Initial location.
:return:
        """
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
        events = self.join_sub_events()
        return 'Sprite,{layer},{origin},"{file}",{sx:.0f},{sy:.0f}\n'.format(**dic) + events

class ExtSprite(Sprite):
    def __init__(self, layer=Layer.Background, origin=Origin.TopLeft, file="", location=(0, 0)):
        """
A Sprite with more built-ins to play with than the standard commands.
 :param layer: Layer where to place it.
 :param origin: Location to use as pivot.
 :param file: File to use for sprite.
 :param location: Initial location.
 :return:
        """
        # A sprite, except with more stuff.
        Sprite.__init__(self, layer, origin, file, location)

    def display(self, start_time, end_time):
        self.fade(Ease.Linear, start_time, end_time, 1, 1)

class Sample(object):
    def __init__(self, time, layer, file, volume):
        """
An audio sample to play.
 :param time:  When to play it.
 :param layer: Play only on fail, pass, or always (bg/fg)
 :param file: Audio file to play.
 :param volume: Volume (0 to 100) to play the sound with.
 :return:
        """
        Storyboard.add_sprite(self)
        self.file = file
        self.time = time
        self.layer = layer
        self.volume = volume

    def __str__(self):
        return 'Sample,{time},{layer},"{file}",volume'.format(time=self.time,
                                                              layer=self.layer,
                                                              file=self.file,
                                                              volume=self.volume)
