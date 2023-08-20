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
        self.name = name
        self.year = year
        self.age = 0
        self.alive = True
        self.genetics = genetics

    def step(self, alive: bool):
        if alive is False:
            self.alive = False
            return
        self.age += 1

    def is_alive(self):
        return self.alive

    def __repr__(self):
        return str({k: v for k, v in self.__dict__.items() if v is not self.genetics})


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

    def get_children_alive(self):
        return [child for child in self.children if child.is_alive()]

    def is_parent(self, entity: Entity):
        return self.parent_a is entity or self.parent_b is entity

    def is_child(self, entity: Entity):
        return entity in self.children

    def is_reproducible(self):
        if len(self.children) > 0:
            youngest_child = self.children[-1]
            has_newborn = youngest_child.age == 0
        else:
            has_newborn = False
        return self.is_partner_alive() and not has_newborn

    def is_parent_alive(self):
        return self.parent_a.is_alive() or self.parent_b.is_alive()

    def is_partner_alive(self):
        return self.parent_a.is_alive() and self.parent_b.is_alive()

    def is_children_alive(self):
        for child in self.children:
            if child.is_alive():
                return True
        return False

    def is_family_alive(self):
        return self.is_partner_alive() or self.is_children_alive()


def generate_genetics(genetics):
    templates: GENETICS = {
        group: tuple(random.random() - 0.5 for _ in range(len(gene)))
        for group, gene in genetics.items()
    }
    return Genetics(templates, templates)
