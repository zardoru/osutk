from copy import copy


class Cycle(object):
    def __init__(self, start_time, duration, repetitions=1, gap=0):
        self.start_time = start_time
        self.duration = duration
        self.repetitions = repetitions
        self.gap = gap

    def with_start_time(self, start_time):
        ret = copy(self)
        ret.start_time = start_time
        return ret

    def get_cycle(self):
        for i in range(self.repetitions):
            yield (self.start_time + i * self.duration + i * self.gap, self.duration)


class CycleNotes(object):
    def __init__(self, notes, duration=None, start_time=None):
        self.notes = list(sorted(notes, key=lambda x: x.time))
        self.duration = duration
        self.start_time = start_time or self.get_note_start_time()

    def get_note_start_time(self):
        return min(x.time for x in self.notes)

    def with_start_time(self, start_time):
        ret = copy(self)
        ret.start_time = start_time
        return ret

    # if a duration is provided, include the last note
    # otherwise don't
    def get_cycle(self):
        adjustment = self.start_time - self.get_note_start_time()
        for i, note in enumerate(self.notes):
            nt = note.time + adjustment
            if self.duration is not None:
                if i + 1 < len(self.notes):
                    next_note = self.notes[i + 1]
                    note_dt = next_note.time - nt
                    yield (nt, min(self.duration, note_dt))
                else:
                    yield (nt, self.duration)
            else:
                if i + 1 < len(self.notes):
                    next_note = self.notes[i + 1]
                    note_dt = next_note.time - nt
                    yield (nt, note_dt)


