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

