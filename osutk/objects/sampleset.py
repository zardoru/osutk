__author__ = 'Agka'

class SampleSet(object):
    set_kinds = ("Auto", "Normal", "Soft", "Drum")

    def __init__(self, kind=set_kinds[0], volume=15, custom_set=0):
        self.kind = kind
        self.volume = volume
        self.custom_set = custom_set

    @staticmethod
    def kind_from_index(index):
        return SampleSet.set_kinds[index] if index in range(0, 4) else SampleSet.set_kinds[0]

    def set_kind_from_index(self, index):
        self.kind = SampleSet.kind_from_index(index)

    def get_osu_kind_index(self):
        return SampleSet.set_kinds.index(self.kind) + 1
