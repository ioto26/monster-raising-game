# Player.py
import random
from interface import get_management_menu_choice, get_monster_selection

class Player:
    def __init__(self, name="主人公"):
        self.name = name
        self.monsters = []
        self.items = {}
        self.gold = 0
        self.current_monster_index = 0

    def add_monster(self, monster):
        self.monsters.append(monster)

    def gain_gold(self, amount):
        self.gold += amount