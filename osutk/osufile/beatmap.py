__author__ = 'Agka'

import re

import osutk.objects.timing_point as timing_point

class Color(object):
    def __init__(self, r=255, g=255, b=255):
        self.Red = r
        self.Green = g
        self.Blue = b


class Beatmap(object):
    def __init__(self):

        # missing: Metadata, version, mode, etcetera

        self.timing_points = []
        """ A list containing all timing points for this osu! osufile. """

        self.objects = []
        """ A list containing all objects for this osu! osufile. """

        self.colors = {}
        """ A dictionary containing the colors used on the beatmap.
        Indices are numbers, meaning ComboN has as key N. Colors have the form Color.Red/Green/Blue
        as bytes from range 0 to 255 when the map is valid. """

        self.metadata = lambda: None
        """ Metadata for this beatmap. Does not follow python naming conventions!
         It's a 1:1 mapping of attributes from the [Metadata] section.
         This means you can use this as self.metadata.AudioFilename and so on.
         """

        self.general = lambda: None
        """ Same bindings as metadata, except for the [General] section.
        """

    def get_tags(self):
        """
        Get a list of tags from the metadata.
        :return: Tags.
        """
        return self.metadata.Tags.split(" ")

    def get_mode(self):
        """
        Return a string representation of the mode this beatmap is for.
        :return: The mode.
        """
        modes = ("standard", "taiko", "ctb", "mania")
        return modes[int(self.general.Mode)]


def read_timing(beatmap, line):
    beatmap.timing_points.append(timing_point.from_string(line))


def read_attributes(area, line):
    line = line.split(":")
    attribute = line[0].strip() if len(line) > 0 else None
    value = line[1].strip() if len(line) > 1 else None

    # turn metadata into python attributes; attribute: value
    if attribute is not None and value is not None:
        setattr(area, attribute, value)


def read_color(colors, line):
    match = re.match(
        "\s*Combo(\d+)\s*:\s*(\d{0,3}),(\d{0,3}),(\d{0,3})\s*", line)
    if match is not None:
        colors[int(match.group(1))] = Color(r=int(match.group(2)), g=int(match.group(3)), b=int(match.group(4)))


def read_from_file(filename):
    """
    Read a osu! beatmap from a osufile.
    :param filename:
    :return: the beatmap object
    """
    output = Beatmap()
    with open(filename) as in_file:
        current_section = "version"
        section_regex = re.compile(r'^\[(.*)\]$')
        section_dict = {}
        for line in in_file:
            line = line.rstrip()
            # Read the version.
            if current_section == "version":
                match = re.match("osu file format v(\d+)", line)
                output.version = int(match.group(1))
                current_section = "null"
                continue

            # See if we're changing the current reading section
            section_match = section_regex.match(line)
            if section_match is not None:  # Yes, we are
                current_section = section_match.group(1)
                section_dict[current_section] = []
                continue
            elif current_section != "null":  # No, we are not
                line = line.rstrip()
                if len(line) > 0:
                    section_dict[current_section].append(line)

        for section in section_dict:
            for line in section_dict[section]:
                if section == "TimingPoints":
                    read_timing(output, line)
                elif section == "General":
                    read_attributes(output.general, line)
                elif section == "Metadata":
                    read_attributes(output.metadata, line)
                elif section == "Colours" or section == "Colors":
                    read_color(output.colors, line)
    return output
