import os

from osutk.osufile.beatmap import read_from_file, write_to_file, Hitsound
from osutk.objects.hitobject import HitObject, HitCircle
from shutil import copyfile

from osutk.translate import to_osu_time_notation


def accumulate_by_sound_set(sound_list: list[Hitsound], sounds_to_accumulate: int) -> int:
    """
    Reduce the number of sounds used in a custom set by accumulating them into a single sound
    @param sound_list: List of sounds to reduce.
    @param sounds_to_accumulate: Number of sounds to accumulate
    @return: Count of sounds that could not be accumulated.
    """
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


def group_sounds_by_custom_set(sound_list: list[Hitsound]) -> dict[int, list[Hitsound]]:
    sounds_by_group_index = {}
    for sound in sound_list:
        if sound.custom_set not in sounds_by_group_index:
            sounds_by_group_index[sound.custom_set] = []

        sounds_by_group_index[sound.custom_set].append(sound)
    return sounds_by_group_index


def group_sounds_by_sample_set(sounds: list[Hitsound]) -> dict[int, list[Hitsound]]:
    sounds_by_soundset = {}
    for snd in sounds:
        if snd.sample_set not in sounds_by_soundset:
            sounds_by_soundset[snd.sample_set] = []

        sounds_by_soundset[snd.sample_set].append(snd)
    return sounds_by_soundset


def assign_sounds_to_closest_objects_with_same_sound(
        hitobjects: set[HitObject],
        last_sounds: dict[Hitsound, float],
        snd_len: int,
        sounds: list[Hitsound]):
    snd_map = []
    used_sounds = set()
    for sound in sounds[:snd_len]:

        # we have assigned this sound to an object previously?
        unused_objects = hitobjects - used_sounds
        if sound in last_sounds:
            # find closest object
            obj = min(unused_objects, key=lambda o: abs(o.x - last_sounds[sound]))
        else:
            # leftmost object that's empty, any if none are empty
            obj = min(unused_objects, key=lambda o: 1024 if o.hitsound != 0 else o.x)

        # copy the position to keep track of what would be the closest to this later.
        last_sounds[sound] = obj.x
        used_sounds.add(obj)

        # map our sound to this object.
        snd_map.append((sound, obj))

    return snd_map, list(set(sounds).difference(used_sounds))


def accumulate_hitsounds(t: float, hitobjects: set[HitObject], sounds: list[Hitsound], msgfn):
    if len(sounds) > len(hitobjects):
        sounds_by_soundset = group_sounds_by_sample_set(sounds)

        sounds_to_accumulate = len(sounds) - len(hitobjects)
        for sound_set, sound_list in sounds_by_soundset.items():
            sounds_to_accumulate = accumulate_by_sound_set(sound_list, sounds_to_accumulate)
            if sounds_to_accumulate == 0:
                break

        if sounds_to_accumulate > 0:
            msgfn("we are {} notes short (there are {} notes and {} sounds) to be able to not lose any information at "
                  "{} "
                  .format(sounds_to_accumulate, len(hitobjects), len(sounds), to_osu_time_notation(t)))


def copy_sounds(
        last_sounds: dict[Hitsound, float],
        copy_to_closest: bool,
        hitobjects_dst: set[HitObject],
        sounds: list[Hitsound]):
    # map sounds to objects
    # snd_map is a list where each element of the tuple is what sound to apply to what object
    snd_len = min(len(sounds), len(hitobjects_dst))
    if copy_to_closest:
        snd_map, reminder = assign_sounds_to_closest_objects_with_same_sound(
            hitobjects_dst,
            last_sounds,
            snd_len,
            sounds)
    else:  # doesn't matter i guess?
        sndlist = list(sounds)
        snd_map = zip(sndlist[:snd_len], list(hitobjects_dst)[:snd_len])
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
                obj.addition_set = snd.sample_set

    return reminder


def do_hitsound_copy(filename_src,
                     filename_dst,
                     msgfn,
                     strictly_additive=False,
                     copy_to_closest=False,
                     copy_nonauto_hitnormals=True,
                     allow_multiple_additions=False):
    msgfn("Reading beatmap at {}...".format(filename_src))
    beatmap_src = read_from_file(filename_src)
    beatmap_dst = read_from_file(filename_dst)

    msgfn("Analyzing...")
    moments = list(sorted(beatmap_src.get_distinct_times()))

    # remove volume information but copy the storyboard sounds otherwise
    sb_sounds_out = set(x[:3] for x in beatmap_dst.sb_samples)

    if not strictly_additive:
        # We will completely replace sounds if this is true.
        sb_sounds_out = set()
        for obj in beatmap_dst.objects:
            obj.reset_hitsound()

    # This is similar to the process of make_hitsound_diff
    last_sounds = {}  # map sound to lane
    for t in moments:
        objs_src = beatmap_src.get_objects_at_time(t)
        sb_sounds_src = [x for x in beatmap_src.sb_samples if x[0] == t]

        # get all the distinct sounds at this time
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
                msgfn("{} - no objects to put {} sounds.".format(to_osu_time_notation(t), len(time_sounds_src)))
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
            accumulate_hitsounds(t, empty_sound_objs, accumulatable_sounds, msgfn)

            time_sounds_difference = custom_sounds + accumulatable_sounds

        # perform the copy at this time
        reminder = copy_sounds(last_sounds, copy_to_closest, empty_sound_objs, time_sounds_difference)

        # add remaining custom sample sounds to storyboard
        for snd in reminder:
            if snd.is_custom_sample:
                # there's not a sound at this time with the same sample? add it then
                sb_sounds_out.add((int(t), 0, snd.custom_sample))

        # at this time we have not accounted for sounds that already exist
        # so add those. to the last time we've used these sounds.
        for snd in time_sounds_pre_existing:
            if snd.obj is not None:
                last_sounds[snd] = snd.obj.x

    beatmap_dst.sb_samples = sb_sounds_out

    base_bak_path = filename_dst + '.bak'
    bak_path = base_bak_path
    suffix_index = 0
    while os.path.exists(bak_path):
        bak_path = base_bak_path + str(suffix_index)
        suffix_index += 1

    msgfn("Backing up original file {} to {}.".format(filename_dst, bak_path))
    copyfile(filename_dst, bak_path)

    msgfn("Writing output.")
    with open(filename_dst, 'w') as outfile:
        write_to_file(beatmap_dst, outfile)

    msgfn("Done.")
    msgfn("~")


def open_gui():
    import tkinter as ui
    import tkinter.filedialog as fd

    main_window = ui.Tk()
    main_window.title("agka's pragmatic osu!mania hitsound copier")

    main_pane = ui.Frame(main_window)
    main_pane.pack(padx=10, pady=10, expand=1, fill=ui.BOTH)

    lr_pane = ui.PanedWindow(main_pane, orient=ui.HORIZONTAL)
    lr_pane.pack(padx=10, pady=10, expand=1, fill=ui.BOTH)

    left_pane = ui.PanedWindow(lr_pane, orient=ui.VERTICAL)
    left_pane.pack(side=ui.LEFT, padx=10, pady=10, expand=1)
    lr_pane.add(left_pane)

    right_pane = ui.PanedWindow(lr_pane, orient=ui.VERTICAL)
    right_pane.pack(side=ui.RIGHT, padx=10, pady=10, expand=1, fill=ui.Y)
    lr_pane.add(right_pane)

    # files pane
    files_frame = ui.LabelFrame(left_pane, text="Input/Output", padx=10, pady=10)
    files_frame.pack()
    left_pane.add(files_frame)

    files_pane = ui.PanedWindow(files_frame)
    files_pane.pack()

    # input pane
    input_pane = ui.Frame(files_pane)
    input_pane.pack(fill=ui.X, pady=5)

    input_filename_tb = ui.Text(input_pane, height=1)
    input_filename_tb.pack(side=ui.LEFT, fill=ui.X, padx=5)

    def set_input_file():
        fh = fd.askopenfile(mode="r", title="open destination osu file", filetypes=[(".osu files", "*.osu")])

        input_filename_tb.delete("1.0", ui.END)
        input_filename_tb.insert("1.0", fh.name)

        fh.close()

    input_button = ui.Button(input_pane,
                             text="choose source beatmap...",
                             command=set_input_file)
    input_button.pack(side=ui.RIGHT, fill=ui.X, padx=5)

    # output pane
    output_pane = ui.Frame(files_pane)
    output_pane.pack(fill=ui.X, pady=5)

    output_filename = ui.Text(output_pane, height=1)
    output_filename.pack(side=ui.LEFT, fill=ui.X, padx=5)

    def set_output_file():
        fh = fd.askopenfile(mode="w", title="open destination osu file", filetypes=[(".osu files", "*.osu")])

        # managing text with tkinter blows lol
        output_filename.delete("1.0", ui.END)
        output_filename.insert("1.0", fh.name)

        fh.close()

    output_button = ui.Button(output_pane,
                              text="choose destination beatmap...",
                              command=set_output_file,
                              padx=5)

    output_button.pack(side=ui.RIGHT, fill=ui.NONE)

    # options pane
    options_frame = ui.LabelFrame(left_pane, text="Options", pady=10, padx=10)
    options_frame.pack(side="left", expand=1, fill=ui.BOTH)
    left_pane.add(options_frame)

    options_pane = ui.Frame(options_frame)
    options_pane.pack(side="left", expand=1)

    replace_dst_hs = ui.BooleanVar()
    replace_dst_hs_cb = ui.Checkbutton(options_pane, text="Replace destination hitsounds", variable=replace_dst_hs)
    replace_dst_hs_cb.grid(column=0, row=0, sticky="W", padx=5)

    copy_to_closest = ui.BooleanVar()
    copy_to_closest_cb = ui.Checkbutton(options_pane,
                                        text="Copy to most similarly positioned note",
                                        variable=copy_to_closest)
    copy_to_closest_cb.grid(column=1, row=0, sticky="W", padx=5)

    allow_multiple_adds = ui.BooleanVar()
    allow_multiple_adds_cb = ui.Checkbutton(options_pane, text="Allow multiple additions per note",
                                            variable=allow_multiple_adds)
    allow_multiple_adds_cb.grid(column=0, row=1, sticky="W", padx=5)

    copy_nonauto_hitnormals = ui.BooleanVar(value=True)
    copy_nonauto_hitnormals_cb = ui.Checkbutton(options_pane, text="Copy hitnormals with non-default sampleset",
                                                variable=copy_nonauto_hitnormals)
    copy_nonauto_hitnormals_cb.grid(column=1, row=1, sticky="W", padx=5)

    # messages pane
    messages_frame = ui.LabelFrame(right_pane, text="Messages")
    messages_frame.pack(expand=1, fill=ui.BOTH)
    right_pane.add(messages_frame)

    messages_pane = ui.PanedWindow(messages_frame)
    messages_pane.pack(expand=1, fill=ui.BOTH, pady=10, padx=10)

    messages_scrollbar = ui.Scrollbar(messages_pane)
    messages_scrollbar.pack(side=ui.RIGHT, fill=ui.Y)

    messages = ui.Text(messages_pane, height=20, yscrollcommand=messages_scrollbar.set)
    messages.pack(side=ui.LEFT, expand=1, fill=ui.BOTH)

    messages_scrollbar.config(command=messages.yview)


    # actions pane
    actions_pane = ui.PanedWindow(main_pane)
    actions_pane.pack(expand=0, fill=ui.X, side=ui.BOTTOM, anchor="s")

    def print_msg(content: str):
        messages.insert(ui.END, content + "\n")

    def run_copy():
        inp = input_filename_tb.get("1.0", ui.END).strip()
        out = output_filename.get("1.0", ui.END).strip()

        if not os.path.isfile(inp):
            print_msg("couldn't find or access file {}.".format(inp))
            return

        if not os.path.isfile(out):
            print_msg("couldn't find or access file {}.".format(out))
            return

        # clear the output thingy
        messages.delete("1.0", ui.END)

        do_hitsound_copy(inp, out,
                         print_msg,
                         strictly_additive=replace_dst_hs.get(),
                         copy_to_closest=copy_to_closest.get(),
                         copy_nonauto_hitnormals=copy_nonauto_hitnormals.get(),
                         allow_multiple_additions=allow_multiple_adds.get())

    execute_button = ui.Button(actions_pane, text="run copy", command=run_copy)
    execute_button.pack(expand=0, fill=ui.NONE, side=ui.RIGHT, anchor=ui.S)
    actions_pane.add(execute_button)

    main_window.resizable(True, True)
    main_window.mainloop()


if __name__ == '__main__':
    open_gui()
