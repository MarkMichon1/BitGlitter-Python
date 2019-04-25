import unittest
from bitglitter.read.coloranalysis import colorSnap, returnDistance


class Test(unittest.TestCase):

    # Return the correct color with both zero changes in value, and 'dirty' values.
    def test_colorSnap(self):
        self.assertEqual(colorSnap((0, 0, 0), ((0, 0, 0), (255, 255, 255))), (0, 0, 0))
        self.assertEqual(colorSnap((100, 100, 100), ((0, 0, 0), (255, 255, 255))), (0, 0, 0))
        self.assertEqual(colorSnap((235, 210, 255), ((0, 0, 0), (255, 255, 255))), (255, 255, 255))

    def test_returnDistance(self):
        # self.assertAlmostEqual()
        pass # Will finish once framelockon module is complete



if __name__ == '__main__':
    unittest.main()