from copy import copy
from enum import Enum
import math


# Whether to include the last divisor of a cycle
class CycleMode(Enum):
    NONE = 0  # Never
    ALL = 1  # Every Cycle
    LAST = 2  # Only the last cycle


class Emitter(object):
    def __init__(self, divisor, effect, is_bpm=False, round_decimals=None):
        self.divisor = divisor
        self.effect = effect
        self.is_bpm = is_bpm
        self.round_decimals = round_decimals

    def emit(self, cycle, template_timing_point, include_last_mode=CycleMode.NONE):

        ret = []

        cycle_cnt = cycle.get_cycle_count()
        for cur_cycle, time, dur in enumerate(cycle.get_cycle()):
            if include_last_mode == CycleMode.NONE:
                include_last = False
            elif include_last_mode == CycleMode.ALL:
                include_last = True
            else:
                include_last = cycle_cnt - 1 == cur_cycle

            for div_frac, div_time in self.divisor.get_cycle_relative_times(dur, include_last):
                final_time = time + div_time
                value = self.effect(div_frac)

                if self.round_decimals is not None:
                    exponent = math.pow(10, self.round_decimals)
                    final_time *= exponent
                    final_time = round(final_time)
                    final_time /= exponent

                tp = copy(template_timing_point)
                if self.is_bpm:
                    tp.set_time_and_bpm(final_time, value)
                else:
                    tp.set_time_and_mult(final_time, value)

                ret.append(tp)

        return ret


class MeasureLineEffectEmitter(object):
    def __init__(self,
                 effect,
                 distance_bpm_ms,
                 warp=True,
                 framerate=50,
                 first_part_dx=0.000001,
                 frame_first_bpm_duration_proportion=0.75,
                 warp_bpm=1000000,
                 measureline_bpm=120):  # bpm to use with measure line in effect

        self.effect = effect
        self.distance_bpm_ms = distance_bpm_ms
        self.warp = warp
        self.framerate = framerate
        self.firstPartDx = first_part_dx
        self.frameFirstBpmDurationProportion = frame_first_bpm_duration_proportion
        self.frametime = 1 / framerate * 100
        self.warp_bpm = warp_bpm
        self.measureline_bpm = measureline_bpm

        self.bpm1_duration = distance_bpm_ms * frame_first_bpm_duration_proportion
        self.bpm2_duration = self.frametime - self.bpm1_duration
        self.bpm1 = distance_bpm_ms * first_part_dx / self.bpm1_duration
        self.bpm2 = distance_bpm_ms * (1 - first_part_dx) / self.bpm2_duration
        self.bpm1_displacement = self.bpm1 * self.bpm1_duration

    def _emit(self, start_time, duration):
        frame_count = math.floor(duration / self.frametime)
        for i in range(frame_count):
            point = self.effect(i / frame_count)
            base_time = start_time + i * self.frametime + 1 if self.warp else 0

            if self.warp:
                yield (base_time - 1, self.warp_bpm)

            yield (base_time, self.bpm1)
            yield (base_time + self.bpm1_duration, self.bpm2)

            bpm_ms = point * self.distance_bpm_ms

            if bpm_ms < self.bpm1_displacement:
                # How far along in time of bpm1?
                t = bpm_ms / self.bpm1

                # Place a line here!
                if t != 0:
                    yield (base_time + t, self.bpm1)
            else:
                # Start relative to the start position of bpm2.
                bpm_ms -= self.bpm1_displacement

                # How far along in time in bpm2?
                t = bpm_ms / self.bpm2

                # same as before!
                if t != 0:
                    yield (base_time + self.bpm1_duration + t, self.measureline_bpm)

    def emit(self, start_time, duration, tp_template):
        emission = self._emit(start_time, duration)
        ret = []
        for time, bpm in sorted(emission, key=lambda x: x.time):
            tp = copy(tp_template)
            tp.set_time_and_bpm(time, bpm)
            ret.append(tp)

        return ret


def join_emissions(emission_list):
    return list([x for lst in emission_list for x in lst])
