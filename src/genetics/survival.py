import random
from typing import Dict, List, Optional

import numpy

from genetics.family import Member, Family, Template, Genetics


class Survivor:
    def __init__(self, entity: Member):
        self.entity = entity
        self.points = 0.0
        self.score = 0.0
        self.vitality = 0.0
        self.alive = True

    def update(self, score: float, vitality: float, alive: bool):
        self.vitality = vitality
        self.score = score
        self.alive = alive

    def set_vitality(self, vitality: float):
        self.vitality = vitality

    def set_points(self, points: float):
        self.points = points

    def set_score(self, score: float):
        self.score = score

    def __repr__(self):
        alive = 'Yes' if self.alive else 'No'
        return f'{str(self.entity):<40} Points:{self.points:.1f} Score:{self.score:.2f} ' \
               f'Vitality:{self.vitality:.2f} Survive:{alive}'


class Register:
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

    def has_active_family(self):
        if self.current_family is None:
            return False
        if self.current_family.is_partner_alive() is True:
            return True
        self.current_family = None
        return False

    def is_looking_for_mate(self):
        if self.current_family is None:
            return True
        return self.current_family.is_partner_alive() is False


class Archive:
    def __init__(self):
        self.survivor_log: Dict[Member, Survivor] = {}
        self.register_log: Dict[Survivor, Register] = {}

    def create_record(self, survivor: Survivor, archive: Register):
        self.survivor_log[survivor.entity] = survivor
        self.register_log[survivor] = archive

    def get_archive(self, entity: Member):
        survivor = self.survivor_log.get(entity)
        archive = self.register_log.get(survivor)
        return archive

    def get_survivor(self, entity: Member):
        return self.survivor_log.get(entity)

    def get_origin(self, entity: Member):
        archive = self.get_archive(entity)
        return archive.origin

    def get_family(self, entity: Member):
        archive = self.get_archive(entity)
        return archive.current_family


class Matcher:
    def __init__(self, archive: Archive, pairing_age: int):
        self.looking_for_mate: List[Survivor] = []
        self.archive: archive = archive
        self.pairing_age: int = pairing_age

    def start_dating(self, survivor: Survivor):
        if survivor in self.looking_for_mate:
            return True
        if survivor.entity.age < self.pairing_age:
            return False
        status = self.archive.get_archive(survivor.entity)
        if status.is_looking_for_mate() is False:
            return False
        self.looking_for_mate.append(survivor)
        return True

    def create_pairs(self):
        amount_potential_mates = len(self.looking_for_mate)
        if amount_potential_mates < 2:
            return
        # Work in process: Add logic to prevent incest between matches
        self.sort_best_partner()
        amount_potential_pairs = amount_potential_mates // 2 - 1
        for _ in range(amount_potential_pairs):
            partner_a = self.find_best_partner()
            partner_b = self.find_best_partner()
            family = Family(partner_a.entity, partner_b.entity)
            self.archive.get_archive(partner_a.entity).register_family(family)
            self.archive.get_archive(partner_b.entity).register_family(family)

    def sort_best_partner(self):
        def filter_score(stats: Survivor):
            return stats.points

        self.looking_for_mate.sort(key=filter_score, reverse=True)

    def find_best_partner(self):
        survivor = self.looking_for_mate.pop(0)
        if survivor.alive is False:
            return self.find_best_partner()
        return survivor

    def remove(self, survivor):
        if survivor in self.looking_for_mate:
            self.looking_for_mate.remove(survivor)


class Scores:
    def __init__(self):
        self.best: float = 0
        self.median: float = 0
        self.middle: float = 0
        self.average: float = 0
        self.worst: float = 0

    def __add__(self, other: 'Scores'):
        score = Scores()
        for keys in score.__dict__:
            score.__dict__[keys] = self.__dict__[keys] + other.__dict__[keys]
        return score

    def __sub__(self, other: 'Scores'):
        score = Scores()
        for keys in score.__dict__:
            score.__dict__[keys] = self.__dict__[keys] - other.__dict__[keys]
        return score

    def __repr__(self):
        return str({key: round(value, 3) for key, value in self.__dict__.items()})


class Observer:
    def __init__(self):
        self.history: List[List[Survivor]] = []
        self.scores: List[Scores] = []

    def progression(self):
        # Attempt programming progression
        # This function is not done
        try:
            current = self.scores[-1]
            previous = self.scores[-2]
        except IndexError:
            return 0
        performance = current - previous
        return (performance.average - performance.worst) / (performance.median - performance.worst)

    def evaluate(self, points: List[float]):
        scores = Scores()

        scores.best = max(points)
        scores.worst = min(points)
        scores.median = float(numpy.median(points))
        scores.middle = (scores.best + scores.worst) / 2
        scores.average = sum(points) / len(points)

        self.scores.append(scores)
        return scores


class Population:
    def __init__(self, population_max, pairing_age):
        self.archive = archive = Archive()
        self.matcher = Matcher(archive, pairing_age)
        self.survivors: List[Survivor] = []
        self.register: Dict[Survivor, Register] = {}

        self.population_current = 0
        self.population_max = population_max
        self.log_count = 0

    def survivor_record(self, entity: Member, family: Optional[Family] = None):
        survivor = Survivor(entity)
        register = Register(survivor)
        self.survivors.append(survivor)
        self.register[survivor] = register
        self.archive.create_record(survivor, register)
        self.population_current += 1
        self.log_count += 1
        if family is None:
            return
        register.register_family(family)

    def survivor_generate(self, year: int, genetics: Genetics):
        entity = Member(f'Entity {self.log_count}', year, genetics)
        self.survivor_record(entity)

    def survivor_born(self, year: int, family: Family):
        if family.is_reproducible() is False:
            return False
        child = family.create_child(f'Child {self.log_count}', year)
        self.survivor_record(child, family)
        return True

    def survivor_fallen(self, survivor: Survivor):
        self.survivors.remove(survivor)
        self.matcher.remove(survivor)
        self.population_current += -1


class Survival:
    def __init__(self, template: Template, population_max=100, pairing_age=2):
        self.population = Population(population_max, pairing_age)
        self.observer = Observer()
        self.genetics = template
        self.year = 0

    def generate(self):
        amount = self.statistics()['missing']
        if amount < 0:
            return 0
        for x in range(amount):
            self.population.survivor_generate(self.year, self.genetics.generate())
        return amount

    def statistics(self):
        amount_alive = self.population.population_current
        amount_missing = self.population.population_max - amount_alive
        amount_born = amount_missing // 2
        amount_generated = amount_missing - amount_born
        return {'alive': amount_alive, 'missing': amount_missing,
                'born': amount_born, 'generated': amount_generated, }

    def reproduce(self):
        statistics = self.statistics()
        amount_born = 0
        for survivor in self.population.survivors.copy():
            if amount_born >= statistics['missing']:
                break
            family = self.population.register[survivor].current_family
            if family is None:
                continue
            has_reproduced = self.population.survivor_born(self.year, family)
            if has_reproduced is False:
                continue
            amount_born += 1
        return amount_born

    def survive(self):
        survivors = self.population.survivors.copy()
        for survivor in survivors:
            survivor.entity.step(survivor.alive)
            if survivor.alive is False:
                self.population.survivor_fallen(survivor)
                continue
            self.population.matcher.start_dating(survivor)
        self.population.matcher.create_pairs()

        self.year += 1
        return survivors

    def evaluate(self):
        survivors = self.population.survivors
        points = list(stats.points for stats in survivors)
        scores = self.observer.evaluate(points)
        scores.worst += -1

        average_range = scores.average - scores.worst
        middle_range = scores.best - scores.worst
        median_range = scores.median - scores.worst
        for stats in survivors:
            score = (stats.points - scores.worst) / middle_range
            vitality = (stats.points - scores.worst) / average_range
            survival = vitality > random.random()
            stats.update(score, vitality, survival)
        return scores
