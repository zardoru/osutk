__author__ = 'PAVILION'

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

            effects.append( (sv_time, new_sv) )
            last_sv = new_sv

    end = start + time_per_cycle * cycle_cnt
    if end not in effects:
        effects.append((end, effect(1)))
    return effects
