from .constants import *

__author__ = 'Agka'


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

    @property
    def duration(self):
        return self.end_time - self.start_time

    @property
    def _time_shorthand(self):
        if self.start_time == self.end_time:
            return "{:.0f},".format(self.start_time)
        else:
            return "{:.0f},{:.0f}".format(self.start_time, self.end_time)

    @property
    def _1v_shorthand(self):
        if self.start_value == self.end_value:
            return "{}".format(_fmt(self.start_value))
        else:
            return "{},{}".format(_fmt(self.start_value), _fmt(self.end_value))

    @property
    def _2v_shorthand(self):
        for i, x in enumerate(self.start_value):
            if x is None:
                self.start_value[i] = self.end_value[i]
            if self.end_value[i] is None:
                self.end_value[i] = self.start_value[i]


        if self.start_value == self.end_value:
            return "{},{}".format(_fmt(self.start_value[0]), _fmt(self.start_value[1]))
        else:
            return "{},{},{},{}".format(_fmt(self.start_value[0]), _fmt(self.start_value[1]),
                                        _fmt(self.end_value[0]), _fmt(self.end_value[1]))

    @property
    def _3v_shorthand(self):
        if self.start_value == self.end_value:
            return "{},{},{}".format(_fmt(self.start_value[0]), _fmt(self.start_value[1]), _fmt(self.start_value[2]))
        else:
            return "{},{},{},{},{},{}".format(_fmt(self.start_value[0]),
                                              _fmt(self.start_value[1]),
                                              _fmt(self.start_value[2]),
                                              _fmt(self.end_value[0]),
                                              _fmt(self.end_value[1]),
                                              _fmt(self.end_value[2]))

    @property
    def _p_shorthand(self):
        if self.command == Command.FlipHorizontally:
            return 'H'
        elif self.command == Command.FlipVertically:
            return 'V'
        elif self.command == Command.MakeAdditive:
            return 'A'


    def _get_as_dictionary(self):
        cmd = self.command
        dic = {
            'cmd': Command.Shorthand[cmd],
            'ease': self.ease,
            'tsh': self._time_shorthand  # time shorthand
        }

        if cmd == Command.Fade:
            dic['vsh'] = self._1v_shorthand  # value shorthand
        elif cmd == Command.MoveX:
            dic['vsh'] = self._1v_shorthand  # value shorthand
        elif cmd == Command.MoveY:
            dic['vsh'] = self._1v_shorthand  # value shorthand
        elif cmd == Command.Scale:
            dic['vsh'] = self._1v_shorthand  # value shorthand
        elif cmd == Command.Rotate:
            dic['vsh'] = self._1v_shorthand
        elif cmd == Command.VectorScale:
            dic['vsh'] = self._2v_shorthand
        elif cmd == Command.Move:
            dic['vsh'] = self._2v_shorthand
        elif cmd == Command.Color:
            dic['vsh'] = self._3v_shorthand
        elif cmd == Command.FlipHorizontally:
            dic['vsh'] = self._p_shorthand
        elif cmd == Command.FlipVertically:
            dic['vsh'] = self._p_shorthand
        elif cmd == Command.MakeAdditive:
            dic['vsh'] = self._p_shorthand

        return dic

    def __str__(self):
        dic = self._get_as_dictionary()

        return "{cmd},{ease},{tsh},{vsh}".format(**dic)

class SpriteMultievent(object):
    def __init__(self, evt):
        self.start_time = evt.start_time
        self.duration = evt.end_time - evt.start_time
        self.event_type = Command.Shorthand[evt.command]
        self.values = []
        self.ease = evt.ease

        self.add_event(evt, True)

    def add_event(self, evt, include_start=False):
        if isinstance(evt.start_value, list):
            if include_start:
                self.values += [x for x in evt.start_value]

            self.values += [x for x in evt.end_value]
        else:
            if include_start:
                self.values.append(evt.start_value)

            self.values.append(evt.end_value)
        
        if any(x is None for x in self.values):
            print("event {}/{} of type {} has None values".format(evt.start_value, evt.end_value, evt.command))

    def __str__(self):
        return "{},{},{},{},{}".format(
            self.event_type,
            self.ease,
            self.start_time,
            self.start_time + self.duration,
            ",".join(str(round(x, 6)) for x in self.values)
        )


def create_event(command, **args):
    """
    Create an event with variable keywords and a type given by
    the Commands enumeration class.
    :param command: The command value as given by the Command class.
    :param args: Keywords.
    :return:
    """
    # print(args)
    evt = SpriteEvent(command)
    if 'start_time' in args:
        if args['start_time'] is not None:
            evt.start_time = args['start_time']
        else:
            evt.start_time = args['end_time']
    if 'end_time' in args:
        if 'duration' in args and args['duration']:
            evt.end_time = args['start_time'] + args['duration']
        else:
            if args['end_time'] is not None:
                evt.end_time = args['end_time']
            else:
                evt.end_time = args['start_time'] 
    else:
        evt.end_time = args['start_time']
    if 'ease' in args:
        evt.ease = args['ease'] or 0
    if 'start_value' in args:
        if args['start_value'] is not None:
            evt.start_value = args['start_value'] 
        else:
            evt.start_value = args['end_value']

    if 'end_value' in args:
        if args['end_value'] is not None:
            if not isinstance(args['end_value'], list):
                evt.end_value = args['end_value']
            else:
                evt.end_value = [x if x is not None else args['start_value'][i] for i, x in enumerate(args['end_value'])]
        else:
            evt.end_value = args['start_value']
    else:
        evt.end_value = args['start_value']

    assert(evt.start_time is not None)
    if isinstance(evt.end_time, list):
        assert(all(x is not None for x in evt.end_time))
    else:
        assert(evt.end_time is not None)
    assert(evt.start_value is not None)

    if isinstance(evt.end_value, list):
        assert(all(x is not None for x in evt.end_value))
    else:
        assert(evt.end_value is not None)

    return evt


# This function takes a list of events and joins them by duration.
def join_events(events):
    events_by_command = {
        cmd_type: [x for x in events if x.command == cmd_type] 
        for cmd_type in Command.CommandTypes
    }

    return_events = []

    for cmd_type, command_events in events_by_command.items():
        if not Command.is_reducible(cmd_type):
            return_events += command_events
            continue

        # group events by duration
        durations = {evt.duration for evt in command_events}
        events_by_duration = {dur: [x for x in command_events if x.duration == dur] for dur in durations if dur != 0}

        # group together those with chained end/start times
        for dur, evts in events_by_duration.items():
            sorted_events = sorted(evts, key=lambda x: x.start_time)

            while len(sorted_events) > 0:
                current_event = sorted_events[0]

                # Skip!
                #if current_event.start_time == current_event.end_time and \
                #   current_event.start_value == current_event.end_value:
                #   continue

                # put in this shorthand object
                current_event_group = SpriteMultievent(
                    current_event
                )

                # find all events that can be grouped with this one
                similar_events = [current_event]
                for evt in sorted_events[1:]:

                    # Does the current event smoothly transition from the last one?
                    if evt.start_time - current_event.end_time < 1 and \
                       evt.ease == current_event.ease and \
                       evt.start_value == current_event.end_value:
                       similar_events.append(evt)

                       current_event = evt
                       continue

                    # no more events can be chained to this one (performance condition)
                    if int(evt.start_time) > int(current_event.end_time):
                        break 


                # remove the grouped events. we are lucky that order is preserved!
                sorted_events = [x for x in sorted_events if x not in similar_events]

                for evt in similar_events:
                    current_event_group.add_event(evt)

                return_events.append(current_event_group)
    
    return return_events
    


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

    def move(self, _ease=0,
             _st=0, _et=None,
             _sx=0, _sy=0,
             _ex=None, _ey=None,
             _dur=None):
        """
        Move from point A to point B.
         :param _ease: Easing.
         :param _st: Start time.
         :param _et: End time.
         :param _sx: Start X.
         :param _sy: Start Y.
         :param _ex: End X.
         :param _ey: End Y.
         :param _dur: If _et is not set but _dur is, _et is _st + dur. Else, it's _st.
         :return:
        """
        self.add_event(create_event(Command.Move,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=[_sx, _sy],
                                    end_value=[_ex, _ey],
                                    duration=_dur))
        return self

    def move_x(self, _ease=0, _st=None, _et=None, _sx=None, _ex=None, _dur=None):
        """
        Move across the X axis.
         :param _ease: Easing.
         :param _st: Start time.
         :param _et: End time.
         :param _sx: Start X value.
         :param _ex: End X value.
         :param _dur: If _et is not set but _dur is, _et is _st + dur. Else, it's _st.
         :return:
        """
        self.add_event(create_event(Command.MoveX,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=_sx,
                                    end_value=_ex,
                                    duration=_dur))
        return self

    def move_y(self, _ease=0, _st=0, _et=None, _sy=0, _ey=None, _dur=None):
        """
        Move across the Y axis.
         :param _ease: Easing.
         :param _st: Start Time.
         :param _et: End Time.
         :param _sy: Start Y value.
         :param _ey: End Y value.
         :param _dur: If _et is not set but _dur is, _et is _st + dur. Else, it's _st.
         :return: self
        """
        self.add_event(create_event(Command.MoveY,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=_sy,
                                    end_value=_ey,
                                    duration=_dur))
        return self

    def scale(self, _ease=0, _st=0, _et=None, _ss=1, _es=1, _dur=None):
        """
        Simultaneous axis scaling. Grow X and Y by a factor.
         :param _ease: Easing.
         :param _st: Start time.
         :param _et: End time.
         :param _ss: Start scale.
         :param _es: End scale.
         :param _dur: If _et is not set but _dur is, _et is _st + dur. Else, it's _st.
         :return: self
        """
        self.add_event(create_event(Command.Scale,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=_ss,
                                    end_value=_es,
                                    duration=_dur))
        return self

    def vector_scale(self, _ease=0,
                     _st=0, _et=None,
                     _sx=1, _sy=1,
                     _ex=None, _ey=None,
                     _dur=None):
        """
        Vector scaling. Independently grow X and Y axis by a factor of the original size.
         :param _ease: Easing.
         :param _st: Start time.
         :param _et: End time.
         :param _sx: Start X value.
         :param _sy: Start Y value.
         :param _ex: End X value.
         :param _ey: End Y value.
         :param _dur: If _et is not set but _dur is, _et is _st + dur. Else, it's _st.
        :return: self
        """
        self.add_event(create_event(Command.VectorScale,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=[_sx, _sy],
                                    end_value=[_ex, _ey],
                                    duration=_dur))
        return self

    def fade(self, _ease=0, _st=0, _et=None, _sv=1, _ev=None, _dur=None):
        """
        Fade from a value to another value (0 being fully transparent, 1 fully opaque)
         :param _ease: Easing.
         :param _st: Start time.
         :param _et: End time.
         :param _sv: Start fade value.
         :param _ev: End fade value.
         :param _dur: If _et is not set but _dur is, _et is _st + dur. Else, it's _st.
         :return: self
        """
        self.add_event(create_event(Command.Fade,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=_sv,
                                    end_value=_ev,
                                    duration=_dur))
        return self

    def rotate(self, _ease=0, _st=None, _et=None, _sr=None, _er=None, _dur=None):
        """
        Rotate from a value to another value in radians.
         :param _ease: Easing.
         :param _st: Start time.
         :param _et: End time.
         :param _sr: Start rotation value.
         :param _er: End rotation value.
         :param _dur: If _et is not set but _dur is, _et is _st + dur. Else, it's _st.
         :return:
        """

        self.add_event(create_event(Command.Rotate,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=_sr,
                                    end_value=_er,
                                    duration=_dur))
        return self

    def colour(self, _ease=0,
               _st=None, _et=None,
               _sr=None, _sg=None, _sb=None,
               _er=None, _eg=None, _eb=None,
               _dur=None):
        """
        Same as color().
        """
        if _er is None:
            _er = _sr
        if _eg is None:
            _eg = _sg
        if _eb is None:
            _eb = _sb

        self.add_event(create_event(Command.Color,
                                    ease=_ease,
                                    start_time=_st,
                                    end_time=_et,
                                    start_value=[_sr, _sg, _sb],
                                    end_value=[_er, _eg, _eb],
                                    duration=_dur))
        return self

    def color(self, _ease=0,
              _st=None, _et=None,
              _sr=None, _sg=None, _sb=None,
              _er=None, _eg=None, _eb=None,
              _dur=None):
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
         :param _dur: If _et is not set but _dur is, _et is _st + dur. Else, it's _st.
         :return: self
        """
        self.colour(_ease, _st, _et, _sr, _sg, _sb, _er, _eg, _eb, _dur)
        return self

    def flip_horizontally(self, _st=None, _et=None):
        """
        Flip sprite horizontally for a specific duration.
         :param _st: Start time.
         :param _et: End time.
         :return: self
        """
        self.add_event(create_event(Command.FlipVertically, start_time=_st, end_time=_et))
        self.add_event(create_event(Command.FlipHorizontally, start_time=_st, end_time=_et))
        return self

    def flip_vertically(self, _st=None, _et=None, _dur=None):
        """
        Flip sprite vertically for a specific duration.
         :param _st: Start time.
         :param _et: End time.
         :param _dur: If _et is not set but _dur is, _et is _st + dur. Else, it's _st.
         :return: self
        """
        self.add_event(create_event(Command.FlipVertically,
                                    start_time=_st, end_time=_et,
                                    duration=_dur))
        return self

    def additive(self, _st=None, _et=None, _dur=None):
        """
        Set additive mode for a specific duration.
         :param _st: Start time.
         :param _et: End time.
         :param _dur: If _et is not set but _dur is, _et is _st + dur. Else, it's _st.
         :return: self
        """
        self.add_event(create_event(Command.MakeAdditive,
                                    start_time=_st, end_time=_et,
                                    duration=_dur))
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
        events_joined = join_events(self._events)
        return "\n".join(["\n".join(map(lambda x: "_" + x, str(x).split("\n"))) for x in events_joined])
        # return "\n".join(["\n".join(map(lambda x: "_" + x, str(x).split("\n"))) for x in self._events])


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

class TemporalSprite(Sprite):
    def __init__(self, layer=Layer.Background, origin=Origin.TopLeft, file="", location=(0, 0)):
        super().__init__(layer, origin, file, location)
        self.active_periods = []

    def add_active_period(self, period):
        self.active_periods.append(period)
    
    def is_active_at(self, t_start, t_end):
        for x in self.active_periods:
            if not (t_end <= x[0] or  # "not outside of the segment"
                   t_start >= x[1]):
                return True
        
        return False

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
