__author__ = 'Agka'


def bpm_to_beatspace(bpm):
    """
    Convert a BPM to a beatspace
    :param bpm: BPM to convert
    :return: BPM converted to Beats per Millisecond
    """
    return 60000.0 / bpm


def bpm_from_beatspace(btsp):
    """
    Convert a beatspace to a BPM
    Provided as convenience; the operation is the same as bpm_to_beatspace.
:param btsp: beatspace to convert
:return: beatspace converted to BPM
    """
    return 60000.0 / btsp


def to_osu_time_notation(time):
    """
    Transform a time in milliseconds to a string with the osu! time notation.
:param time: Time in milliseconds to convert.
:return: The string representation of the time.
    """
    try:
        time = int(time)
    except:
        raise ValueError("Invalid parameter. Expected convertible to int.")

    minutes = int(time/60000)
    milliseconds = int(time % 1000)
    seconds = int((time - minutes * 60000 - milliseconds) / 1000)
    return "{:02d}:{:02d}:{:03d}".format(minutes, seconds, milliseconds)


def beats_to_time(bpm, beats):
    return bpm_to_beatspace(bpm) * beats


def from_editor(str):
    return []


def editor_note_gap(str):
    notes = from_editor(str)
    return notes[1].time - notes[0].time


def from_osu_time_notation(time_string):
    """
    Transform from the osu! time notation to a time in milliseconds
:param time_string: String to convert from
:return: Time in milliseconds. Raises ValueError on failure.
    """
    from re import match

    try:
        time_match = match("(\d{2,}):(\d\d):(\d\d\d)", time_string)
    except:
        raise ValueError("Invalid parameter")

    if time_match is not None:
        mins = int(time_match.group(1))
        secs = int(time_match.group(2))
        millisecs = int(time_match.group(3))
        return mins * 60000 + secs * 1000 + millisecs
    else:
        raise ValueError("Not a valid osu! time notation string!")


def mult_to_sv(mult):
    return -100 / mult


def sv_to_mult(sv):
    return -100 / sv
