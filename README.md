# ASCII Monster Roguelike: Reforged

A terminal monster-catching roguelike built in Python. Explore a procedurally generated dungeon, battle and capture monsters, build a six-monster team, clear elite encounters, collect loot, defeat bosses, and descend through increasingly difficult floors.

## Why this version is different

The original prototype was a single large `game.py`. Reforged splits the project into focused modules for game flow, battles, procedural generation, data models, persistence, content, and UI. The result is easier to test, maintain, and extend.

## Features

- Procedurally generated connected dungeon floors
- Monster, elite, treasure, healing, mystery, and boss rooms
- Turn-based combat with power and accuracy stats
- Capture chance based on remaining enemy HP
- Six-monster team limit
- XP, leveling, HP, attack, defense, and speed progression
- Species-specific rule-based overworld AI
- Multiple floors with increasing difficulty
- Inventory, loot, gold, healing, and Rare Candy
- JSON save/load with a save-version field
- Dungeon map with fog of war
- Automated core tests
- No third-party runtime dependencies

## Project structure

```text
ascii-monster-roguelike-v2/
├── main.py
├── roguelike/
│   ├── battle.py
│   ├── content.py
│   ├── dungeon.py
│   ├── factory.py
│   ├── game.py
│   ├── models.py
│   ├── save.py
│   └── ui.py
├── tests/
│   └── test_core.py
├── screenshots/
├── README.md
└── .gitignore
```

## Run

Requires Python 3.10+.

```bash
python main.py
```

Movement uses `W`, `A`, `S`, `D` followed by Enter. This makes the game work in Windows PowerShell, Command Prompt, VS Code terminals, macOS, and Linux without a platform-specific keyboard library.

## Controls

| Command | Action |
|---|---|
| W A S D | Move |
| M | Map |
| T | Team |
| I | Inventory |
| V | Save |
| H | Help |
| Q | Return to title |

## Technical highlights

This project demonstrates:

- Python package/module organization
- Dataclasses and serialization
- Procedural generation
- Graph connectivity
- State machines and turn-based combat
- Rule-based enemy behavior
- Collision detection
- Manhattan-distance AI decisions
- JSON persistence and save versioning
- Automated testing
- Separation of game data, logic, and presentation

## Tests

The runtime has no third-party dependencies. If `pytest` is installed:

```bash
pytest
```

## Portfolio description

**ASCII Monster Roguelike: Reforged — Python**  
Developed a modular terminal roguelike featuring procedural dungeon generation, turn-based combat, monster collection and progression, rule-based enemy AI, persistent JSON saves, multi-floor difficulty scaling, and automated tests.

## Screenshots

Add screenshots to the `screenshots/` directory, then embed them here before featuring the repository prominently.

## Future ideas

- A* pathfinding
- Status effects and elemental strengths/weaknesses
- Shops and equipment
- More bosses and biomes
- Seeded daily runs
- Pygame graphical client using the same game logic
