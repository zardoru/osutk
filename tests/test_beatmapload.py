from osutk.osufile import Beatmap
import osutk.osufile.beatmap as beatmp
import unittest

__author__ = 'Agka'

print("Attempting to load test1.osu.")
beatmap = Beatmap()
beatmap = beatmp.read_from_file("maps/test1.osu")


class TestBeatmapLoading(unittest.TestCase):
    def test_correct_meta(self):
        print("Testing correct metadata/general data was loaded")
        self.assertEqual(beatmap.metadata.Title, "This Will Be the Day (James Landino's Magical Girl Remix)")
        self.assertEqual(beatmap.metadata.Artist, "Jeff Williams & Casey Lee Williams")
        self.assertEqual(beatmap.metadata.Creator, "Fullerene-")

        print("Map mode is", beatmap.mode)
        self.assertEqual(beatmap.mode, "mania")

    def test_tags(self):
        print("Testing tag loading")
        self.assertEqual(len(beatmap.tags), 14)

    def test_timing_point(self):
        print("Testing that the first timing point has the correct value")
        self.assertEqual(beatmap.timing_points[0].value, 461.538461538462)
        self.assertEqual(beatmap.timing_points[0].time, 1708)
        print("Kiai-enabled timing points: ", len(list(filter(lambda x: x.kiai != 0, beatmap.timing_points))))

    def test_hitobjects(self):
        print("Testing hitobject loading")
        obj = beatmap.get_object_at_time(1708)
        print(obj)
        self.assertEqual(beatmap.get_mania_lane(obj), 0)

        obj = beatmap.get_object_at_time(44169)
        print(obj)
        self.assertEqual(beatmap.get_mania_lane(obj), 0)
        self.assertEqual(obj.end_time, 44400)
        self.assertEqual(obj.duration, 44400 - 44169)
        self.assertEqual(obj.sample_set, 2)  # soft

        obj = beatmap.get_object_at_time(46477)
        print(obj)
        self.assertEqual(beatmap.get_mania_lane(obj), 3)
        self.assertEqual(obj.sample_set, 0)

        obj = beatmap.get_object_at_time(17054)
        self.assertEqual(obj.custom_sample, "hi.wav")




if __name__ == "__main__":
    unittest.main()
