from osutk.osufile.beatmap import read_from_file, write_to_file
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

        # remove the sounds that are completely deduced,
        # leaving only sounds that were actually set
        time_sounds = set(snd for snd in time_sounds if not snd[3])

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

    beatmap.lane_count = lanes

    # map tuples to lanes
    lane_map = {}
    lane_index = 0
    for item in distinct_sound_combinations:
        lane_map[item] = lane_index
        lane_index += 1

    print("Generating hitobjects...", file=sys.stderr)
    new_objects = []
    for t in sounds_at_time.keys():
        sounds_list = sounds_at_time[t]
        for sound in sounds_list:
            lane = lane_map[sound]

            if type(sound) == str:
                obj = HitCircle(beatmap.get_mania_lane_x(lane), 240, t, 0)
                obj.custom_sample = sound
            else:
                obj = HitCircle(beatmap.get_mania_lane_x(lane), 240, t, sound[2])
                obj.custom_set = sound[1]
                obj.sample_set = sound[0]

                if sound[2] & HitObject.SND_NORMAL != 0:
                    obj.addition = sound[0]

            new_objects.append(obj)

    beatmap.metadata.Version = "drgn.hitsounds"
    beatmap.objects = new_objects

    print("Done. Writing output.", file=sys.stderr)
    write_to_file(beatmap, sys.stdout)


if __name__ == '__main__':
    main(sys.argv[1])
