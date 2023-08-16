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

    def get_children_alive(self, year):
        return [child for child in self.children if child.is_alive(year)]

    def is_parent(self, entity: Entity):
        return self.parent_a is entity or self.parent_b is entity

    def is_child(self, entity: Entity):
        return entity in self.children

    def is_reproducible(self, year):
        if len(self.children) > 0:
            youngest_child = self.children[-1]
            has_newborn = youngest_child.age == 0
        else:
            has_newborn = False
        return (self.parent_a.is_alive(year) and self.parent_b.is_alive(year)
                and not has_newborn)

    def is_parent_alive(self, year):
        return self.parent_a.is_alive(year) or self.parent_b.is_alive(year)

    def is_children_alive(self, year):
        for child in self.children:
            if child.is_alive(year):
                return True
        return False

    def is_family_alive(self, year):
        return self.is_parent_alive(year) or self.is_children_alive(year)


class Status:
    def __init__(self):
        self.parent_family: Family = None
        self.child_family: Family = None


class Survival:
    def __init__(self):
        self.survivors_log: Dict[Entity, Status] = {}
        self.survivors: Dict[Entity, Status] = {}

        self.population = 100
        self.year = 0
        self.free = None

    def generate(self, amount=100):
        for x in range(amount):
            genetics = generate_genetics({
                'health': (0, 0),
                'strength': (0, 0, 0, 0),
                'speed': (0, 0, 0),
                'intelligence': (0, 0, 0, 0, 0)
            })
            entity = Entity(f'Entity{x}', self.year, genetics)
            self.survivors[entity] = Status()

    def survive(self):
        grades = grade_survivors(self.survivors)
        for stats in grades:
            if stats['survive'] is True:
                continue
            entity = stats['entity']
            self.survivor_fallen(entity)

        for survivor, status in self.survivors.items():
            survivor.grow_up()

        for survivor, status in self.survivors.items():
            family = status.parent_family
            if family is not None:
                self.survivor_born(family)
            if survivor.year > 5 and family is None:
                self.survivor_match(survivor)

        amount_alive = len(self.survivors)
        if amount_alive <= self.population:
            amount_missing = self.population - amount_alive
            self.generate(amount_missing)

        self.year += 1

    def survivor_born(self, family: Family):
        if family.is_reproducible(self.year) is False:
            return
        x = len(self.survivors_log) + self.population
        child = family.create_child(f'Child{x}', self.year)
        self.survivors[child] = Status()
        self.survivors[child].child_family = family

    def survivor_fallen(self, survivor: Entity):
        status = self.survivors.pop(survivor)
        self.survivors_log[survivor] = status

    def survivor_match(self, survivor):
        if self.free is None:
            self.free = survivor
            return
        partner = self.free
        if partner is survivor:
            return
        family = Family(partner, survivor)
        self.survivors[partner].parent_family = family
        self.survivors[survivor].parent_family = family
        self.free = None


def grade_survivors(survivors):
    grades: List[dict] = []
    for entity in survivors:
        points = grade_entity(entity)
        statistics = {
            'entity': entity,
            'points': points,
        }
        grades.append(statistics)
    minimum = min(grades, key=lambda stats: stats['points'])['points']
    maximum = max(grades, key=lambda stats: stats['points'])['points']
    point_range = maximum - minimum
    for stats in grades:
        points = stats['points']
        stats['grade'] = (points - minimum) / point_range
        stats['survive'] = random.random() < stats['grade']
    return grades


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
