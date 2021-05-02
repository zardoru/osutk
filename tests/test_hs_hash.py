import unittest

from osutk.objects import HitObject, HitCircle
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


class HoHash(unittest.TestCase):
    def test_hash(self):
        a = HitObject(0, 0, 0, 0)
        b = HitObject(0, 0, 0, 0)
        self.assertEqual(a.__hash__(), b.__hash__())

    def test_hash_2(self):
        a = HitObject(1, 0, 0, 0)
        b = HitObject(0, 0, 0, 0)
        self.assertNotEqual(a.__hash__(), b.__hash__())

    def test_hash_3(self):
        s = {HitObject(0, 0, 0, 0), HitCircle(0, 0, 0, 0)}
        self.assertEqual(len(s), 1)


if __name__ == '__main__':
    unittest.main()
