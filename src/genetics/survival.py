import random
from typing import Dict, List, Optional

from genetics.family import Entity, generate_genetics, Family


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

    def __repr__(self):
        return str({k: round(v, 2) if type(v) is float else v
                    for k, v in self.__dict__.items()})


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
        if self.current_family.is_family_alive() is True:
            return True
        self.current_family = None
        return False

    def is_looking_for_mate(self):
        if self.current_family is None:
            return True
        return self.current_family.is_partner_alive() is False


class Archive:
    def __init__(self):
        self.survivor_log: Dict[Entity, Survivor] = {}
        self.register_log: Dict[Survivor, Register] = {}

    def create_record(self, survivor: Survivor, archive: Register):
        self.survivor_log[survivor.entity] = survivor
        self.register_log[survivor] = archive

    def get_archive(self, entity: Entity):
        survivor = self.survivor_log.get(entity)
        archive = self.register_log.get(survivor)
        return archive

    def get_survivor(self, entity: Entity):
        return self.survivor_log.get(entity)

    def get_origin(self, entity: Entity):
        archive = self.get_archive(entity)
        return archive.origin

    def get_family(self, entity: Entity):
        archive = self.get_archive(entity)
        return archive.current_family


class Matcher:
    def __init__(self, archive: Archive):
        self.looking_for_mate: List[Survivor] = []
        self.archive: archive = archive

    def start_dating(self, survivor: Survivor):
        if survivor in self.looking_for_mate:
            return True
        if survivor.entity.age < 5:
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
        amount_potential_pairs = amount_potential_mates // 2
        for _ in range(amount_potential_pairs):
            partner_a = self.find_best_partner()
            partner_b = self.find_best_partner()
            family = Family(partner_a.entity, partner_b.entity)
            self.archive.get_archive(partner_a.entity).register_family(family)
            self.archive.get_archive(partner_b.entity).register_family(family)

    def find_best_partner(self):
        # Work in process: add logic avoiding incest
        def filter_score(stats: Survivor):
            return stats.points

        survivor = max(self.looking_for_mate, key=filter_score)
        self.looking_for_mate.remove(survivor)
        return survivor

    def remove(self, survivor):
        if survivor in self.looking_for_mate:
            self.looking_for_mate.remove(survivor)


class Survival:
    def __init__(self, population_max=100):
        self.survivors: Dict[Survivor, Register] = {}
        self.archive = archive = Archive()
        self.matcher = Matcher(archive)

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
                # to be done: make it simple
                # and supplied from the outside code
                # not hard coded
                'health': (0, 0),
                'strength': (0, 0, 0, 0),
                'speed': (0, 0, 0),
                'intelligence': (0, 0, 0, 0, 0)
            })
            entity = Entity(f'Entity {self.log_count}', self.year, genetics)
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
            survivor.entity.step(survivor.alive)
            if survivor.alive is False:
                self.survivor_fallen(survivor)
                continue
            self.survivor_matching(survivor)
        self.survivor_pairing()

        self.year += 1
        return survivors

    def survivor_record(self, entity: Entity, family: Optional[Family] = None):
        survivor = Survivor(entity)
        register = Register(survivor)
        self.survivors[survivor] = register
        self.archive.create_record(survivor, register)
        self.log_count += 1
        if family is None:
            return
        register.register_family(family)

    def survivor_born(self, family: Family):
        if family.is_reproducible() is False:
            return
        child = family.create_child(f'Child {self.log_count}', self.year)
        self.survivor_record(child, family)

    def survivor_fallen(self, survivor: Survivor):
        self.survivors.pop(survivor)
        self.matcher.remove(survivor)

    def survivor_matching(self, survivor: Survivor):
        self.matcher.start_dating(survivor)

    def survivor_pairing(self):
        self.matcher.create_pairs()

    def evaluate(self):
        def get_points(stats: Survivor):
            return stats.points

        survivors = self.get_survivors()
        minimum = min(survivors, key=get_points).points
        maximum = max(survivors, key=get_points).points
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
