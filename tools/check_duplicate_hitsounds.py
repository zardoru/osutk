from osutk.osufile.beatmap import read_from_file
from osutk.objects.hitobject import HitObject
import sys
from itertools import combinations
from osutk.translate import to_osu_time_notation


# only checks if additions are duplicate, not normals.
def check_duplicates(beatmap, time):
    objects = beatmap.get_objects_at_time(time)

    if len(objects) == 0:
        return []

    # get all distinct pairs where the object is not the same
    duplicates = []
    obj_pairs = set(x for x in combinations(objects, 2) if x[0] != x[1])
    for obj1, obj2 in obj_pairs:

        # different samples, not duplicated
        if obj1.custom_sample != obj2.custom_sample:
            continue

        # different addition set, not duplicated
        if beatmap.get_effective_addition_set(obj1) != beatmap.get_effective_addition_set(obj2):
            continue

        # different custom set, not duplicated
        if obj1.custom_set != obj2.custom_set:
            continue

        lane1 = beatmap.get_mania_lane(obj1) + 1
        lane2 = beatmap.get_mania_lane(obj2) + 1

        # overlaid hitsound? but it's not just a hitnormal?
        if (obj1.hitsound & obj2.hitsound) != 0:
            duplicates.append((time, lane1, lane2, obj1.hitsound & obj2.hitsound, obj1, obj2))
            continue

    return duplicates


def deduplicate(duplicates):
    for time, l1, l2, sounds, o1, o2 in duplicates:
        o2.hitsound &= (15 ^ sounds)


def main():
    beatmap = read_from_file(sys.argv[1])
    beatmap.sort_timing_points()
    duplicates = find_all_duplicates(beatmap)

    if len(duplicates) == 0:
        print("No duplicates found.")
        return

    unique_duplicate_times = set(x[0] for x in duplicates)

    if "-p" in sys.argv:
        print_results(duplicates, unique_duplicate_times)

    if "-d" in sys.argv:
        passes = 0
        while len(duplicates) > 0:
            deduplicate(duplicates)
            duplicates = find_all_duplicates(beatmap)
            passes = 1

        print("Deduplicated in {} pass(es)".format(passes))
        for x in beatmap.objects:
            print(str(x))


def find_all_duplicates(beatmap):
    moments = beatmap.get_distinct_times()
    duplicates = []
    for moment in moments:
        moment_duplicates = check_duplicates(beatmap, moment)

        duplicates.extend(moment_duplicates)
    return duplicates


def print_results(duplicates, unique_duplicate_times):
    print("{} duplicates found at {} unique times.".format(len(duplicates), len(unique_duplicate_times)))
    print("All duplicates:")
    print("==========================")
    for time, l1, l2, sounds, o1, o2 in duplicates:
        repeat = []
        if sounds & HitObject.SND_NORMAL:
            repeat.append("Normal")

        if sounds & HitObject.SND_WHISTLE:
            repeat.append("Whistle")

        if sounds & HitObject.SND_FINISH:
            repeat.append("Finish")

        if sounds & HitObject.SND_CLAP:
            repeat.append("Clap")

        ft = to_osu_time_notation(time)
        r = ", ".join(repeat)
        out = "{0} ({4}|{1},{4}|{2}) - {1} and {2} repeat {3}".format(ft, l1, l2, r, int(time))
        print(out)
    print("Unique Duplicates:")
    print("==========================")
    for t in sorted(unique_duplicate_times):
        print("{0} - ".format(to_osu_time_notation(t)))


if __name__ == '__main__':
    main()
