import unittest

from osutk.osufile.beatmap import Hitsound


class HsHash(unittest.TestCase):
    def test_hash(self):
        a = Hitsound()
        b = Hitsound()
        self.assertEqual(a.__hash__(), b.__hash__())

    def test_hash_2(self):
        a = Hitsound(custom_sample="hi.wav")
        b = Hitsound()
        self.assertNotEqual(a.__hash__(), b.__hash__())

    def test_hash_3(self):
        a = Hitsound(hitsound=1)
        b = Hitsound(hitsound=2)
        self.assertNotEqual(a.__hash__(), b.__hash__())

    def test_hash_4(self):
        a = Hitsound()
        b = Hitsound()
        self.assertEqual(len({a, b}), 1)


if __name__ == '__main__':
    unittest.main()
