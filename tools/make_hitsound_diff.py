import os.path

from osutk.osufile.beatmap import read_from_file, write_to_file, Hitsound
from osutk.objects.hitobject import HitObject, HitCircle
import sys


def generate(in_filename: str, diffname: str, msgfn):
    msgfn("Reading beatmap from '{}'...".format(in_filename))
    beatmap = read_from_file(in_filename)
    moments = beatmap.get_distinct_times()

    msgfn("Analyzing...")
    distinct_sound_combinations = set()
    sounds_at_time = {}
    for t in moments:
        objs = beatmap.get_objects_at_time(t)

        # get all of the distinct sounds at this time
        time_sounds = set(snd for obj in objs for snd in beatmap.get_effective_sounds(obj))

        sb_obj_t = [x for x in beatmap.sb_samples if int(x[0]) == int(t)]

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

    msgfn(
        "{} unique sounds found over {} different timestamps."
        .format(len(distinct_sound_combinations), len(moments))
    )

    lanes = len(distinct_sound_combinations)
    if lanes > 18 or lanes == 0:
        msgfn(
            "{} is an unreasonable number of lanes. I'll do my best."
            .format(lanes)
        )

    beatmap.lane_count = min(lanes, 18)

    # map tuples to lanes
    lane_map = {}
    lane_index = 0
    for item in distinct_sound_combinations:
        lane_map[item] = lane_index
        lane_index += 1

    msgfn("Generating hitobjects...")
    new_objects = []
    sb_obj = []
    for t in sounds_at_time.keys():
        sounds_list = sounds_at_time[t]
        for sound in sounds_list:
            obj = None
            lane = lane_map[sound]

            if sound.is_custom_sample:
                if lane > 18:
                    sb_obj.append((int(t), 0, sound.custom_sample))
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
                    obj.addition_set = sound.sample_set

            if obj is not None:
                new_objects.append(obj)

    beatmap.metadata.Version = diffname
    beatmap.objects = new_objects
    beatmap.sb_samples = sb_obj

    (directory, _) = os.path.split(os.path.abspath(in_filename))
    ofn = "{} - {} ({}) [{}].osu".format(
        beatmap.metadata.Artist,
        beatmap.metadata.Title,
        beatmap.metadata.Creator,
        diffname,
    )

    out_path = os.path.join(directory, ofn)
    msgfn("Done. Writing output to {}.".format(out_path))

    with open(out_path, "w") as output:
        write_to_file(beatmap, output)


if __name__ == '__main__':
    import tkinter as ui
    import tkinter.filedialog as fd

    root = ui.Tk()
    root.title("agka's pragmatic hitsound difficulty generator")

    lr_pane = ui.PanedWindow(root)
    lr_pane.pack(padx=10, pady=10, ipady=10, ipadx=10, side=ui.TOP, expand=1, fill=ui.BOTH)

    # Input section
    in_frame = ui.LabelFrame(lr_pane, text="input")
    in_frame.pack(ipadx=10, ipady=10, expand=1, fill=ui.BOTH, side=ui.LEFT)

    in_pane = ui.Frame(in_frame)
    in_pane.pack(expand=1, fill=ui.BOTH)

    input_tb = ui.Entry(in_pane)
    input_tb.pack(side=ui.LEFT, fill=ui.X, expand=1, pady=10, padx=10)

    def find_input():
        fh = fd.askopenfile(filetypes=[(".osu files", "*.osu")])

        input_tb.delete(0, ui.END)
        input_tb.insert(0, fh.name)

        fh.close()

    input_btn = ui.Button(in_pane, text="choose input file", command=find_input)
    input_btn.pack(side=ui.RIGHT, pady=10, padx=10)

    diffname_frame = ui.Frame(in_frame)
    diffname_frame.pack(side=ui.BOTTOM, expand=1, fill=ui.X, padx=10, pady=10)

    diffname = ui.StringVar(value="drgn.hitsounds")
    out_diffname_lbl = ui.Label(diffname_frame, text="Difficulty name")
    out_diffname_lbl.pack(side=ui.LEFT, padx=10, pady=10)

    out_diffname = ui.Entry(diffname_frame, textvariable=diffname)
    out_diffname.pack(side=ui.RIGHT, expand=1, fill=ui.X, padx=10, pady=10)

    # Messages section
    message_frame = ui.LabelFrame(lr_pane, text="Messages")
    message_frame.pack(side=ui.RIGHT, expand=1, fill=ui.BOTH)

    message_pane = ui.Frame(message_frame)
    message_pane.pack(expand=1, fill=ui.BOTH, padx=10, pady=10)

    message_scrollbar = ui.Scrollbar(message_pane)
    message_scrollbar.pack(expand=1, fill=ui.Y, side=ui.RIGHT)

    messages = ui.Text(message_pane, yscrollcommand= message_scrollbar.set, height=12)
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

        messages.delete("1.0", ui.END)

        generate(in_fn, diffname.get(), send_msg)

    action_btn = ui.Button(root, text="generate", command=perform_gen)
    action_btn.pack(side=ui.BOTTOM, pady=10, padx=10, expand=0, fill=ui.X)

    root.mainloop()
