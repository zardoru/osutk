__author__ = 'Agka'

import re
from objects.timing_point import TimingPoint

class Beatmap(object):
    def __init__(self):

        # missing: Metadata, version, mode, etcetera

        self.timing_points = []
        """ A list containing all timing points for this osu! file. """

        self.objects = []
        """ A list containing all objects for this osu! file. """

        self.metadata = lambda: None
        """ Metadata for this beatmap. Does not follow python conventions!
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

    @staticmethod
    def read_timing(beatmap, line):
        beatmap.timing_points.append(TimingPoint.from_string(line))

    @staticmethod
    def read_attributes(area, line):
        line = line.split(":")
        attribute = line[0].trim() if len(line) > 0 else None
        value = line[1].trim() if len(line) > 1 else None

        # turn metadata into python attributes; attribute: value
        setattr(area, attribute, value)
        pass

    @staticmethod
    def read_from_file(self, filename):
        """
        Read a osu! beatmap from a file.
        :param filename:
        :return: the beatmap object
        """
        output = Beatmap()
        in_file = open(filename)

        current_section = "version"
        section_regex = re.compile(r'^\[(.*)\]$')
        section_dict = {}
        for line in in_file:
            # Read the version.
            if current_section == "version":
                output.version = int(re.match(line, "osu file format v(\d+)").group(1))
                current_section = "null"
                continue

            # See if we're changing the current reading section
            section_match = section_regex.match(line)
            if section_match is not None: # Yes, we are
                current_section = section_match.group(1)
                section_dict[current_section] = []
                continue
            else: # No, we are not
                line = line.rstrip()
                section_dict[current_section].append(line)

        for section in section_dict:
            if section == "TimingPoints":
                for x in section_dict[section]: Beatmap.read_timing(output, x)
            if section == "General":
                for x in section_dict[section]: Beatmap.read_attributes(output.general, x)
            if section == "Metadata":
                for x in section_dict[section]: Beatmap.read_attributes(output.metadata, x)
        return output