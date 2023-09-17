import random
from typing import Dict, List, Tuple, Optional, Set

Gen = Tuple[float, ...]
Genes = Dict[str, Gen]

MemberSet = Set['Member']
RelationTree = Dict[int, MemberSet]


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
        if self.alive is False:
            return
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


class Member(Entity):
    def __init__(self, name, year, genetics: Genetics, family: 'Family' = None):
        super().__init__(name, year, genetics)
        self.origin: Optional[Family] = family
        self.families: List[Family] = []

    def add_family(self, family: 'Family'):
        self.families.append(family)

    def as_dict(self):
        exclude = (self.families, self.origin, self.genetics)
        return {k: v for k, v in self.__dict__.items() if v not in exclude}


class Relationship:
    def __init__(self, member: Member):
        self.descendants: RelationTree = {}
        self.ascendants: RelationTree = {}
        self.relatives: RelationTree = {}
        self.__init_relations(member)

    def __init_relations(self, member: Member):
        family = member.origin
        if family is None:
            return
        self.relatives[0] = {child for child in family.children if child is not self}
        self.ascendants[0] = {family.parent_a, family.parent_b}
        self.__set_ascendants(family.parent_a)
        self.__set_ascendants(family.parent_b)
        self.__update_ancestors(member)
        self.__update_relatives(member)

    def __update_relatives(self, member: Member):
        # Adding relatives to all relatives (ancestors siblings)
        for generation, relative_group in self.relatives.items():
            for relative in relative_group:
                if type(relative) is Member:
                    relative_ = relative.relationships
                    relative_.__update_relation_member(relative_.relatives, -generation, member)

    def __update_ancestors(self, member: Member):
        # Adding descendant in all ancestors
        for generation, ancestor_group in self.ascendants.items():
            for ancestor in ancestor_group:
                if type(ancestor) is Member:
                    ancestor_ = ancestor.relationships
                    ancestor_.__update_relation_member(ancestor_.descendants, generation, member)

    def __set_ascendants(self, parent: Member):
        if type(parent) is not Member:
            return
        # Copy ascendants from parent
        for generation, ascendants in parent.relationships.ascendants.items():
            self.__update_relation_tree(self.ascendants, generation + 1, ascendants)
        # Copy relatives from parent
        for generation, relatives in parent.relationships.relatives.items():
            self.__update_relation_tree(self.relatives, generation + 1, relatives)

    @staticmethod
    def __update_relation_tree(relation_tree: RelationTree, generation: int, member_set: MemberSet):
        if generation not in relation_tree:
            relation_tree[generation] = set()
        relation_tree[generation].update(member_set)

    @staticmethod
    def __update_relation_member(relation_tree: RelationTree, generation: int, member: Member):
        if generation not in relation_tree:
            relation_tree[generation] = set()
        relation_tree[generation].add(member)


class Family:
    def __init__(self, parent_a: Member, parent_b: Member):
        self.parent_a: Member = parent_a
        self.parent_b: Member = parent_b
        self.children: List[Member] = []

    def create_child(self, name, year):
        genetics_a = self.parent_a.genetics.get_mutated_crossover_genes()
        genetics_b = self.parent_b.genetics.get_mutated_crossover_genes()
        genetics = Genetics(genetics_a, genetics_b)
        child = Member(name, year, genetics, self)
        self.children.append(child)
        return child

    def get_children_alive(self):
        return [child for child in self.children if child.is_alive()]

    def is_parent(self, entity: Member):
        return self.parent_a is entity or self.parent_b is entity

    def is_child(self, entity: Member):
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
