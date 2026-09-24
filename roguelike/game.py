from __future__ import annotations
import random
from .models import Player
from .factory import make_monster, random_monster, boss_monster
from .dungeon import generate_dungeon, WIDTH, HEIGHT
from .content import ROOM_ICONS
from .battle import Battle
from .save import save_game, load_game
from .ui import clear, pause, title, choose


class Game:
    def __init__(self):
        self.rng = random.Random()
        self.player = Player()
        self.team = []
        self.inventory = {"Potion": 3, "Super Potion": 0, "Capture Orb": 5, "Rare Candy": 0}
        self.dungeon = {}
        self.room_pos = (0, 0)
        self.player_pos = (WIDTH // 2, HEIGHT // 2)
        self.enemies = {}

    def run(self):
        while True:
            clear()
            title("ASCII MONSTER ROGUELIKE // REFORGED")
            print("\n1. New Run")
            print("2. Continue")
            print("3. How to Play")
            print("4. Quit")
            action = choose("\nChoose: ", {"1","2","3","4"})
            if action == "1":
                self.new_game()
                self.game_loop()
            elif action == "2":
                if self.continue_game():
                    self.game_loop()
            elif action == "3":
                self.help_screen()
            else:
                return

    def new_game(self):
        self.player = Player()
        self.team = []
        self.inventory = {"Potion": 3, "Super Potion": 0, "Capture Orb": 5, "Rare Candy": 0}
        self._choose_starter()
        self._new_floor()

    def _choose_starter(self):
        clear()
        title("CHOOSE YOUR STARTER")
        starters = [("1","Slime","Durable and steady"),
                    ("2","Snake","Fast attacker"),
                    ("3","Wolf","Powerful hunter")]
        for key, name, desc in starters:
            m = make_monster(name, 1)
            print(f"\n{key}. {m.symbol} {name:<8} - {desc}")
        choice = choose("\nStarter: ", {"1","2","3"})
        species = {"1":"Slime","2":"Snake","3":"Wolf"}[choice]
        self.team = [make_monster(species, 1)]

    def _new_floor(self):
        count = min(18, 11 + self.player.floor)
        self.dungeon = generate_dungeon(self.rng, self.player.floor, count)
        self.room_pos = (0, 0)
        self.player_pos = (WIDTH // 2, HEIGHT // 2)
        self.enemies = {}
        for pos, room in self.dungeon.items():
            if room.kind == "monster":
                self.enemies[pos] = random_monster(self.rng, self.player.floor)
            elif room.kind == "elite":
                self.enemies[pos] = random_monster(self.rng, self.player.floor, elite=True)
            elif room.kind == "boss":
                self.enemies[pos] = boss_monster(self.player.floor)

    def continue_game(self):
        clear()
        try:
            data = load_game()
        except Exception as exc:
            print(f"Could not load save: {exc}")
            pause()
            return False
        if data is None:
            print("No savegame.json found.")
            pause()
            return False
        (self.player, self.team, self.inventory, self.dungeon,
         self.room_pos, self.player_pos) = data
        self.enemies = {}
        # Recreate living room encounters deterministically enough for continued play.
        for pos, room in self.dungeon.items():
            if not room.cleared:
                if room.kind == "monster":
                    self.enemies[pos] = random_monster(self.rng, self.player.floor)
                elif room.kind == "elite":
                    self.enemies[pos] = random_monster(self.rng, self.player.floor, True)
                elif room.kind == "boss":
                    self.enemies[pos] = boss_monster(self.player.floor)
        return True

    def help_screen(self):
        clear()
        title("HOW TO PLAY")
        print("""
Explore connected dungeon rooms and defeat or capture monsters.

Movement: W A S D, then Enter
M: dungeon map
T: team
I: inventory
V: save
H: help
Q: return to title

Symbols:
@ = player   # = wall   . = floor
S/B/N/W/G/R/D = monsters

Reach the BO room and defeat its boss to descend to the next floor.
Every floor gets larger and monsters scale upward.
""")
        pause()

    def game_loop(self):
        while True:
            self._draw_room()
            cmd = input("\nCommand: ").strip().lower()
            if not cmd:
                continue
            cmd = cmd[0]

            if cmd == "q":
                return
            if cmd == "m":
                self._show_map()
                continue
            if cmd == "t":
                self._show_team()
                continue
            if cmd == "i":
                self._show_inventory()
                continue
            if cmd == "h":
                self.help_screen()
                continue
            if cmd == "v":
                save_game(self.player, self.team, self.inventory,
                          self.dungeon, self.room_pos, self.player_pos)
                pause("Game saved. Press Enter...")
                continue
            if cmd in "wasd":
                self._move(cmd)
                if self._resolve_room() == "lost":
                    return

    def _draw_room(self):
        clear()
        room = self.dungeon[self.room_pos]
        room.visited = True
        grid = [row[:] for row in room.tiles]
        x, y = self.room_pos

        if (x - 1, y) in self.dungeon:
            grid[HEIGHT // 2][0] = "<"
        if (x + 1, y) in self.dungeon:
            grid[HEIGHT // 2][WIDTH - 1] = ">"
        if (x, y - 1) in self.dungeon:
            grid[0][WIDTH // 2] = "^"
        if (x, y + 1) in self.dungeon:
            grid[HEIGHT - 1][WIDTH // 2] = "v"

        enemy = self.enemies.get(self.room_pos)
        if enemy and not room.cleared and room.enemy_pos:
            ex, ey = room.enemy_pos
            grid[ey][ex] = enemy.symbol

        px, py = self.player_pos
        grid[py][px] = self.player.symbol

        title(f"FLOOR {self.player.floor} // {room.kind.upper()}")
        lead = next((m for m in self.team if m.alive), None)
        lead_text = f"{lead.species} Lv.{lead.level} {lead.hp}/{lead.max_hp}HP" if lead else "NO ACTIVE MONSTER"
        print(f"Gold {self.player.gold} | Captures {self.player.captures} | {lead_text}")
        print("-" * 66)
        for row in grid:
            print("".join(row))
        print("-" * 66)
        print("WASD move | M map | T team | I inventory | V save | H help | Q quit")

    def _move(self, cmd):
        dx, dy = {"w":(0,-1),"s":(0,1),"a":(-1,0),"d":(1,0)}[cmd]
        px, py = self.player_pos
        nx, ny = px + dx, py + dy
        rx, ry = self.room_pos

        transitions = {
            (0, HEIGHT // 2): ((rx - 1, ry), (WIDTH - 2, HEIGHT // 2)),
            (WIDTH - 1, HEIGHT // 2): ((rx + 1, ry), (1, HEIGHT // 2)),
            (WIDTH // 2, 0): ((rx, ry - 1), (WIDTH // 2, HEIGHT - 2)),
            (WIDTH // 2, HEIGHT - 1): ((rx, ry + 1), (WIDTH // 2, 1)),
        }
        if (nx, ny) in transitions:
            new_room, spawn = transitions[(nx, ny)]
            if new_room in self.dungeon:
                self.room_pos = new_room
                self.player_pos = spawn
                self.dungeon[new_room].visited = True
                return

        room = self.dungeon[self.room_pos]
        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and room.tiles[ny][nx] != "#":
            self.player_pos = (nx, ny)

    def _resolve_room(self):
        room = self.dungeon[self.room_pos]
        if room.cleared:
            return None

        if room.kind in ("monster","elite","boss"):
            enemy = self.enemies.get(self.room_pos)
            if enemy is None:
                room.cleared = True
                return None
            ex, ey = room.enemy_pos or (WIDTH - 4, HEIGHT // 2)
            px, py = self.player_pos
            if abs(px - ex) + abs(py - ey) <= 1:
                pause(f"A {enemy.species} attacks! Press Enter...")
                result = Battle(self.rng, self.team, self.inventory).fight(
                    enemy, allow_capture=room.kind != "boss"
                )
                if result == "lost":
                    return "lost"
                if result in ("won","caught"):
                    room.cleared = True
                    self.enemies.pop(self.room_pos, None)
                    if result == "caught":
                        self.player.captures += 1
                    if room.kind == "elite":
                        reward = 60 + self.player.floor * 20
                        self.player.gold += reward
                        pause(f"Elite reward: {reward} gold. Press Enter...")
                    if room.kind == "boss":
                        self.player.wins += 1
                        self._floor_victory()
                return None

            self._move_enemy(room, enemy)
            return None

        if room.kind == "treasure" and not room.event_done:
            reward = self.rng.choice(["gold","orb","potion","candy"])
            if reward == "gold":
                amount = self.rng.randint(30, 80) + self.player.floor * 10
                self.player.gold += amount
                text = f"Found {amount} gold."
            elif reward == "orb":
                self.inventory["Capture Orb"] += 2
                text = "Found 2 Capture Orbs."
            elif reward == "potion":
                self.inventory["Potion"] += 2
                text = "Found 2 Potions."
            else:
                self.inventory["Rare Candy"] += 1
                text = "Found a Rare Candy."
            room.event_done = room.cleared = True
            pause(text + " Press Enter...")

        elif room.kind == "healing" and not room.event_done:
            for m in self.team:
                m.heal_full()
            room.event_done = room.cleared = True
            pause("The shrine restored your entire team. Press Enter...")

        elif room.kind == "mystery" and not room.event_done:
            roll = self.rng.choice(["gold","heal","ambush"])
            room.event_done = room.cleared = True
            if roll == "gold":
                self.player.gold += 50
                pause("A hidden cache contained 50 gold. Press Enter...")
            elif roll == "heal":
                for m in self.team:
                    m.hp = min(m.max_hp, m.hp + 20)
                pause("A strange light restored 20 HP to your team. Press Enter...")
            else:
                enemy = random_monster(self.rng, self.player.floor)
                pause(f"Ambush! {enemy.species} appeared. Press Enter...")
                result = Battle(self.rng, self.team, self.inventory).fight(enemy)
                if result == "lost":
                    return "lost"
                if result == "caught":
                    self.player.captures += 1
        return None

    def _move_enemy(self, room, enemy):
        if not room.enemy_pos:
            return
        ex, ey = room.enemy_pos
        px, py = self.player_pos
        distance = abs(px - ex) + abs(py - ey)

        chase_range = {"wanderer":5, "skittish":4, "ambusher":3, "hunter":9, "guardian":6, "boss":0}.get(enemy.behavior, 5)
        if enemy.behavior == "boss":
            return

        candidates = []
        if distance <= chase_range:
            if enemy.behavior == "skittish" and distance <= 2:
                candidates = [(ex - (px-ex), ey), (ex, ey - (py-ey))]
            else:
                if px != ex:
                    candidates.append((ex + (1 if px > ex else -1), ey))
                if py != ey:
                    candidates.append((ex, ey + (1 if py > ey else -1)))
        elif self.rng.random() < 0.25:
            dirs = [(1,0),(-1,0),(0,1),(0,-1)]
            self.rng.shuffle(dirs)
            candidates = [(ex+dx, ey+dy) for dx,dy in dirs]

        for nx, ny in candidates:
            if (nx, ny) == self.player_pos:
                continue
            if 1 <= nx < WIDTH-1 and 1 <= ny < HEIGHT-1 and room.tiles[ny][nx] == ".":
                room.enemy_pos = (nx, ny)
                break

    def _floor_victory(self):
        clear()
        title("FLOOR CLEARED")
        reward = 100 + self.player.floor * 50
        self.player.gold += reward
        print(f"\nYou defeated the floor boss.")
        print(f"Victory reward: {reward} gold.")
        print(f"Next floor: {self.player.floor + 1}")
        pause("\nPress Enter to descend...")
        self.player.floor += 1
        for m in self.team:
            m.heal_full()
        self.inventory["Potion"] += 1
        self.inventory["Capture Orb"] += 1
        self._new_floor()

    def _show_map(self):
        clear()
        title(f"DUNGEON MAP // FLOOR {self.player.floor}")
        xs = [p[0] for p in self.dungeon]
        ys = [p[1] for p in self.dungeon]
        for y in range(min(ys), max(ys)+1):
            line = ""
            for x in range(min(xs), max(xs)+1):
                pos = (x,y)
                if pos == self.room_pos:
                    cell = "@@"
                elif pos not in self.dungeon:
                    cell = "  "
                elif not self.dungeon[pos].visited:
                    cell = "##"
                else:
                    cell = ROOM_ICONS[self.dungeon[pos].kind]
                line += f"[{cell}]"
            print(line)
        print("\n@@ you | ## unexplored | !! monster | EL elite | $$ treasure | ++ heal | ?? mystery | BO boss")
        pause()

    def _show_team(self):
        clear()
        title("MONSTER TEAM")
        for i, m in enumerate(self.team, 1):
            print(f"\n{i}. {m.symbol} {m.species} Lv.{m.level}")
            print(f"   HP {m.hp}/{m.max_hp} | ATK {m.attack} | DEF {m.defense} | SPD {m.speed}")
            print(f"   XP {m.xp}/{m.xp_needed} | AI type: {m.behavior}")
            print("   Moves: " + ", ".join(move.name for move in m.moves))
        pause()

    def _show_inventory(self):
        clear()
        title("INVENTORY")
        for name, amount in self.inventory.items():
            print(f"{name:<16} x{amount}")
        print(f"{'Gold':<16} {self.player.gold}")
        print("\nRare Candy can be used from here.")
        if self.inventory["Rare Candy"] > 0 and self.team:
            action = input("Use a Rare Candy? (y/n): ").strip().lower()
            if action == "y":
                self.inventory["Rare Candy"] -= 1
                target = self.team[0]
                for line in target.gain_xp(target.xp_needed):
                    print(line)
        pause()
