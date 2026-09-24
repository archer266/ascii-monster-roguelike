from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import List


@dataclass
class Move:
    name: str
    power: int
    accuracy: int = 100


@dataclass
class Monster:
    species: str
    symbol: str
    level: int
    max_hp: int
    hp: int
    attack: int
    defense: int
    speed: int
    behavior: str
    moves: List[Move] = field(default_factory=list)
    xp: int = 0

    @property
    def alive(self) -> bool:
        return self.hp > 0

    @property
    def xp_needed(self) -> int:
        return 70 + self.level * 35

    def heal_full(self) -> None:
        self.hp = self.max_hp

    def gain_xp(self, amount: int) -> list[str]:
        messages = [f"{self.symbol} {self.species} gained {amount} XP."]
        self.xp += amount
        while self.xp >= self.xp_needed:
            needed = self.xp_needed
            self.xp -= needed
            self.level += 1
            self.max_hp += 5
            self.attack += 2
            self.defense += 1
            self.speed += 1
            self.hp = self.max_hp
            messages.append(f"LEVEL UP! {self.species} is now Lv.{self.level}.")
        return messages

    def to_dict(self) -> dict:
        data = asdict(self)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Monster":
        data = dict(data)
        data["moves"] = [Move(**move) for move in data.get("moves", [])]
        return cls(**data)


@dataclass
class Player:
    name: str = "Hero"
    symbol: str = "@"
    hp: int = 100
    max_hp: int = 100
    gold: int = 0
    floor: int = 1
    wins: int = 0
    captures: int = 0
