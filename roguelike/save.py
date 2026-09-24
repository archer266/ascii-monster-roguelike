from __future__ import annotations
import json
from pathlib import Path
from .models import Player, Monster
from .dungeon import Room

SAVE_FILE = Path("savegame.json")
SAVE_VERSION = 2


def save_game(player, team, inventory, dungeon, room_pos, player_pos):
    data = {
        "version": SAVE_VERSION,
        "player": player.__dict__,
        "team": [m.to_dict() for m in team],
        "inventory": inventory,
        "room_pos": list(room_pos),
        "player_pos": list(player_pos),
        "dungeon": [],
    }
    for pos, room in dungeon.items():
        data["dungeon"].append({
            "pos": list(pos),
            "kind": room.kind,
            "visited": room.visited,
            "cleared": room.cleared,
            "tiles": room.tiles,
            "enemy_pos": list(room.enemy_pos) if room.enemy_pos else None,
            "event_done": room.event_done,
        })
    SAVE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_game():
    if not SAVE_FILE.exists():
        return None
    data = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
    if data.get("version") != SAVE_VERSION:
        raise ValueError("This save belongs to an older game version. Start a new run.")
    player = Player(**data["player"])
    team = [Monster.from_dict(m) for m in data["team"]]
    dungeon = {}
    for item in data["dungeon"]:
        room = Room(
            kind=item["kind"],
            visited=item["visited"],
            cleared=item["cleared"],
            tiles=item["tiles"],
            enemy_pos=tuple(item["enemy_pos"]) if item["enemy_pos"] else None,
            event_done=item.get("event_done", False),
        )
        dungeon[tuple(item["pos"])] = room
    return (
        player, team, data["inventory"], dungeon,
        tuple(data["room_pos"]), tuple(data["player_pos"])
    )
