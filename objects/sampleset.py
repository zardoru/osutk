__author__ = 'Agka'

class SampleSet(object):
    set_kinds = ("Normal", "Soft", "Drum")

    def __init__(self, kind="Normal", volume=15, custom_set=0):
        self.kind = kind
        self.volume = volume
        self.custom_set = custom_set

    def set_kind_from_index(self, index):
        self.kind = SampleSet.set_kinds[index - 1] if index in range(1, 3) else SampleSet.set_kinds[0]

    def get_osu_kind_index(self):
        return SampleSet.set_kinds.index(self.kind) + 1
