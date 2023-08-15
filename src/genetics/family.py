import random
from typing import Dict, List, Tuple

GENE = Tuple[float, ...]
GENETICS = Dict[str, GENE]


class Genetics:
    def __init__(self, genetics_a, genetics_b):
        self.genetics_a: GENETICS = genetics_a
        self.genetics_b: GENETICS = genetics_b

    def mutation(self, probability=0.001):
        group_keys = self.genetics_a.keys()
        for group in group_keys:
            if random.random() > probability:
                continue
            choice = random.random()
            mutation = random.random() + 0.5
            self.mutation_gene(group, choice, mutation)

    def mutation_gene(self, group: str, choice: float, mutation: float):
        gene = list(self.get_gene_copy(group, choice))
        index = random.randrange(len(gene))
        gene[index] *= mutation
        self.set_gene(group, choice, tuple(gene))

    def get_genetics(self):
        group_keys = self.genetics_a.keys()
        genetics: GENETICS = {group: self.get_gene(group) for group in group_keys}
        return genetics

    def get_genetics_copy(self):
        group_keys = self.genetics_a.keys()
        group_choice = {group: random.Random() for group in group_keys}
        genetics: GENETICS = {
            group: self.get_gene_copy(group, choice)
            for group, choice in group_choice.items()
        }
        return genetics

    def get_gene(self, group: str):
        gene_a = self.genetics_a[group]
        gene_b = self.genetics_b[group]
        gene: GENE = tuple((a + b) / 2 for a, b in zip(gene_a, gene_b))
        return gene

    def set_gene(self, group: str, choice: float, gene: GENE):
        if choice < 0.5:
            self.genetics_a[group] = gene
        else:
            self.genetics_b[group] = gene

    def get_gene_copy(self, group: str, choice: float):
        if choice < 0.5:
            gene = self.genetics_a[group]
        else:
            gene = self.genetics_b[group]
        return gene


class Entity:
    def __init__(self, name, year, genetics: Genetics):
        self.year = year
        self.name = name
        self.age = 0
        self.genetics = genetics

    def grow_up(self):
        self.age += 1

    def is_alive(self, year):
        return self.year + self.age == year


class Family:
    def __init__(self, parent_a: Entity, parent_b: Entity):
        self.parent_a = parent_a
        self.parent_b = parent_b
        self.children: List[Entity] = []

    def create_child(self, name, year):
        genetics_a = self.parent_a.genetics.get_genetics_copy()
        genetics_b = self.parent_b.genetics.get_genetics_copy()
        genetics = Genetics(genetics_a, genetics_b)
        child = Entity(name, year, genetics)
        self.children.append(child)
        return child

    def is_parent(self, entity: Entity):
        return self.parent_a is entity or self.parent_b is entity

    def is_child(self, entity: Entity):
        return entity in self.children

    def is_parent_alive(self, year):
        return self.parent_a.is_alive(year) and self.parent_b.is_alive(year)


class Survival:
    def __init__(self):
        self.families_fallen: List[Family] = []
        self.families_alive: List[Family] = []
        self.entities_fallen: List[Entity] = []
        self.entities_alive: List[Entity] = []

    def generate(self):
        for x in range(100):
            genetics = generate_genetics({
                'health': (0, 0),
                'strength': (0, 0, 0, 0),
                'speed': (0, 0, 0),
                'intelligence': (0, 0, 0, 0, 0)
            })
            entity = Entity(f'Entity{x}', 0, genetics)
            self.entities_alive.append(entity)

    def survive(self):
        for entity in self.entities_alive:
            points = grade_entity(entity)
            pass


def generate_genetics(genetics):
    templates: GENETICS = {
        group: tuple(random.random() - 0.5 for _ in range(len(gene)))
        for group, gene in genetics.items()
    }
    return Genetics(templates, templates)


def grade_entity(entity):
    points = 0
    genetics = entity.genetics.get_genetics()
    health, resistance = genetics['health']
    strength, durability, block, weight = genetics['strength']
    speed, agility = genetics['speed']
    intelligence, courage, creativity, skill, prediction = genetics['intelligence']

    points += grade_multiplication(health, strength)
    points += grade_multiplication(health, durability)
    points += grade_multiplication(health, weight)

    points += grade_opposed(strength, weight)
    points += grade_opposed(courage, weight)
    points += grade_opposed(block, weight)

    points += grade_multiplication(speed, agility)
    points += grade_opposed(speed, weight)
    points += grade_opposed(agility, weight)

    points += grade_multiplication(prediction, speed)
    points += grade_multiplication(prediction, intelligence)
    points += grade_multiplication(skill, agility)
    points += grade_multiplication(skill, creativity)
    points += grade_multiplication(skill, block)
    points += grade_opposed(creativity, resistance)
    points += grade_opposed(intelligence, strength)

    return points


def grade_opposed(positive, negative):
    if positive - negative == 0:
        return 0
    return positive / (positive - negative)


def grade_multiplication(positive, multiplication):
    if positive + multiplication == 0:
        return 0
    return positive * multiplication / (positive + multiplication)