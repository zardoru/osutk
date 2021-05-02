from osutk.osufile.beatmap import read_from_file, write_to_file, Hitsound
from osutk.objects.hitobject import HitObject, HitCircle
import sys


def main(filename):
    print("Reading beatmap...", file=sys.stderr)
    beatmap = read_from_file(filename)
    moments = beatmap.get_distinct_times()

    print("Analyzing...", file=sys.stderr)
    distinct_sound_combinations = set()
    sounds_at_time = {}
    for t in moments:
        objs = beatmap.get_objects_at_time(t)

        # get all of the distinct sounds at this time
        time_sounds = set(snd for obj in objs for snd in beatmap.get_effective_sounds(obj))

        sb_obj_t = [x for x in beatmap.sb_samples if x[0] == t]

        for x in sb_obj_t:
            time_sounds.add(Hitsound(custom_sample=x[2]))

        # remove the sounds that are completely deduced,
        # leaving only sounds that were actually set
        time_sounds = set(snd for snd in time_sounds if not snd.is_auto)

        # add the distinct sounds to our list of
        # distinct sounds in the totality of the map
        for x in time_sounds:
            distinct_sound_combinations.add(x)

        # add to our dictionary of sounds at different times
        sounds_at_time[t] = time_sounds

    print(
        "{} unique sounds found over {} different timestamps."
        .format(len(distinct_sound_combinations), len(moments)),
        file=sys.stderr
    )

    lanes = len(distinct_sound_combinations)
    if lanes > 18 or lanes == 0:
        print(
            "{} is an unreasonable number of lanes. I'll do my best."
            .format(lanes),
            file=sys.stderr
        )

    beatmap.lane_count = min(lanes, 18)

    # map tuples to lanes
    lane_map = {}
    lane_index = 0
    for item in distinct_sound_combinations:
        lane_map[item] = lane_index
        lane_index += 1

    print("Generating hitobjects...", file=sys.stderr)
    new_objects = []
    sb_obj = []
    for t in sounds_at_time.keys():
        sounds_list = sounds_at_time[t]
        for sound in sounds_list:
            obj = None
            lane = lane_map[sound]

            if sound.is_custom_sample:
                if lane > 18:
                    sb_obj.append((t, 0, sound.custom_sample))
                else:
                    obj = HitCircle(beatmap.get_mania_lane_x(lane), 240, t, 0)
                    obj.custom_sample = sound.custom_sample

            else:
                if lane > 18:
                    continue  # TODO: maybe make it so if it's a custom set, we translate that to a custom sample?

                obj = HitCircle(beatmap.get_mania_lane_x(lane), 240, t, sound.hitsound)
                obj.custom_set = sound.custom_set
                obj.sample_set = sound.sample_set

                if sound[2] & HitObject.SND_NORMAL != 0:
                    obj.addition = sound.sample_set

            if obj is not None:
                new_objects.append(obj)

    beatmap.metadata.Version = "drgn.hitsounds"
    beatmap.objects = new_objects
    beatmap.sb_samples = sb_obj

    print("Done. Writing output.", file=sys.stderr)
    write_to_file(beatmap, sys.stdout)


if __name__ == '__main__':
    main(sys.argv[1])
