from math import floor
from ..translate.functions import bpm_to_beatspace


class DivisorFixed(object):
    def __init__(self, count):
        self.count = count

    def get_cycle_relative_times(self, duration, include_last):
        gap = floor(duration / self.count)
        for i in range(self.count + 1 if include_last else 0):
           yield (i / self.count, gap * i)


class DivisorBpm(object):
    def __init__(self, bpm, beat_cnt):
        self.bpm = bpm
        self.beat_cnt = beat_cnt

        self.gap = bpm_to_beatspace(self.bpm) * self.beat_cnt

    def get_cycle_relative_times(self, duration, include_last):
        count = floor(duration / self.gap)
        for i in range(count + 1 if include_last else 0):
            yield (i / count, self.gap * i)


class DivisorSpan(object):
    def __init__(self, span):
        self.span = span

    def get_cycle_relative_times(self, duration, include_last):
        count = floor(duration / self.span)
        for i in range(count + 1 if include_last else 0):
            yield (i / count, self.span * i)

