import translate
import unittest

__author__ = 'Agka'

class TestTranslation(unittest.TestCase):
    def test_to_osu_notation(self):
        self.assertEqual("01:00:000", translate.to_osu_time_notation(60000))
        self.assertEqual("01:25:125", translate.to_osu_time_notation(60000 + 25125))
        self.assertEqual("01:05:025", translate.to_osu_time_notation(60000 + 5025))
        self.assertEqual("100:10:100", translate.to_osu_time_notation(60000 * 100 + 10100))

    def test_from_osu_notation(self):
        self.assertEqual(60000, translate.from_osu_time_notation("01:00:000"))
        self.assertEqual(60000 + 25125, translate.from_osu_time_notation("000001:25:125"))
        self.assertEqual(60000 * 100 + 10100, translate.from_osu_time_notation("100:10:100"))
        self.assertEqual(60000+5025, translate.from_osu_time_notation("01:05:025"))
        self.assertEqual(60000 + 59477, translate.from_osu_time_notation("01:59:477 (119477|4,119564|6,119652|5) - "))
        self.assertEqual(4876, translate.from_osu_time_notation("00:04:876 (2,3,4,1) - "))
        self.assertEqual(1000, translate.from_osu_time_notation("00:01:000 00:02:000"))
        self.assertEqual(-1, translate.from_osu_time_notation("0:25.125"))
        self.assertEqual(-1, translate.from_osu_time_notation(":2:25"))
        self.assertEqual(-1, translate.from_osu_time_notation("00:000025:100"))
        self.assertEqual(-1, translate.from_osu_time_notation("00:02:0"))

if __name__ == "__main__":
    unittest.main()
