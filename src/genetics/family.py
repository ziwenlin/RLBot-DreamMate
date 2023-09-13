import random
from typing import Dict, List, Tuple

Gen = Tuple[float, ...]
Genes = Dict[str, Gen]


class Genetics:
    def __init__(self, gene_a: Genes, gene_b: Genes):
        self.genes_a: Genes = gene_a
        self.genes_b: Genes = gene_b

    def get_mutated_crossover_genes(self):
        genes = self.get_crossover_genes()
        trait = random.choice(tuple(genes))
        genes[trait] = tuple(
            value * random.uniform(0.5, 1.5)
            for value in genes[trait]
        )
        return genes

    def get_crossover_genes(self):
        trait_names = self.genes_a.keys()
        genes_choice = (self.genes_a, self.genes_b)
        genes: Genes = {
            trait: random.choice(genes_choice)[trait]
            for trait in trait_names
        }
        return genes

    def get_joint_genes(self):
        trait_names = self.genes_a.keys()
        genes: Genes = {
            trait: self.__get_joint_gen(trait)
            for trait in trait_names
        }
        return genes

    def __get_joint_gen(self, trait: str):
        genes_pair = zip(self.genes_a[trait], self.genes_b[trait])
        joint_gen: Gen = tuple((a + b) / 2 for a, b in genes_pair)
        return joint_gen

    def __repr__(self):
        trait_names = self.genes_a.keys()
        return str({
            trait: tuple(
                (round(a + b, 3) / 2, round(a, 4), round(b, 4))
                for a, b in zip(self.genes_a[trait], self.genes_b[trait]))
            for trait in trait_names
        })


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

    def as_dict(self):
        exclude = (self.genetics,)
        return {k: v for k, v in self.__dict__.items() if v not in exclude}

    def __repr__(self):
        return str(self.as_dict())


class Family:
    def __init__(self, parent_a: Entity, parent_b: Entity):
        self.parent_a = parent_a
        self.parent_b = parent_b
        self.children: List[Entity] = []

    def create_child(self, name, year):
        genetics_a = self.parent_a.genetics.get_mutated_crossover_genes()
        genetics_b = self.parent_b.genetics.get_mutated_crossover_genes()
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


class Template:
    def generate(self):
        templates: Genes = {
            group: tuple(random.random() - 0.5 for _ in range(size))
            for group, size in self.__dict__.items()}
        return Genetics(templates, templates)
