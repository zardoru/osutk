import re
from osutk.objects.timing_point import TimingPoint
from osutk.objects.hitobject import HitObject

__author__ = 'Agka'


class Color(object):
    """
    A combo color.
    """

    def __init__(self, r=255, g=255, b=255):
        self.Red = r
        """ The red value for this combo """
        self.Green = g
        """ The green value for this combo """
        self.Blue = b
        """The blue value for this combo """


class Hitsound(object):
    def __init__(self, sample_set=0, custom_set=0, hitsound=0, is_auto=True, custom_sample=""):
        self.sample_set = sample_set
        self.custom_set = custom_set
        self.hitsound = hitsound
        self._is_auto = is_auto
        self.custom_sample = custom_sample

    @property
    def is_auto(self):
        return False if len(self.custom_sample) > 4 else self._is_auto

    @property
    def is_custom_sample(self):
        return len(self.custom_sample) > 4

    def __hash__(self):
        if len(self.custom_sample) > 4:
            return hash(self.custom_sample)

        return hash((self.sample_set, self.custom_set, self.hitsound, self._is_auto))

    def __eq__(self, other):
        if len(self.custom_sample) > 4:
            eq1 = self.custom_sample
        else:
            eq1 = (self.sample_set, self.custom_set, self.hitsound, self._is_auto)

        if len(other.custom_sample) > 4:
            eq2 = other.custom_sample
        else:
            eq2 = (other.sample_set, other.custom_set, other.hitsound, other._is_auto)

        return eq1 == eq2

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getitem__(self, item):
        if item == 0:
            return self.sample_set
        if item == 1:
            return self.custom_set
        if item == 2:
            return self.hitsound
        if item == 3:
            return self.is_auto

    def __setitem__(self, key, value):
        if key == 0:
            self.sample_set = value
        if key == 1:
            self.custom_set = value
        if key == 2:
            self.hitsound = value
        if key == 3:
            self.is_auto = value


class Beatmap(object):
    def __init__(self):

        # missing: Metadata, version, mode, etcetera

        self.timing_points = []
        """ A list containing all timing points for this beatmap. """

        self.objects = []
        """ A list containing all objects for this beatmap. """

        self.colors = {}
        """ A dictionary containing the colors used on the beatmap.
        Indices are numbers, meaning ComboN has as key N. Colors have the form Color.Red/Green/Blue
        as bytes from range 0 to 255 when the map is valid. """

        self.events = []
        """ A list containing all lines from the Events section. Unparsed.
        """

        self.metadata = lambda: None
        """ Metadata for this beatmap. Does not follow python naming conventions!
         It's a 1:1 mapping of attributes from the [Metadata] section.
         This means you can use this as self.metadata.AudioFilename and so on.
         All members within this object are string-typed.
         """

        self.general = lambda: None
        """
        Same bindings as metadata, except for the [General] section.
        """

        self.difficulty = lambda: None
        """
        Same as before, except for the [Difficulty] section.
        """

        self.editor = lambda: None
        """
        Same, but the [Editor] section.
        """

    @property
    def audio(self):
        return self.metadata.AudioFilename

    @property
    def tags(self):
        """
        Get a list of tags from the metadata.
         :return: List of tags.
        """
        return self.metadata.Tags.split()

    @property
    def mode(self):
        """
        Return a string representation of the mode this beatmap is for.
         :rtype: string
         :return: The mode.
        """
        modes = ("std", "taiko", "ctb", "mania")
        return modes[int(self.general.Mode)]

    @property
    def circle_size(self):
        return int(self.difficulty.CircleSize)

    @property
    def lane_count(self):
        return self.circle_size

    @lane_count.setter
    def lane_count(self, new_count):
        self.difficulty.CircleSize = new_count

    def get_object_at_time(self, time):
        """
        Get the first declared hitobject at time.
         :param time: Time to look for a hitobject.
         :return: The HitObject.
        """
        for x in filter(lambda o: o.time == time, self.objects):
            return x
        return None

    def get_objects_at_time(self, time):
        """
        Get list of objects that overlap at time.
         :param time: Time to look for hitobjects.
         :return: [HitObject]
        """
        return list(filter(lambda o: o.time == time, self.objects))

    def get_mania_lane(self, hitobject):
        """
        Given the beatmap's circle size, return the lane the object corresponds to.
        The lane is given in the range of [0, Channels).
         :param hitobject: Hitobject to read from.
         :return: The lane for an object given the beatmap properties.
        """
        lanes = int(self.lane_count)
        lane_width = 512.0 / lanes
        if hitobject.x > 512.0:
            raise ValueError("The object's X (={}) is out of range.".format(hitobject.x))
        else:
            return int(hitobject.x / lane_width)

    def get_mania_lane_x(self, lane):
        lane_width = 512.0 / int(self.lane_count)
        return int(lane * lane_width + lane_width / 2)

    def get_lane_objects(self, lane):
        return [hitobject for hitobject in self.objects if self.get_mania_lane(hitobject) == lane]

    def get_last_object_time(self):
        return max([x.time for x in self.objects])

    def get_uninherited_points(self):
        return [x for x in self.timing_points if x.uninherited == 1]

    def get_inherited_points(self):
        return [x for x in self.timing_points if x.uninherited == 0]

    def sort_timing_points(self):
        self.timing_points = list(sorted(self.timing_points, key=lambda x: x.time))

    # Assumes times are sorted
    def get_effective_timing_point(self, time):
        current = self.timing_points[0]
        for tp in self.timing_points:
            if time >= tp.time > current.time:
                current = tp

            if tp.time > time:
                break

        return current

    def get_effective_sample_set(self, obj):
        if obj.sample_set != 0:
            return obj.sample_set
        else:
            return self.get_effective_timing_point(obj.time).sample_set.get_osu_kind_index()

    def get_effective_addition_set(self, obj):
        if obj.addition != 0:
            return obj.addition
        else:
            if obj.sample_set != 0:
                return obj.sample_set

            return self.get_effective_timing_point(obj.time).sample_set.get_osu_kind_index()

    def get_effective_sounds(self, obj):
        """

        @param obj: a hitobject
        @return: a single elemnt array with the custom sample filename,
        or an array where each element is a tuple that
        contain the soundset (normal, soft, drum), index, sound (normal, whistle, finish, clap), and whether
        the sound, soundset and index are all deduced from context.
        """
        if len(obj.custom_sample) > 4:
            return [Hitsound(custom_sample=obj.custom_sample)]

        if obj.hitsound != 0:  # has an addition
            sounds_list = []

            # if it has a SND_NORMAL, add an SND_NORMAL with the addition set and custom set indicated.
            for hitsound_type in HitObject.SOUND_TYPES:
                addition_set = self.get_effective_addition_set(obj)
                if obj.hitsound & hitsound_type:
                    custom_set = obj.custom_set if obj.custom_set == 0 \
                        else self.get_effective_timing_point(obj.time).custom_set

                    sounds_list.append(Hitsound(addition_set, custom_set, hitsound_type, False))

            return sounds_list
        else:
            custom_set = obj.custom_set if obj.custom_set == 0 \
                else self.get_effective_timing_point(obj.time).custom_set

            sampleset = self.get_effective_sample_set(obj)
            return [Hitsound(sampleset, custom_set, HitObject.SND_NORMAL, obj.custom_set == 0 and obj.sample_set == 0)]

    def get_sv_time_pairs(self):
        return [
            (x.time, x.sv)
            for x in self.get_inherited_points()
        ]

    def get_distinct_times(self):
        return set(x.time for x in self.objects)


def read_from_file(filename):
    """
    Read a osu! beatmap from a osufile.
     :param filename: File to read from.
     :return: The beatmap object
    """
    output = Beatmap()
    section_dict = {}

    # internal methods
    def read_timing(beatmap, line):
        beatmap.timing_points.append(TimingPoint.from_string(line))

    def read_attributes(area, line):
        line = line.split(":")
        attribute = line[0].strip() if len(line) > 0 else None
        value = line[1].strip() if len(line) > 1 else None

        # turn metadata into python attributes; attribute: value
        if attribute is not None and value is not None:
            setattr(area, attribute, value)

    def read_color(colors, line):
        color_regex = "\s*Combo(\d+)\s*:\s*(\d{0,3}),(\d{0,3}),(\d{0,3})\s*"
        match = re.match(color_regex, line)
        if match is not None:
            colors[int(match.group(1))] = Color(r=int(match.group(2)), g=int(match.group(3)), b=int(match.group(4)))

    def read_event(events, line):
        events.append(line)

    def read_hitobject(output_list, line):
        output_list.append(HitObject.from_string(line))

    def read_sections(file):
        current_section = "version"
        for line in file:
            line = line.rstrip()
            # Read the version.
            if current_section == "version":
                match = re.match("osu file format v(\d+)", line)
                output.version = int(match.group(1))
                current_section = "null"
                continue

            # See if we're changing the current reading section
            section_match = re.match(r'^\[(.*)\]$', line)
            if section_match is not None:  # Yes, we are
                current_section = section_match.group(1)
                section_dict[current_section] = []
                continue
            elif current_section != "null":  # No, we are not
                line = line.rstrip()
                if len(line) > 0:
                    section_dict[current_section].append(line)

    def load_sections():
        for section in section_dict:
            for line in section_dict[section]:
                if section == "TimingPoints":
                    read_timing(output, line)
                elif section == "General":
                    read_attributes(output.general, line)
                elif section == "Metadata":
                    read_attributes(output.metadata, line)
                elif section == "Difficulty":
                    read_attributes(output.difficulty, line)
                elif section == "Colours" or section == "Colors":
                    read_color(output.colors, line)
                elif section == "HitObjects":
                    read_hitobject(output.objects, line)
                elif section == "Editor":
                    read_attributes(output.editor, line)
                elif section == "Events":
                    read_event(output.events, line)

    with open(filename) as in_file:
        # Read all sections.
        read_sections(in_file)
        load_sections()

    return output


def write_to_file(beatmap, file_output):
    def write_attributes(area):
        for key in area.__dict__.keys():
            value = getattr(area, key)
            file_output.write("{}:{}\n".format(key, value))

    file_output.write("osu file format v{}\n\n".format(beatmap.version))

    file_output.write("[General]\n")
    write_attributes(beatmap.general)

    file_output.write("\n[Editor]\n")
    write_attributes(beatmap.editor)

    file_output.write("\n[Metadata]\n")
    write_attributes(beatmap.metadata)

    file_output.write("\n[Difficulty]\n")
    write_attributes(beatmap.difficulty)

    file_output.write("\n[Events]\n")
    file_output.writelines(x + "\n" for x in beatmap.events)

    file_output.write("\n[TimingPoints]\n")
    file_output.writelines(str(x) + "\n" for x in beatmap.timing_points)

    file_output.write("\n[HitObjects]\n")
    file_output.writelines(str(x) + "\n" for x in beatmap.objects)

    file_output.flush()


def replace_timing_section(in_filename, out_filename, tp):
    timing = read_from_file(in_filename).get_uninherited_points() + tp
    timing_str = "\n".join(str(x) for x in sorted(timing, key=lambda x: x.time))

    with open(in_filename) as in_file:
        text = in_file.read()
        s = "[TimingPoints]\n{}\n[".format(timing_str)
        out_text = re.sub(r"\[timingpoints\](.+?)\[", s, text, flags=re.I)
        # print(text, out_text)

    with open(out_filename, "w") as out_file:
        out_file.write(out_text)
