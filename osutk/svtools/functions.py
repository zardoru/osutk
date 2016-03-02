__author__ = 'Agka'


def sv_effect(start, time_per_cycle, effect, divisions_per_cycle=1, cycle_cnt=1):
    """
    Get SV effect for effect starting from start lasting time_per_cycle in divisions_per_cycle per cycle
cycle_cnt times
:param start: Start time (ms)
:param time_per_cycle: Duration of a cycle (in ms)
:param effect: A function to determine what SV is mapped to values 0->1 of each cycle
:param divisions_per_cycle: How many SVs to put per a cycle
:param cycle_cnt: Amount of cycles to do
:return: A list of tuples containing time and sv value.
    """
    effects = []
    last_sv = -1
    for cycle in range(cycle_cnt):
        for division in range(divisions_per_cycle):
            division_lerp = division / divisions_per_cycle
            cycle_start = time_per_cycle * cycle
            division_start = division_lerp * time_per_cycle
            sv_time = start + cycle_start + division_start
            effect_value = effect(division_lerp)

            # discard pairs that go outside of osu's allowed range
            if effect_value < 0.1 or effect_value > 10:
                continue

            # only if SV changed a significant amount (up to 2 fraction digits) add to output
            new_sv = -100.0 / round(effect_value, 2)
            if last_sv == new_sv:
                continue

            effects.append((sv_time, new_sv))
            last_sv = new_sv

    end = start + time_per_cycle * cycle_cnt
    if end not in effects:
        effects.append((end, effect(1)))
    return effects


def sv_lerp(start_time, end_time, start_sv, end_sv, steps, ease=lambda x: x):
    """
    Returns a list of (time, value) pairs that lerps from start to finish in a number of steps
:param start_time: Starting time for the accel effect.
:param end_time: Ending time for the accel effect.
:param start_sv: Start SV for the accel effect.
:param end_sv: End SV for the accel effect.
:param steps: Amount of points to place a SV in.
:param ease: A function that eases the 0->1 mapping somehow.
:return: List of (time, value) pairs.
    """
    duration = end_time - start_time

    def lerp_func(x):
        return start_sv + (end_sv - start_sv) * ease(x)

    return sv_effect(start_time, duration, lerp_func, steps)


def sv_normalize(timing_points, bpm):
    """
    Get timing point values for inherited points which make the input timing points to a speed that looks
    like it is at the specified bpm.
:param timing_points: Timing points input. Must be a TimingPoint iterable collection.
:param bpm: BPM to make the uninherited timing points look as.
:return: A list of (time, value) pairs that acomplish this task.
    """

    # TODO: Make the algorithm also normalize SV changes to preserve (or not) their multipliers
    from ..objects import TimingPoint
    import osutk.translate as translate

    output = []
    for tp in timing_points:
        assert tp is TimingPoint
        if tp.uninherited:
            normalized_value = translate.mult_to_sv(bpm / translate.bpm_from_beatspace(tp.value))
            output.append((tp.time, normalized_value))

    return output
