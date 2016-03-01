__author__ = 'Agka'


class PlayingField(object):
    WIDTH = 512
    HEIGHT = 384


class HitObject(object):
    CIRCLE = 1
    SLIDER = 2
    NEW_COMBO = 4
    SPINNER = 8
    NEW_COMBO_2 = 16
    NEW_COMBO_3 = 32
    NEW_COMBO_4 = 64
    HOLD = 128

    # 4, 8, 16, 32, 64 = New Combo as well. (from aibat)
    COMBO_MASK = 4 | 8 | 16 | 32 | 64

    def __init__(self, x, y, time, hitsound):
        self.x = x
        self.y = y
        self.time = time
        self.hitsound = hitsound
        self.sample_set = 0
        self.addition = 0
        self.custom_set = 0
        self.volume = 0
        self.custom_sample = ""

    def set_addition(self, add_dt):
        self.sample_set = add_dt[0] if len(add_dt) > 0 else 0
        self.addition = add_dt[1] if len(add_dt) > 1 else 0
        self.custom_set = add_dt[2] if len(add_dt) > 2 else 0
        self.volume = add_dt[3] if len(add_dt) > 3 else 0
        self.custom_sample = add_dt[4] if len(add_dt) > 4 else ""

    def get_additive_str(self):
        if len(self.custom_sample) > 0:
            s = "0:0:0:{}:{}".format(self.volume, self.custom_sample)
        else:
            s = "{}:{}:{}:{}:".format(self.sample_set,
                                      self.addition,
                                      self.custom_set,
                                      self.volume)
        return s

    def __str__(self):
        return "{},{},{},{},{},{}".format(self.x,
                                          self.y,
                                          self.time,
                                          self.type,
                                          self.hitsound,
                                          self.get_additive_str())

    @staticmethod
    def from_string(string):
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


def default_int(s):
    try:
        return int(s)
    except Exception as e:
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
        self.points = []
        self.type = "P"
        self.pixel_length = 140
        self.edge_hitsound = 0
        self.edge_addition = 0
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
        self.type = HitObject.SPINNER

    def set_data(self, data):
        self.end_time = data[5]
        self.set_addition(list(map(default_int, data[6].split(":"))))


class Hold(HitObject):
    def __init__(self, x, y, time, hitsound):
        HitObject.__init__(self, x, y, time, hitsound)
        self.end_time = time
        self.type = HitObject.HOLD

    def set_data(self, data):
        hs_data = list(map(default_int, data[5].split(":")))
        self.end_time = int(hs_data[0])
        self.set_addition(hs_data[1:])

    def get_additive_str(self):
        return "{}:".format(self.end_time) + HitObject.get_additive_str(self)

    @property
    def duration(self):
        return self.end_time - self.time
