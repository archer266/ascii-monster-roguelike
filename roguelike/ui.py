import os
import sys

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def pause(message="Press Enter to continue..."):
    input(message)


def choose(prompt: str, options: set[str]) -> str:
    options = {x.lower() for x in options}
    while True:
        value = input(prompt).strip().lower()
        if value in options:
            return value


def hp_bar(hp: int, max_hp: int, width: int = 18) -> str:
    ratio = max(0, min(1, hp / max_hp if max_hp else 0))
    filled = round(ratio * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def title(text: str):
    print("=" * 66)
    print(text.center(66))
    print("=" * 66)
