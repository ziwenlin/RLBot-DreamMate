from unittest import TestCase

from tools.helper import clip_to_box
from util.vec import Vec3


class Test(TestCase):
    def test_vec3_a(self):
        self.assertEqual(Vec3(), Vec3())

    def test_vec3_b(self):
        self.assertFalse(Vec3() is Vec3())

    def test_vec3_c(self):
        self.assertTrue(Vec3() == Vec3())

    def test_clip_to_box(self):
        mid_p = Vec3(10, 20, 30)
        mid_n = Vec3(-10, -20, 0)
        result = clip_to_box(Vec3(0, 0, 0), mid_p, mid_n)
        self.assertEqual(Vec3(0, 0, 0), result)

        result = clip_to_box(Vec3(30, 0, 0), mid_p, mid_n)
        self.assertEqual(Vec3(10, 0, 0), result)

        result = clip_to_box(Vec3(30, -30, 0), mid_p, mid_n)
        self.assertEqual(Vec3(10, -20, 0), result)

        result = clip_to_box(Vec3(30, -30, -10), mid_p, mid_n)
        self.assertEqual(Vec3(10, -20, 0), result)
