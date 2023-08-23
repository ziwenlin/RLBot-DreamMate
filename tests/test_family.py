from unittest import TestCase
from unittest.mock import patch

from genetics.family import Entity, Template, Genetics, GENETICS


class CustomTemplate(Template):
    def __init__(self):
        self.foo = 2
        self.bar = 3


class TestTemplate(TestCase):
    def setUp(self):
        self.template = CustomTemplate()

    def tearDown(self):
        pass

    def test_generate_type(self):
        genetics = self.template.generate()

        self.assertIs(type(genetics), Genetics)
        self.assertIs(type(genetics.genetics_a), dict)
        self.assertIs(type(genetics.genetics_b), dict)

    def test_generate_genetics_1(self):
        with patch('random.random') as mocked_random:
            mocked_random.return_value = 0.5
            genetics = self.template.generate()

        self.assertEqual(genetics.genetics_a, {'foo': (0.0, 0.0), 'bar': (0.0, 0.0, 0.0)})
        self.assertEqual(genetics.genetics_b, {'foo': (0.0, 0.0), 'bar': (0.0, 0.0, 0.0)})

    def test_generate_genetics_2(self):
        with patch('random.random') as mocked_random:
            mocked_random.return_value = 1.0
            genetics = self.template.generate()

        self.assertEqual(genetics.genetics_a, {'foo': (0.5, 0.5), 'bar': (0.5, 0.5, 0.5)})
        self.assertEqual(genetics.genetics_b, {'foo': (0.5, 0.5), 'bar': (0.5, 0.5, 0.5)})

    def test_generate_genetics_3(self):
        with patch('random.random') as mocked_random:
            mocked_random.return_value = 0.0
            genetics = self.template.generate()

        self.assertEqual(genetics.genetics_a, {'foo': ((-0.5), (-0.5)), 'bar': ((-0.5), (-0.5), (-0.5))})
        self.assertEqual(genetics.genetics_b, {'foo': ((-0.5), (-0.5)), 'bar': ((-0.5), (-0.5), (-0.5))})
