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
        lanes = int(self.difficulty.CircleSize)
        lane_width = 512.0 / lanes
        if hitobject.x > 512.0:
            raise ValueError("The object's X (={}) is out of range.".format(hitobject.x))
        else:
            return int(hitobject.x / lane_width)

    def get_uninherited_points(self):
        return [x for x in self.timing_points if x.uninherited == 1]


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

    with open(filename) as in_file:
        # Read all sections.
        read_sections(in_file)
        load_sections()

    return output


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
