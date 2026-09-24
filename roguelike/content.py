from .models import Move

SPECIES = {
    "Slime": {
        "symbol": "S", "hp": 38, "attack": 8, "defense": 7, "speed": 5,
        "behavior": "wanderer",
        "moves": [Move("Tackle", 8), Move("Bubble", 10, 95), Move("Slime Shot", 12, 90)]
    },
    "Bat": {
        "symbol": "B", "hp": 30, "attack": 10, "defense": 5, "speed": 13,
        "behavior": "skittish",
        "moves": [Move("Bite", 9), Move("Wing Cut", 11, 95), Move("Screech", 14, 80)]
    },
    "Snake": {
        "symbol": "N", "hp": 34, "attack": 11, "defense": 6, "speed": 10,
        "behavior": "ambusher",
        "moves": [Move("Bite", 9), Move("Venom Fang", 13, 90), Move("Coil Strike", 15, 80)]
    },
    "Wolf": {
        "symbol": "W", "hp": 46, "attack": 13, "defense": 8, "speed": 12,
        "behavior": "hunter",
        "moves": [Move("Bite", 11), Move("Claw", 13, 95), Move("Rage Rush", 17, 80)]
    },
    "Golem": {
        "symbol": "G", "hp": 58, "attack": 14, "defense": 14, "speed": 4,
        "behavior": "guardian",
        "moves": [Move("Stone Fist", 13), Move("Quake", 17, 85), Move("Crush", 20, 75)]
    },
    "Wraith": {
        "symbol": "R", "hp": 40, "attack": 16, "defense": 7, "speed": 15,
        "behavior": "hunter",
        "moves": [Move("Haunt", 14), Move("Shadow Claw", 17, 90), Move("Soul Rush", 20, 80)]
    },
    "Demon": {
        "symbol": "D", "hp": 75, "attack": 19, "defense": 12, "speed": 11,
        "behavior": "boss",
        "moves": [Move("Hellfire", 18), Move("Doom Claw", 21, 90), Move("Obliterate", 25, 75)]
    },
}

ROOM_ICONS = {
    "start": "ST",
    "normal": "..",
    "monster": "!!",
    "treasure": "$$",
    "healing": "++",
    "mystery": "??",
    "elite": "EL",
    "boss": "BO",
}
