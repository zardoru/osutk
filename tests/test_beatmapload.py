from osutk.osufile import Beatmap
import osutk.osufile.beatmap as beatmp
import unittest

__author__ = 'Agka'

print("Attempting to load test1.osu.")
beatmap = Beatmap()
beatmap = beatmp.read_from_file("maps/test1.osu")


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
        print ("Kiai-enabled timing points: ", len(list(filter(lambda x: x.kiai != 0, beatmap.timing_points))))


if __name__ == "__main__":
    unittest.main()
