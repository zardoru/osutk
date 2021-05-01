import os

from osutk.osufile.beatmap import read_from_file, write_to_file, Hitsound
from osutk.objects.hitobject import HitObject, HitCircle
from shutil import copyfile
import sys

from osutk.translate import to_osu_time_notation


def reduce_by_custom_set(sound_list, sounds_to_accumulate):
    sounds_by_custom_set = group_sounds_by_custom_set(sound_list)

    for custom_set, sound_list in sounds_by_custom_set.items():
        # group hitsounds of this group.
        while len(sound_list) > 1:
            sound_list[0].hitsound |= sound_list[1].hitsound
            sound_list.remove(sound_list[1])
            sounds_to_accumulate -= 1

            if sounds_to_accumulate <= 0:
                break

        if sounds_to_accumulate <= 0:
            break

    return sounds_to_accumulate


def group_sounds_by_custom_set(sound_list):
    sounds_by_group_index = {}
    for sound in sound_list:
        if sound.custom_set not in sounds_by_group_index:
            sounds_by_group_index[sound.custom_set] = []

        sounds_by_group_index[sound.custom_set].append(sound)
    return sounds_by_group_index


def group_sounds_by_sample_set(sounds):
    sounds_by_soundset = {}
    for snd in sounds:
        if snd.sample_set not in sounds_by_soundset:
            sounds_by_soundset[snd.sample_set] = []

        sounds_by_soundset[snd.sample_set].append(snd)
    return sounds_by_soundset


def assign_sounds_to_closest_objects_with_same_sound(hitobjects, last_sounds, snd_len, sounds):
    snd_map = []
    used_sounds = set()
    for sound in sounds[:snd_len]:

        # we have assigned this sound to an object previously?
        if sound in last_sounds:
            # find closest object
            obj = min(hitobjects - used_sounds, key=lambda o: abs(o.x - last_sounds[sound]))
        else:
            # leftmost object that's empty, any if none are empty
            obj = min(hitobjects - used_sounds, key=lambda o: 1024 if o.hitsound != 0 else o.x)

        # copy the position to keep track of what would be the closest to this later.
        last_sounds[sound] = obj.x
        used_sounds.add(obj)

        # map our sound to this object.
        snd_map.append((sound, obj))

    return snd_map, list(set(sounds).difference(used_sounds))


def accumulate_hitsounds(t, hitobjects, sounds):
    if len(sounds) > len(hitobjects):
        sounds_by_soundset = group_sounds_by_sample_set(sounds)

        sounds_to_accumulate = len(sounds) - len(hitobjects)
        for sound_set, sound_list in sounds_by_soundset.items():
            sounds_to_accumulate = reduce_by_custom_set(sound_list, sounds_to_accumulate)
            if sounds_to_accumulate == 0:
                break

        if sounds_to_accumulate > 0:
            print("we are {} notes short (there are {} notes and {} sounds) to be able to not lose any information at "
                  "{} "
                  .format(sounds_to_accumulate, len(hitobjects), len(sounds), to_osu_time_notation(t)))


def copy_sounds(last_sounds, copy_to_closest, hitobjects, sounds):

    # map sounds to objects
    # snd_map is a list where each element of the tuple is what sound to apply to what object
    snd_len = min(len(sounds), len(hitobjects))
    if copy_to_closest:
        snd_map, reminder = assign_sounds_to_closest_objects_with_same_sound(hitobjects, last_sounds, snd_len, sounds)
    else:  # doesn't matter i guess?
        sndlist = list(sounds)
        snd_map = zip(sndlist[:snd_len], list(hitobjects)[:snd_len])
        reminder = sndlist[snd_len:]

    # copy sounds
    for snd, obj in snd_map:
        if snd.is_custom_sample:
            obj.custom_sample = snd.custom_sample
        else:
            obj.sample_set = snd.sample_set
            obj.custom_set = snd.custom_set
            obj.hitsound = snd.hitsound

            if snd.hitsound > 0:
                obj.addition = snd.sample_set

    return reminder


def main(filename_src,
         filename_dst,
         strictly_additive=False,
         copy_to_closest=False,
         copy_nonauto_hitnormals=True,
         allow_multiple_additions=False):
    print("Reading beatmap...", file=sys.stderr)
    beatmap_src = read_from_file(filename_src)
    beatmap_dst = read_from_file(filename_dst)

    print("Analyzing...", file=sys.stderr)
    moments = list(sorted(beatmap_src.get_distinct_times()))

    # remove volume information but copy the storyboard sounds otherwise
    sb_sounds_out = set(x[:3] for x in beatmap_dst.sb_sounds)

    if not strictly_additive:
        sb_sounds_out = []
        for obj in beatmap_dst.objects:
            obj.reset_hitsound()

    # This is similar to the process of make_hitsound_diff
    last_sounds = {}  # map sound to lane
    for t in moments:
        objs_src = beatmap_src.get_objects_at_time(t)
        sb_sounds_src = [x for x in beatmap_src.sb_samples if x[0] == t]

        # get all of the distinct sounds at this time
        # remove the sounds that are completely deduced,
        # leaving only sounds that were actually set
        time_sounds_src = list(snd for obj in objs_src
                               for snd in beatmap_src.get_effective_sounds(obj)
                               if not snd.is_auto)

        # account for storyboard samples
        time_sounds_src.extend(Hitsound(custom_sample=x[2]) for x in sb_sounds_src)

        # exclude hitnormals from our copy, if the user said not to include them.
        if not copy_nonauto_hitnormals:
            time_sounds_src = list(snd for snd in time_sounds_src
                                   if snd.hitsound != HitObject.SND_NORMAL)

        # get objects of the destination at the current timestamp
        objs_dst = beatmap_dst.get_objects_at_time(t)
        sb_sounds_dst = [x for x in sb_sounds_out if x[0] == t]

        # if it's empty, don't bother
        if len(objs_dst) == 0:
            if len(time_sounds_src) > 0:
                # informative, but a little spammy. just in case it's useful.
                print("no sounds at {} to put {} sounds.".format(t, len(time_sounds_src)))
            continue

        # get the list of all sounds for the objects of the destination at this time.
        time_sounds_dst = list(snd for obj in objs_dst for snd in beatmap_dst.get_effective_sounds(obj))

        # add list of storyboard samples in the destination
        time_sounds_dst.extend(Hitsound(custom_sample=x[2]) for x in sb_sounds_dst)

        # take out all sounds from the source that already exist in the destination
        time_sounds_pre_existing = []
        time_sounds_difference = time_sounds_src[:]
        for snd in time_sounds_dst:
            if snd in time_sounds_difference:
                time_sounds_pre_existing.append(snd)
                time_sounds_difference.remove(snd)

        # get hitobjects we can add hitsounds to, because they're empty
        empty_sound_objs = set(obj for obj in objs_dst
                               for snd in beatmap_dst.get_effective_sounds(obj)
                               if snd.is_auto)

        # accumulate sounds if we're short a few empty objects and they can be accumulated
        if allow_multiple_additions:
            custom_sounds = [x for x in time_sounds_difference if x.is_custom_sample]
            accumulatable_sounds = [x for x in time_sounds_difference if not x.is_custom_sample]
            accumulate_hitsounds(t, empty_sound_objs, accumulatable_sounds)

            time_sounds_difference = custom_sounds + accumulatable_sounds

        # perform the copy at this time
        reminder = copy_sounds(last_sounds, copy_to_closest, empty_sound_objs, time_sounds_difference)

        # add remaining custom sample sounds to storyboard
        for snd in reminder:
            if snd.is_custom_sample:
                # there's not a sound at this time with the same sample? add it then
                sb_sounds_out.add((t, 0, snd.custom_sample))

        # at this time we have not accounted for sounds that already exist
        # so add those. to the last time we've used these sounds.
        for snd in time_sounds_pre_existing:
            if snd.obj is not None:
                last_sounds[snd] = snd.obj.x

    print("Backing up original file {} to {}.".format(filename_dst, filename_dst + '.bak'))
    copyfile(filename_dst, filename_dst + '.bak')

    print("Writing output.")
    with open(filename_dst, 'w') as outfile:
        write_to_file(beatmap_dst, outfile)

    print("Done.")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("copy_hitsounds '[src]' '[dst]' (-a|-c|-n|-m)+")
        print("-a: only add sounds")
        print("-c: copy sounds to closest note")
        print("-n: copy hitnormals with non-auto sample set")
        print("-m: allow multiple additions on one note")

    if not os.path.exists(sys.argv[1]):
        print("sorry, can't locate source file at {}".format(os.path.abspath(sys.argv[1])))
        quit(1)

    if os.path.exists(sys.argv[2]):
        print("overwriting file {}".format(os.path.abspath(sys.argv[2])))
    else:
        print("creating file {}".format(os.path.abspath(sys.argv[2])))

    main(
        sys.argv[1], sys.argv[2],
        strictly_additive='-a' in sys.argv,
        copy_to_closest='-c' in sys.argv,
        copy_nonauto_hitnormals='-n' in sys.argv,
        allow_multiple_additions='-m' in sys.argv
    )
