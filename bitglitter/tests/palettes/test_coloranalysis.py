import unittest
from bitglitter.read.coloranalysis import color_snap, return_distance


class Test(unittest.TestCase):

    # Return the correct color with both zero changes in value, and 'dirty' values.
    def test_colorSnap(self):
        self.assertEqual(color_snap((0, 0, 0), ((0, 0, 0), (255, 255, 255))), (0, 0, 0))
        self.assertEqual(color_snap((100, 100, 100), ((0, 0, 0), (255, 255, 255))), (0, 0, 0))
        self.assertEqual(color_snap((235, 210, 255), ((0, 0, 0), (255, 255, 255))), (255, 255, 255))

    def test_returnDistance(self):
        # self.assertAlmostEqual()
        pass # Will finish once framelockon module is complete



if __name__ == '__main__':
    unittest.main()