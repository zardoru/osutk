import os

from osutk.osufile.beatmap import read_from_file, Beatmap
from osutk.objects.hitobject import HitObject
import sys
from itertools import combinations
from osutk.translate import to_osu_time_notation

dupentry = tuple[float, int, int, int, HitObject, HitObject]


# only checks if additions are duplicate, not normals.
def check_duplicates_at_time(beatmap: Beatmap, time: float) -> list[dupentry]:
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


def deduplicate(duplicates: list[dupentry]):
    for time, l1, l2, sounds, o1, o2 in duplicates:
        o2.hitsound &= (15 ^ sounds)


def find_all_duplicates(beatmap: Beatmap) -> list[dupentry]:
    moments = beatmap.get_distinct_times()
    duplicates = []
    for moment in moments:
        moment_duplicates = check_duplicates_at_time(beatmap, moment)

        duplicates.extend(moment_duplicates)
    return duplicates


def print_results(beatmap: Beatmap, duplicates: list[dupentry], unique_duplicate_times, msg):
    msg("{} duplicates found at {} unique times.".format(len(duplicates), len(unique_duplicate_times)))
    msg("All duplicates:")
    msg("==========================")
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
        out = "{0} ({4}|{1},{4}|{2}) - {1} and {2} repeat {3} - Sets: {5}/{6} Custom Set {7}/{8}" \
            .format(ft, l1, l2, r, int(time),
                    beatmap.get_effective_addition_set(o1), beatmap.get_effective_addition_set(o2),
                    o1.custom_set, o2.custom_set)
        msg(out)
    msg("Unique Duplicates:")
    msg("==========================")
    for t in sorted(unique_duplicate_times):
        msg("{0}".format(to_osu_time_notation(t)))


def check_duplicates(filename: str, should_print_results: bool, should_deduplicate: bool, msg):
    beatmap = read_from_file(filename)
    beatmap.sort_timing_points()
    duplicates = find_all_duplicates(beatmap)

    if len(duplicates) == 0:
        msg("No duplicates found.")
        return

    unique_duplicate_times = set(x[0] for x in duplicates)

    if should_print_results:
        print_results(beatmap, duplicates, unique_duplicate_times, msg)

    if should_deduplicate:
        # passes = 0
        while len(duplicates) > 0:
            deduplicate(duplicates)
            duplicates = find_all_duplicates(beatmap)
            # passes = 1

        # print("Deduplicated in {} pass(es)".format(passes))
        # for x in beatmap.objects:
        #    print(str(x))


if __name__ == '__main__':
    import tkinter as ui
    import tkinter.filedialog as fd

    root = ui.Tk()
    root.title("agka's surprisingly practical hitsound deduplicator")

    lr_pane = ui.PanedWindow(root, orient=ui.VERTICAL)
    lr_pane.pack(padx=10, pady=10, ipady=10, ipadx=10, side=ui.TOP, expand=1, fill=ui.BOTH)

    # Input section
    in_frame = ui.LabelFrame(lr_pane, text="input")
    lr_pane.add(in_frame)

    in_pane = ui.Frame(in_frame)
    in_pane.pack(expand=1, fill=ui.X)

    input_tb = ui.Entry(in_pane)
    input_tb.pack(side=ui.LEFT, fill=ui.X, expand=1, pady=10, padx=10)


    def find_input():
        fh = fd.askopenfile(filetypes=[(".osu files", "*.osu")])

        input_tb.delete(0, ui.END)
        input_tb.insert(0, fh.name)

        fh.close()


    input_btn = ui.Button(in_pane, text="choose input file", command=find_input)
    input_btn.pack(side=ui.RIGHT, pady=10, padx=10)

    # Messages section
    message_frame = ui.LabelFrame(lr_pane, text="Messages")
    lr_pane.add(message_frame)

    message_pane = ui.Frame(message_frame)
    message_pane.pack(expand=1, fill=ui.BOTH, padx=10, pady=10)

    message_scrollbar = ui.Scrollbar(message_pane)
    message_scrollbar.pack(expand=1, fill=ui.Y, side=ui.RIGHT)

    messages = ui.Text(message_pane, yscrollcommand=message_scrollbar.set, height=12)
    messages.pack(expand=1, fill=ui.BOTH, side=ui.LEFT)

    message_scrollbar.config(command=messages.yview)

    # Actions
    def send_msg(msg):
        messages.insert(ui.END, msg + "\n")

    def perform_gen():
        in_fn = input_tb.get()
        if not os.path.isfile(in_fn):
            send_msg("couldn't open file {}.".format(in_fn))
            return

        dedup = not dry_run.get()
        messages.delete("1.0", ui.END)

        check_duplicates(in_fn, True, dedup, send_msg)


    action_btn = ui.Button(root, text="generate", command=perform_gen)
    action_btn.pack(side=ui.BOTTOM, pady=10, padx=10, expand=0, fill=ui.X)

    dry_run = ui.BooleanVar(root, value=False)
    dry_run_cb = ui.Checkbutton(text="Dry run (i.e., do not deduplicate)", variable=dry_run)
    dry_run_cb.pack(side=ui.BOTTOM, expand=0)



    root.mainloop()
