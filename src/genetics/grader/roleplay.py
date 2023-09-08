"""
This grader is based on logic of roleplaying games.
"""
from genetics.family import Template, Entity


class Attributes(Template):
    def __init__(self):
        self.health = 2
        self.strength = 4
        self.speed = 3
        self.intelligence = 5


class Creature:
    def __init__(self, hp, ap, mp, bp, ec, se, it):
        self.hitpoints = hp
        self.attack_power = ap
        self.magic_power = mp
        self.block_power = bp
        self.evade_chance = ec
        self.spirit_energy = se
        self.instinct_talent = it

        self.health = 100
        self.stamina = 100
        self.magica = 100
        self.evasion = 100

    def regenerate(self):
        heal = (self.magic_power + self.instinct_talent) / 10
        self.health = heal / self.hitpoints
        if self.health > 100:
            self.health = 100

        restore = self.magic_power / 10
        self.magica = restore / self.spirit_energy
        if self.magica > 100:
            self.magica = 100

        recover = self.spirit_energy / 10
        self.stamina = recover / self.hitpoints
        if self.stamina > 100:
            self.stamina = 100

    def evade(self, damage):
        evade = damage / self.evade_chance
        self.evasion += -evade
        if self.evasion < 0:
            self.evasion = 100
            return False
        return True

    def attack(self, entity: 'Creature'):
        if self.stamina < 0:
            return
        self.stamina -= 1

        if entity.evade(self.attack_power):
            return

        damage = self.attack_power / entity.block_power
        entity.health -= damage / entity.hitpoints

    def magic(self, entity: 'Creature'):
        if self.magica < 0:
            return
        self.magica -= 1

        if entity.evade(self.magic_power):
            return

        damage = (self.magic_power + self.instinct_talent) / (entity.block_power + entity.instinct_talent)
        entity.health -= damage / entity.hitpoints

    def is_alive(self):
        return self.health > 0

    def is_exhausted(self):
        return not self.stamina > 0

    def is_depleted(self):
        return not self.magica > 0

    def __repr__(self):
        return f"HP:{self.health:.2f} MP:{self.magica:.2f} SP:{self.stamina:.2f}"


def spawn_player(attributes: dict):
    health, resistance = attributes['health']
    strength, durability, block, weight = attributes['strength']
    speed, agility, endurance = attributes['speed']
    intelligence, courage, creativity, skill, prediction = attributes['intelligence']

    hitpoints = abs(health * resistance * durability)
    attack_power = abs(strength * skill) + abs(agility)
    magic_power = abs(intelligence * creativity * skill)
    block_power = abs(block * strength * weight * courage) + abs(speed)
    evade_chance = abs(speed * agility * prediction) - abs(weight)
    spirit_energy = abs(endurance * courage * resistance)
    instinct_talent = abs(creativity * skill * endurance * prediction * intelligence)

    player = Creature(
        hitpoints, attack_power, magic_power,
        block_power, evade_chance,
        spirit_energy, instinct_talent
    )
    return player


def spawn_enemy(difficulty: float):
    difficulty = difficulty / 1000 + 0.001

    # Goblin attributes
    attributes = (3.3, 1.8, 0.5, 1.5, 1.2, 0.8, 2.2)
    hp, ap, mp, bp, ec, se, it = (stat * difficulty for stat in attributes)

    enemy = Creature(hp, ap, mp, bp, ec, se, it)
    return enemy


def grade_entity(entity: Entity):
    genes = entity.genetics.get_joint_genes()
    player = spawn_player(genes)

    points = 1
    for level in range(1000):
        reward = game_level(player, level)
        if reward <= 0:
            break

        player.regenerate()
        points += reward

    return points


def game_level(player: Creature, level: int):
    enemy = spawn_enemy(level ** 1.2)

    reward_decay = 0.1
    reward = 10
    while reward > 0:
        player.attack(enemy)
        player.magic(enemy)
        if not enemy.is_alive():
            reward += 10
            break

        enemy.attack(player)
        enemy.magic(player)
        if not player.is_alive():
            reward += -10
            break

        reward -= reward_decay
    return reward
