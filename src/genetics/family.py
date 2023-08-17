import random
from typing import Dict, List, Tuple, Optional

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
        group_choice = {group: random.random() for group in group_keys}
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

    def __repr__(self):
        return f'{self.name} Year:{self.year} Age:{self.age}'


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
        return self.is_partner_alive(year) and not has_newborn

    def is_parent_alive(self, year):
        return self.parent_a.is_alive(year) or self.parent_b.is_alive(year)

    def is_partner_alive(self, year):
        return self.parent_a.is_alive(year) and self.parent_b.is_alive(year)

    def is_children_alive(self, year):
        for child in self.children:
            if child.is_alive(year):
                return True
        return False

    def is_family_alive(self, year):
        return self.is_partner_alive(year) or self.is_children_alive(year)


class Survivor:
    def __init__(self, entity: Entity):
        self.entity = entity
        self.points = 0.0
        self.score = 0.0
        self.vitality = 0.0
        self.alive = True

    def set_vitality(self, vitality: float):
        self.vitality = vitality

    def set_points(self, points: float):
        self.points = points

    def set_score(self, score: float):
        self.score = score

    def __str__(self):
        return f'entity: {self.entity},\t' \
               f'points: {self.points:.2f},\t' \
               f'score: {self.score:.2f},\t' \
               f'vitality: {self.vitality:.2f}\t' \
               f'alive: {self.alive}'


class Archive:
    def __init__(self, survivor: Survivor):
        self.survivor = survivor
        self.families: List[Family] = []
        self.origin: Optional[Family] = None
        self.current_family: Optional[Family] = None

    def register_origin(self, family: Family):
        self.origin = family

    def register_family(self, family: Family):
        self.families.append(family)
        self.current_family = family

    def has_active_family(self, year):
        if self.current_family is None:
            return False
        if self.current_family.is_family_alive(year) is True:
            return True
        self.current_family = None
        return False

    def is_looking_for_mate(self, year):
        return self.has_active_family(year) is False


class Survival:
    def __init__(self, population_max=100):
        self.survivors_log: Dict[Survivor, Archive] = {}
        self.survivors: Dict[Survivor, Archive] = {}
        self.looking_for_mate: List[Survivor] = []

        self.population_max = population_max
        self.population_current = 0
        self.log_count = 0
        self.year = 0

    def get_survivors(self):
        return list(self.survivors)

    def generate(self):
        amount = self.population_max - self.population_current
        if amount < 0:
            return 0
        for x in range(amount):
            genetics = generate_genetics({
                'health': (0, 0),
                'strength': (0, 0, 0, 0),
                'speed': (0, 0, 0),
                'intelligence': (0, 0, 0, 0, 0)
            })
            entity = Entity(f'Entity{self.log_count}', self.year, genetics)
            self.survivor_record(entity)
        self.population_current += amount
        return amount

    def reproduce(self):
        amount_alive = len(self.survivors)
        amount_missing = self.population_current - amount_alive
        self.population_current += -amount_missing
        if self.population_max < amount_alive:
            return (self.population_current, amount_alive, amount_missing, 0, 0)
        amount_born = 0
        for survivor in list(self.survivors):
            family = self.survivors[survivor].current_family
            if family is None:
                continue
            self.survivor_born(family)
            amount_born += 1
        self.population_current += amount_born
        amount_generated = self.generate()

        return (self.population_current, amount_alive, amount_missing,
                amount_born, amount_generated,)

    def survive(self):
        survivors = self.get_survivors()
        for survivor in survivors:
            if survivor.alive is False:
                self.survivor_fallen(survivor)
                continue
            survivor.entity.grow_up()
            self.survivor_matching(survivor)
        self.survivor_pairing()

        self.year += 1
        return survivors

    def survivor_record(self, entity: Entity, family: Optional[Family] = None):
        survivor = Survivor(entity)
        self.survivors[survivor] = archive = Archive(survivor)
        if family is None:
            return
        archive.register_family(family)
        self.log_count += 1

    def survivor_born(self, family: Family):
        if family.is_reproducible(self.year) is False:
            return
        child = family.create_child(f'Child{self.log_count}', self.year)
        self.survivor_record(child, family)

    def survivor_fallen(self, survivor: Survivor):
        status = self.survivors.pop(survivor)
        self.survivors_log[survivor] = status
        if survivor in self.looking_for_mate:
            self.looking_for_mate.remove(survivor)

    def survivor_matching(self, survivor: Survivor):
        if survivor in self.looking_for_mate:
            return True
        if survivor.entity.age < 5:
            return False
        status = self.survivors[survivor]
        if status.is_looking_for_mate(self.year) is False:
            return False
        self.looking_for_mate.append(survivor)
        return True

    def survivor_pairing(self):
        amount_potential_mates = len(self.looking_for_mate)
        if amount_potential_mates < 2:
            return
        amount_potential_pairs = amount_potential_mates // 2
        for _ in range(amount_potential_pairs):
            partner_a = self.select_best_mate()
            partner_b = self.select_best_mate()
            family = Family(partner_a.entity, partner_b.entity)
            self.survivors[partner_a].register_family(family)
            self.survivors[partner_b].register_family(family)

    def select_best_mate(self):
        def filter_score(stats: Survivor):
            return stats.points

        survivor = max(self.looking_for_mate, key=filter_score)
        self.looking_for_mate.remove(survivor)
        return survivor

    def evaluate(self, survivors: List[Survivor]):
        def filter_score(stats: Survivor):
            return stats.points

        minimum = min(survivors, key=filter_score).points
        maximum = max(survivors, key=filter_score).points
        average = sum(list(stats.points for stats in survivors)) / len(survivors)
        average_range = average - minimum
        middle_range = maximum - minimum
        for stats in survivors:
            points = stats.points
            score = (points - minimum) / middle_range
            vitality = (points - minimum) / average_range
            stats.set_score(score)
            stats.set_vitality(vitality)
            stats.alive = vitality > random.random()
        return survivors


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
    average = sum(list(grade['points'] for grade in grades)) / len(grades)
    average_range = average - minimum
    for stats in grades:
        points = stats['points']
        stats['grade'] = (points - minimum) / point_range
        stats['score'] = (points - minimum) / average_range
        stats['survive'] = random.random() < stats['score']
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
    speed, agility, endurance = genetics['speed']
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
