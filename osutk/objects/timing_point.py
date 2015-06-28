from .sampleset import SampleSet

__author__ = 'Agka'

class TimingPoint(object):
    """ Timing point class that contains the relevant osu! information such as
        time, value, inherited, etc... """

    def __init__(self, time=-1, value=500, beats_per_measure=4, uninherited=1, sample_set=SampleSet(), kiai=0):
        """
        Construct a Timing Point object.
        :param time: Time in milliseconds of the current timing point.
        :param value: Value of this timing point. No validation is done.
        :param beats_per_measure: How many beats per measure are defined on this TP. Not usable for inherited TPs.
        :param inherited: Whether this is an inherited TP or not.
        :param sample_set: Sample set data (addition set, normal set, volume)
        :return: Nothing.
        """
        self.time = time
        """ Time in milliseconds for this timing point """

        self.uninherited = uninherited
        """ Whether the timing point is inherited """

        self.sample_set = sample_set
        """ Refer to SampleSet. """

        self.value = value
        """ The value of this timing point, in osu! format. """

        self.beats_per_measure = beats_per_measure
        """ The beats per measure. Only valid when the TP is not inherited. """

        self.kiai = kiai
        """ Whether this TP is a kiai section. 1 for it is, 0 for it's not. """

    def __str__(self):
        """
        Get osu! representation of timing point.
        :return: osu! representation as string for this timing point
        """
        return "{},{},{},{},{},{},{},{}".format(self.time,
                                                self.value,
                                                self.beats_per_measure,
                                                self.sample_set.get_osu_kind_index(),
                                                self.sample_set.custom_set,
                                                self.sample_set.volume,
                                                self.uninherited,
                                                self.kiai)


def from_string(string):
    """
    Construct a timing point from a osu! TP string.
    :param string: The string to build the TP from. osu! format.
    :return: The new timing point.
    """
    output = TimingPoint()
    tp = list(map(float, string.split(",")))

    # This chain is important to prevent out-of-range errors.
    for x in range(len(tp)):
        if x == 0:
            output.time = tp[x]
        elif x == 1:
            output.value = tp[x]
        elif x == 2:
            output.beats_per_measure = tp[x]
        elif x == 3:
            output.sample_set.set_kind_from_index(int(tp[x]))
        elif x == 4:
            output.sample_set.custom_set = int(tp[x])
        elif x == 5:
            output.sample_set.volume = tp[x]
        elif x == 6:
            output.uninherited = 1 if tp[x] != 0 else 0
        elif x == 7:
            output.kiai = 1 if tp[x] != 0 else 0
    return output
