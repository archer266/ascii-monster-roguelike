from __future__ import annotations
from dataclasses import dataclass, field
import random

WIDTH = 31
HEIGHT = 15

@dataclass
class Room:
    kind: str = "normal"
    visited: bool = False
    cleared: bool = False
    tiles: list[list[str]] = field(default_factory=list)
    enemy_pos: tuple[int, int] | None = None
    event_done: bool = False

    def make_tiles(self, rng: random.Random) -> None:
        self.tiles = []
        for y in range(HEIGHT):
            row = []
            for x in range(WIDTH):
                row.append("#" if x in (0, WIDTH - 1) or y in (0, HEIGHT - 1) else ".")
            self.tiles.append(row)

        # Pillars/walls, but keep center corridors open.
        for _ in range(20):
            x = rng.randint(2, WIDTH - 3)
            y = rng.randint(2, HEIGHT - 3)
            if abs(x - WIDTH // 2) <= 2 or abs(y - HEIGHT // 2) <= 1:
                continue
            self.tiles[y][x] = "#"

        if self.kind in ("monster", "elite", "boss"):
            self.enemy_pos = self._open_spawn(rng)

    def _open_spawn(self, rng: random.Random) -> tuple[int, int]:
        choices = []
        for y in range(2, HEIGHT - 2):
            for x in range(WIDTH // 2 + 3, WIDTH - 2):
                if self.tiles[y][x] == ".":
                    choices.append((x, y))
        return rng.choice(choices) if choices else (WIDTH - 4, HEIGHT // 2)


def neighbors(pos):
    x, y = pos
    return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]


def generate_dungeon(rng: random.Random, floor: int, room_count: int = 12) -> dict:
    dungeon = {(0, 0): Room("start")}
    while len(dungeon) < room_count:
        origin = rng.choice(list(dungeon))
        candidates = [p for p in neighbors(origin) if p not in dungeon]
        if candidates:
            dungeon[rng.choice(candidates)] = Room("normal")

    boss = max(dungeon, key=lambda p: abs(p[0]) + abs(p[1]))
    dungeon[boss].kind = "boss"

    candidates = [p for p in dungeon if p not in ((0, 0), boss)]
    rng.shuffle(candidates)

    layout = ["monster", "monster", "monster", "elite", "treasure", "treasure",
              "healing", "mystery"]
    for pos, kind in zip(candidates, layout):
        dungeon[pos].kind = kind

    for room in dungeon.values():
        room.make_tiles(rng)

    return dungeon
