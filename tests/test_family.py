import random
from unittest import TestCase
from unittest.mock import patch

from genetics.family import Entity, Template, Genetics, Genes


class CustomTemplate(Template):
    def __init__(self):
        self.foo = 2
        self.bar = 3


class TestGenetics(TestCase):
    def setUp(self):
        random.seed(0)
        gene_a = {'foo': (1, 2, 3), 'bar': (0, 0, 0), 'foobar': (3, 2, 1)}
        gene_b = {'foo': (4, 5, 6), 'bar': (2, 2, 2), 'foobar': (1, 2, 3)}
        self.genetics = Genetics(gene_a, gene_b)

    def test_get_joint_genes(self):
        genes = self.genetics.get_joint_genes()
        self.assertEqual({'foo': (2.5, 3.5, 4.5), 'bar': (1, 1, 1), 'foobar': (2, 2, 2)}, genes)

    def test_get_crossover_genes(self):
        genes = self.genetics.get_crossover_genes()
        self.assertEqual({'foo': (4, 5, 6), 'bar': (2, 2, 2), 'foobar': (3, 2, 1)}, genes)

    def test_get_mutated_crossover_genes_1(self):
        with patch('random.uniform') as mocked_random:
            mocked_random.return_value = 1.5
            genes = self.genetics.get_mutated_crossover_genes()
        self.assertEqual({'foo': (4, 5, 6), 'bar': (3, 3, 3), 'foobar': (3, 2, 1)}, genes)

    def test_get_mutated_crossover_genes_2(self):
        with patch('random.uniform') as mocked_random:
            mocked_random.return_value = 0.5
            genes = self.genetics.get_mutated_crossover_genes()
        self.assertEqual({'foo': (4, 5, 6), 'bar': (1, 1, 1), 'foobar': (3, 2, 1)}, genes)


class TestEntity(TestCase):
    def setUp(self):
        random.seed(0)
        template = CustomTemplate()
        self.foo = Entity('Foo', 0, template.generate())
        self.bar = Entity('Bar', 1, template.generate())

    def test_as_dict(self):
        self.assertEqual({'name': 'Foo', 'age': 0, 'year': 0, 'alive': True}, self.foo.as_dict())
        self.assertEqual({'name': 'Bar', 'age': 0, 'year': 1, 'alive': True}, self.bar.as_dict())

    def test_step(self):
        self.foo.step(True)
        self.assertEqual({'name': 'Foo', 'age': 1, 'year': 0, 'alive': True}, self.foo.as_dict())
        self.bar.step(False)
        self.assertEqual({'name': 'Bar', 'age': 0, 'year': 1, 'alive': False}, self.bar.as_dict())

    def test_step_while_dead(self):
        self.foo.step(False)
        self.foo.step(True)
        self.assertFalse(self.foo.is_alive(), 'Foo should be dead')
        self.assertEqual(0, self.foo.age, 'Foo should not age when he is dead')
        self.assertEqual(0, self.foo.year, 'Foo birth year should not change')

    def test_is_alive(self):
        self.foo.step(True)
        self.bar.step(False)
        self.assertTrue(self.foo.is_alive(), 'Foo should be alive')
        self.assertFalse(self.bar.is_alive(), 'Bar should be dead')


class TestTemplate(TestCase):
    def setUp(self):
        self.template = CustomTemplate()

    def tearDown(self):
        pass

    def test_generate_type(self):
        genetics = self.template.generate()

        self.assertIs(type(genetics), Genetics)
        self.assertIs(type(genetics.genes_a), dict)
        self.assertIs(type(genetics.genes_b), dict)

    def test_generate_genetics_1(self):
        with patch('random.random') as mocked_random:
            mocked_random.return_value = 0.5
            genetics = self.template.generate()

        self.assertEqual({'foo': (0.0, 0.0), 'bar': (0.0, 0.0, 0.0)}, genetics.genes_a)
        self.assertEqual({'foo': (0.0, 0.0), 'bar': (0.0, 0.0, 0.0)}, genetics.genes_b)

    def test_generate_genetics_2(self):
        with patch('random.random') as mocked_random:
            mocked_random.return_value = 1.0
            genetics = self.template.generate()

        self.assertEqual({'foo': (0.5, 0.5), 'bar': (0.5, 0.5, 0.5)}, genetics.genes_a)
        self.assertEqual({'foo': (0.5, 0.5), 'bar': (0.5, 0.5, 0.5)}, genetics.genes_b)

    def test_generate_genetics_3(self):
        with patch('random.random') as mocked_random:
            mocked_random.return_value = 0.0
            genetics = self.template.generate()

        self.assertEqual({'foo': (-0.5, -0.5), 'bar': (-0.5, -0.5, -0.5)}, genetics.genes_a)
        self.assertEqual({'foo': (-0.5, -0.5), 'bar': (-0.5, -0.5, -0.5)}, genetics.genes_b)
