__author__ = 'Agka'


class PlayingField(object):
    WIDTH = 512
    HEIGHT = 384


class HitObject(object):
    """
    The HitObject class is a base to all the other objects.
    It contains constants and functions common to all objects.
    """
    CIRCLE = 1
    SLIDER = 2
    NEW_COMBO = 4
    SPINNER = 8
    NEW_COMBO_2 = 16
    NEW_COMBO_3 = 32
    NEW_COMBO_4 = 64
    HOLD = 128

    SND_NORMAL = 0
    SND_WHISTLE = 1
    SND_FINISH = 2
    SND_CLAP = 4

    SOUND_TYPES = [SND_NORMAL, SND_WHISTLE, SND_FINISH, SND_CLAP]

    # 4, 8, 16, 32, 64 = New Combo as well. (from aibat)
    COMBO_MASK = 4 | 8 | 16 | 32 | 64

    def __init__(self, x, y, time, hitsound):
        self.x = x
        """
            The x coordinate of the hitobject.
        """
        self.y = y
        """
            The y coordinate of the hitobject.
        """
        self.time = float(time)
        """
            The time, in milliseconds at which the hitobject is located.
        """
        self.hitsound = hitsound
        """
            The numerical value of the hitsound this object is using.
        """
        self.sample_set = 0
        """
            The numerical value of the sample set of this object.
        """
        self.addition_set = 0
        """
            The numerical value of the additional hitsound of this object.
        """
        self.custom_set = 0
        """
            The index of the sample set currently in use.
        """
        self.volume = 0
        """
            The volume of this object, as osu measures it.
        """

        self.custom_sample = ""
        """
            The sample to play when this object is hit.
            If not empty, overrides sample_set, addition and custom_set to 0.
        """

    def _tuple(self):
        return (self.x, self.y,
             self.time,
             self.hitsound,
             self.sample_set,
             self.addition_set,
             self.custom_set,
             self.volume,
             self.custom_sample)

    def __hash__(self):
        return hash(self._tuple())

    def __eq__(self, other):
        if type(other) is not HitObject:
            return
        return self._tuple() == other._tuple()

    def __ne__(self, other):
        return not self.__eq__(other)

    def set_addition(self, add_dt):
        """
        Set the addition data from the array resulting of splitting the
        entry describing sampleset, addition, custom set, volume and sample of this hitsound.
        :param add_dt: The split entry.
        :return:
        """
        self.sample_set = add_dt[0] if len(add_dt) > 0 else 0
        self.addition_set = add_dt[1] if len(add_dt) > 1 else 0
        self.custom_set = add_dt[2] if len(add_dt) > 2 else 0
        self.volume = add_dt[3] if len(add_dt) > 3 else 0
        self.custom_sample = add_dt[4] if len(add_dt) > 4 else ""

    def get_additive_str(self):
        """
        Get the string for the additive hitsound data.
        :return: A string in the x:x:x:x: format.
        """
        if len(self.custom_sample) > 0:
            s = "0:0:0:{}:{}".format(self.volume, self.custom_sample)
        else:
            s = "{}:{}:{}:{}:".format(self.sample_set,
                                      self.addition_set,
                                      self.custom_set,
                                      self.volume)
        return s

    def __str__(self):
        """
        Generate the string representation of this object.
        :return: A x,y,time and so on representation of this hitobject.
        """
        return "{},{},{},{},{},{}".format(self.x,
                                          self.y,
                                          int(self.time),
                                          self.type,
                                          self.hitsound,
                                          self.get_additive_str())

    @staticmethod
    def from_string(string):
        """
        Create a hitobject of the correct class from a line of the [HitObjects] section of a .osu file.
        :param string: The line of the [HitObjects] section.
        :return: A derivative class of HitObject from this string.
        """
        entries = string.split(",")
        try:
            val = int(entries[3])  # hitobject kind
            info = list(map(int, entries[:5]))  # information applied to all objects

            # remove what corresponds to val
            info = info[:3] + [info[4]]

            if val & HitObject.CIRCLE:
                ret = HitCircle(*info)
            elif val & HitObject.SLIDER:
                ret = Slider(*info)
            elif val & HitObject.SPINNER:
                ret = Spinner(*info)
            elif val & HitObject.HOLD:
                ret = Hold(*info)
            else:
                raise ValueError("Invalid object type ({})".format(val))

            # manually added the type
            ret.type = val
            ret.set_data(entries)
            return ret
        except Exception as e:
            raise ValueError("Invalid object string: {}. Exception: {}".format(string, e))

    def reset_hitsound(self):
        self.hitsound = 0
        self.addition_set = 0
        self.custom_sample = ""
        self.custom_set = 0
        self.sample_set = 0


def default_int(s):
    try:
        return int(s)
    except:
        return s


class HitCircle(HitObject):
    def __init__(self, x, y, time, hitsound):
        HitObject.__init__(self, x, y, time, hitsound)
        self.type = HitObject.CIRCLE

    def set_data(self, data):
        self.set_addition(list(map(default_int, data[5].split(":"))))


class Slider(HitObject):
    def __init__(self, x, y, time, hitsound):
        HitObject.__init__(self, x, y, time, hitsound)
        self.repeat = 1
        """
            The amount of times the slider repeats itself.
        """
        self.points = []
        """
            A list of dictionaries containing the keys 'x' and 'y' containing the point's coordinates.
        """
        self.type = "P"
        """
            The slider type. Follows the .osu representation.
        """
        self.pixel_length = 140
        """
            The playfield-relative length of this slider.
        """
        self.edge_hitsound = 0
        """
            The numerical value of the hitsound to play at an edge.
        """
        self.edge_addition = 0
        """
            The numerical value of the additional hitsound to play at an edge.
        """

        self.type = HitObject.SLIDER

    def set_data(self, data):
        if len(data) > 6:
            self.repeat = int(data[6])

        if len(data) > 7:
            self.pixel_length = float(data[7])

        if len(data) > 8:
            self.edge_hitsound = int(data[8])

        if len(data) > 9:
            self.edge_addition = int(data[9])

        if len(data) > 10:
            self.set_addition(list(map(default_int, data[10].split(":"))))

        if len(data) > 5:
            point_data = data[5].split("|")
            self.type = point_data[0]
            for x in point_data[1:]:
                point = list(map(default_int, x.split(":")))
                self.points.append({"x": point[0], "y": point[1]})

    def __str__(self):
        raise NotImplementedError()


class Spinner(HitObject):
    def __init__(self, x, y, time, hitsound):
        HitObject.__init__(self, x, y, time, hitsound)
        self.end_time = time
        """
            The time at which this spinner ends.
        """
        self.type = HitObject.SPINNER

    def set_data(self, data):
        self.end_time = data[5]
        self.set_addition(list(map(default_int, data[6].split(":"))))


class Hold(HitObject):
    def __init__(self, x, y, time, hitsound):
        HitObject.__init__(self, x, y, time, hitsound)
        self.end_time = time
        """
            The time at which this hold should be released.
        """
        self.type = HitObject.HOLD

    def set_data(self, data):
        hs_data = list(map(default_int, data[5].split(":")))
        self.end_time = int(hs_data[0])
        self.set_addition(hs_data[1:])

    def get_additive_str(self):
        return "{}:".format(self.end_time) + HitObject.get_additive_str(self)

    @property
    def duration(self):
        """
        Get the duration of this hold.
        :return: The duration of this hold, in milliseconds.
        """
        return self.end_time - self.time
