import random
from .models import Monster, Move
from .content import SPECIES


def make_monster(species: str, level: int) -> Monster:
    data = SPECIES[species]
    scale = level - 1
    return Monster(
        species=species,
        symbol=data["symbol"],
        level=level,
        max_hp=data["hp"] + scale * 5,
        hp=data["hp"] + scale * 5,
        attack=data["attack"] + scale * 2,
        defense=data["defense"] + scale,
        speed=data["speed"] + scale,
        behavior=data["behavior"],
        moves=[Move(m.name, m.power, m.accuracy) for m in data["moves"]],
    )


def random_monster(rng: random.Random, floor: int, elite: bool = False) -> Monster:
    pool = ["Slime", "Bat", "Snake", "Wolf"]
    if floor >= 2:
        pool.append("Golem")
    if floor >= 3:
        pool.append("Wraith")
    level = max(1, floor + rng.randint(-1, 1) + (2 if elite else 0))
    return make_monster(rng.choice(pool), level)


def boss_monster(floor: int) -> Monster:
    boss = make_monster("Demon", floor + 4)
    boss.species = f"Abyss Demon F{floor}"
    boss.max_hp += floor * 15
    boss.hp = boss.max_hp
    return boss
