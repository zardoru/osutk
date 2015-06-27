from osufile import Beatmap
import unittest
import translate

__author__ = 'Agka'

print("Attempting to load test1.osu.")
beatmap = Beatmap()
beatmap = beatmap.read_from_file(None, "maps/test1.osu")


class TestBeatmapLoading(unittest.TestCase):
    def test_correctmeta(self):
        print("Testing correct metadata/general data was loaded")
        self.assertEqual(beatmap.metadata.Title, "This Will Be the Day (James Landino's Magical Girl Remix)")
        self.assertEqual(beatmap.metadata.Artist, "Jeff Williams & Casey Lee Williams")
        self.assertEqual(beatmap.metadata.Creator, "Fullerene-")

        print("Map mode is", beatmap.get_mode())
        self.assertEqual(beatmap.get_mode(), "mania")

    def test_tags(self):
        print("Testing tag loading")
        self.assertEqual(len(beatmap.get_tags()), 14)

    def test_timingpoint(self):
        print("Testing that the first timing point has the correct value")
        self.assertEqual(beatmap.timing_points[0].value, 461.538461538462)
        self.assertEqual(beatmap.timing_points[0].time, 1708)
        for x in beatmap.timing_points:
            print("Timing point starting at {} with value {}".format(x.time,
                                                                     round(translate.bpm_from_beatspace(x.value)
                                                                           if x.uninherited else -100 / x.value, 2)))


if __name__ == "__main__":
    unittest.main()
