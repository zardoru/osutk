__author__ = 'Agka'


class SampleSet(object):
    """
    The sampleset data associated to a timing point.
    """

    set_kinds = ("Auto", "Normal", "Soft", "Drum")
    AUTO = 0
    NORMAL = 1
    SOFT = 2
    DRUM = 3

    def __init__(self, kind=set_kinds[0], volume=15, custom_set=0):
        self.kind = kind
        """
        The kind of sampleset, as a string.
        """
        self.volume = volume
        """
        The volume of this sampleset, as a raw numerical .osu value.
        """
        self.custom_set = custom_set
        """
        The custom set to apply at this sampleset.
        """

    @staticmethod
    def kind_from_index(index):
        return SampleSet.set_kinds[index] if index in range(0, 4) else SampleSet.set_kinds[0]

    def set_kind_from_index(self, index):
        self.kind = SampleSet.kind_from_index(index)

    def get_osu_kind_index(self):
        return SampleSet.set_kinds.index(self.kind)
