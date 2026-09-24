from __future__ import annotations
import random
from .ui import clear, hp_bar, pause, choose


class Battle:
    def __init__(self, rng: random.Random, team: list, inventory: dict):
        self.rng = rng
        self.team = team
        self.inventory = inventory

    def _living(self):
        return [m for m in self.team if m.alive]

    def _pick(self):
        living = self._living()
        if not living:
            return None
        while True:
            clear()
            print("Choose a monster:\n")
            for i, m in enumerate(self.team, 1):
                state = f"{m.hp}/{m.max_hp} HP" if m.alive else "FAINTED"
                print(f"{i}. {m.symbol} {m.species} Lv.{m.level} - {state}")
            raw = input("\nNumber: ").strip()
            if raw.isdigit():
                idx = int(raw) - 1
                if 0 <= idx < len(self.team) and self.team[idx].alive:
                    return self.team[idx]

    def _damage(self, attacker, defender, move):
        if self.rng.randint(1, 100) > move.accuracy:
            return 0
        base = move.power + attacker.attack - defender.defense // 2
        variance = self.rng.randint(-2, 3)
        return max(1, base + variance)

    def _enemy_turn(self, enemy, active):
        move = self.rng.choice(enemy.moves)
        damage = self._damage(enemy, active, move)
        if damage == 0:
            return f"{enemy.species} used {move.name}, but missed!"
        active.hp = max(0, active.hp - damage)
        return f"{enemy.species} used {move.name} for {damage} damage!"

    def _capture(self, enemy):
        if len(self.team) >= 6:
            return False, "Your team is full."
        if self.inventory["Capture Orb"] <= 0:
            return False, "You have no Capture Orbs."
        self.inventory["Capture Orb"] -= 1
        hp_ratio = enemy.hp / enemy.max_hp
        chance = 0.20 + (1 - hp_ratio) * 0.65
        chance -= max(0, enemy.level - 3) * 0.02
        if self.rng.random() < max(0.10, min(0.85, chance)):
            enemy.hp = enemy.max_hp
            enemy.xp = 0
            self.team.append(enemy)
            return True, f"Captured {enemy.species}!"
        return False, "The monster broke free!"

    def fight(self, enemy, allow_capture=True):
        active = self._pick()
        if active is None:
            return "lost"

        message = "Battle started!"
        while True:
            clear()
            print("=" * 66)
            print(f" WILD {enemy.symbol} {enemy.species}  Lv.{enemy.level}")
            print(f" {hp_bar(enemy.hp, enemy.max_hp)} {enemy.hp}/{enemy.max_hp}")
            print("-" * 66)
            print(f" YOU  {active.symbol} {active.species}  Lv.{active.level}")
            print(f" {hp_bar(active.hp, active.max_hp)} {active.hp}/{active.max_hp}")
            print("=" * 66)
            print(message)
            print("\nMoves:")
            for i, move in enumerate(active.moves, 1):
                print(f" {i}. {move.name:<16} Power {move.power:<2} Acc {move.accuracy}%")
            print("\n C. Capture   T. Switch   I. Potion   R. Run")

            valid = {str(i) for i in range(1, len(active.moves) + 1)} | {"c","t","i","r"}
            action = choose("\nAction: ", valid)

            if action.isdigit():
                move = active.moves[int(action) - 1]
                damage = self._damage(active, enemy, move)
                if damage:
                    enemy.hp = max(0, enemy.hp - damage)
                    message = f"{active.species} used {move.name} for {damage} damage!"
                else:
                    message = f"{active.species} used {move.name}, but missed!"

                if enemy.hp <= 0:
                    for line in active.gain_xp(enemy.level * 45):
                        print(line)
                    pause()
                    return "won"

            elif action == "c":
                if not allow_capture:
                    message = "Boss monsters cannot be captured."
                    continue
                caught, message = self._capture(enemy)
                if caught:
                    pause(message + "\nPress Enter...")
                    return "caught"

            elif action == "t":
                new_active = self._pick()
                if new_active:
                    active = new_active
                    message = f"Go, {active.species}!"
                continue

            elif action == "i":
                if self.inventory["Potion"] <= 0:
                    message = "No Potions left."
                    continue
                if active.hp >= active.max_hp:
                    message = f"{active.species} is already at full HP."
                    continue
                self.inventory["Potion"] -= 1
                healed = min(30, active.max_hp - active.hp)
                active.hp += healed
                message = f"Potion restored {healed} HP."

            elif action == "r":
                if allow_capture and self.rng.random() < 0.65:
                    return "ran"
                message = "Couldn't escape!"

            if enemy.hp > 0:
                enemy_message = self._enemy_turn(enemy, active)
                message += "\n" + enemy_message
                if not active.alive:
                    if not self._living():
                        pause("Your whole team fainted. Press Enter...")
                        return "lost"
                    pause(f"{active.species} fainted. Press Enter...")
                    active = self._pick()
