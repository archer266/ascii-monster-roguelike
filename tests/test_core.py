import random
from roguelike.factory import make_monster
from roguelike.dungeon import generate_dungeon


def test_monster_levels_scale():
    low = make_monster("Wolf", 1)
    high = make_monster("Wolf", 5)
    assert high.max_hp > low.max_hp
    assert high.attack > low.attack


def test_dungeon_is_connected():
    dungeon = generate_dungeon(random.Random(1), floor=1, room_count=12)
    seen = {(0, 0)}
    stack = [(0, 0)]
    while stack:
        x, y = stack.pop()
        for p in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if p in dungeon and p not in seen:
                seen.add(p)
                stack.append(p)
    assert len(seen) == len(dungeon)
