__author__ = 'Agka'

# Get SV effect for effect starting from start lasting time_per_cycle in divisions_per_cycle per cycle
# cycle_cnt times
def sv_effect(start, time_per_cycle, effect, divisions_per_cycle=1, cycle_cnt=1):
    effects = []
    last_sv = -1
    for cycle in range(cycle_cnt):
        for division in range(divisions_per_cycle):
            division_lerp = division / divisions_per_cycle
            cycle_start = time_per_cycle * cycle
            division_start = division_lerp * time_per_cycle
            sv_time = start + cycle_start + division_start

            # only if SV changed a significant amount (up to 2 fraction digits) add to output
            new_sv = -100.0 / round(effect(division_lerp), 2)
            if last_sv != new_sv:
                effects.append( (sv_time, new_sv) )
                last_sv = new_sv
    end = start + time_per_cycle * cycle_cnt
    if end not in effects:
        effects.append( (end, effect(1)) )
    return effects
