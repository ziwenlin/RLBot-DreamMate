from unittest import TestCase

from util.vec import Vec3


class Test(TestCase):
    def test_vec3_a(self):
        self.assertEqual(Vec3(), Vec3())

    def test_vec3_b(self):
        self.assertFalse(Vec3() is Vec3())

    def test_vec3_c(self):
        self.assertTrue(Vec3() == Vec3())
