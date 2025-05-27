import random
import time
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum

class ItemType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    POTION = "potion"
    TREASURE = "treasure"

class Direction(Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

@dataclass
class Item:
    name: str
    type: ItemType
    value: int
    description: str
    effect: int = 0

@dataclass
class Monster:
    name: str
    health: int
    max_health: int
    attack: int
    defense: int
    exp_value: int
    gold_drop: Tuple[int, int]
    description: str

class Player:
    def __init__(self, name: str):
        self.name = name
        self.health = 100
        self.max_health = 100
        self.attack = 15
        self.defense = 5
        self.level = 1
        self.exp = 0
        self.exp_to_next = 100
        self.gold = 50
        self.inventory = []
        self.equipped_weapon = None
        self.equipped_armor = None
        self.location = (0, 0)
        
    def level_up(self):
        if self.exp >= self.exp_to_next:
            self.level += 1
            self.exp -= self.exp_to_next
            self.exp_to_next = int(self.exp_to_next * 1.5)
            
            # Stat increases
            health_increase = random.randint(10, 20)
            attack_increase = random.randint(2, 5)
            defense_increase = random.randint(1, 3)
            
            self.max_health += health_increase
            self.health = self.max_health  # Full heal on level up
            self.attack += attack_increase
            self.defense += defense_increase
            
            print(f"\n🎉 LEVEL UP! You are now level {self.level}!")
            print(f"   Health: +{health_increase} (now {self.max_health})")
            print(f"   Attack: +{attack_increase} (now {self.attack})")
            print(f"   Defense: +{defense_increase} (now {self.defense})")
            return True
        return False
    
    def heal(self, amount: int):
        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        return self.health - old_health
    
    def take_damage(self, damage: int):
        actual_damage = max(1, damage - self.defense)
        self.health -= actual_damage
        return actual_damage
    
    def get_total_attack(self):
        base_attack = self.attack
        if self.equipped_weapon:
            base_attack += self.equipped_weapon.effect
        return base_attack
    
    def get_total_defense(self):
        base_defense = self.defense
        if self.equipped_armor:
            base_defense += self.equipped_armor.effect
        return base_defense

class GameWorld:
    def __init__(self):
        self.rooms = {}
        self.items_db = self._create_items_db()
        self.monsters_db = self._create_monsters_db()
        self._generate_world()
    
    def _create_items_db(self):
        return {
            "rusty_sword": Item("Rusty Sword", ItemType.WEAPON, 25, "An old but serviceable blade.", 5),
            "iron_sword": Item("Iron Sword", ItemType.WEAPON, 100, "A well-crafted iron weapon.", 12),
            "steel_sword": Item("Steel Sword", ItemType.WEAPON, 250, "A sharp steel blade that gleams.", 20),
            "dragon_sword": Item("Dragon Sword", ItemType.WEAPON, 1000, "A legendary blade forged from dragon scales.", 35),
            
            "leather_armor": Item("Leather Armor", ItemType.ARMOR, 50, "Basic protection made from tanned hide.", 3),
            "chain_mail": Item("Chain Mail", ItemType.ARMOR, 150, "Interlocked metal rings provide good defense.", 8),
            "plate_armor": Item("Plate Armor", ItemType.ARMOR, 400, "Heavy metal plates offer excellent protection.", 15),
            "dragon_armor": Item("Dragon Armor", ItemType.ARMOR, 1200, "Armor crafted from dragon hide.", 25),
            
            "health_potion": Item("Health Potion", ItemType.POTION, 20, "Restores 30 health points.", 30),
            "greater_health_potion": Item("Greater Health Potion", ItemType.POTION, 50, "Restores 60 health points.", 60),
            
            "gold_coins": Item("Gold Coins", ItemType.TREASURE, 0, "Shiny gold coins.", 0),
            "ruby": Item("Ruby", ItemType.TREASURE, 200, "A precious red gem.", 0),
            "emerald": Item("Emerald", ItemType.TREASURE, 300, "A valuable green stone.", 0),
            "diamond": Item("Diamond", ItemType.TREASURE, 500, "A brilliant crystal of immense value.", 0),
        }
    
    def _create_monsters_db(self):
        return {
            "goblin": Monster("Goblin", 25, 25, 8, 2, 15, (5, 12), "A small, green-skinned creature with sharp teeth."),
            "orc": Monster("Orc", 40, 40, 12, 4, 25, (8, 20), "A brutish humanoid with tusks and crude weapons."),
            "skeleton": Monster("Skeleton", 35, 35, 10, 6, 20, (3, 15), "Animated bones held together by dark magic."),
            "troll": Monster("Troll", 80, 80, 18, 8, 50, (20, 40), "A massive creature with regenerative abilities."),
            "dragon": Monster("Dragon", 200, 200, 35, 15, 200, (100, 200), "An ancient, fire-breathing beast of legend."),
            "wolf": Monster("Wolf", 30, 30, 14, 3, 18, (6, 15), "A fierce predator with sharp fangs."),
            "spider": Monster("Giant Spider", 20, 20, 6, 1, 12, (3, 8), "An oversized arachnid with venomous fangs."),
            "bandit": Monster("Bandit", 45, 45, 16, 5, 30, (15, 35), "A highway robber armed and dangerous."),
        }
    
    def _generate_world(self):
        # Create a 5x5 grid world with different room types
        room_types = [
            "forest", "cave", "ruins", "mountain", "swamp", "desert", 
            "village", "dungeon", "tower", "library", "armory", "treasury"
        ]
        
        for x in range(-2, 3):
            for y in range(-2, 3):
                if x == 0 and y == 0:
                    # Starting location - safe village
                    room = {
                        "type": "village",
                        "description": "A peaceful village with friendly merchants and warm hearths.",
                        "monsters": [],
                        "items": [],
                        "special": "shop"
                    }
                else:
                    room_type = random.choice(room_types)
                    room = self._generate_room(room_type, abs(x) + abs(y))
                
                self.rooms[(x, y)] = room
    
    def _generate_room(self, room_type: str, difficulty: int):
        descriptions = {
            "forest": "A dense woodland with towering trees and dappled sunlight.",
            "cave": "A dark cavern with echoing drips and mysterious shadows.",
            "ruins": "Ancient stone structures covered in moss and ivy.",
            "mountain": "Rocky peaks with thin air and treacherous paths.",
            "swamp": "Murky wetlands with twisted trees and strange sounds.",
            "desert": "Endless sand dunes under a scorching sun.",
            "dungeon": "A foreboding underground chamber filled with danger.",
            "tower": "A tall spire reaching toward the clouds.",
            "library": "A repository of ancient knowledge and dusty tomes.",
            "armory": "A weapons cache left behind by long-dead warriors.",
            "treasury": "A vault that once held great riches.",
        }
        
        room = {
            "type": room_type,
            "description": descriptions.get(room_type, "A mysterious location."),
            "monsters": [],
            "items": [],
            "special": None
        }
        
        # Add monsters based on difficulty
        if random.random() < 0.6:  # 60% chance of monsters
            monster_count = random.randint(1, min(3, difficulty))
            available_monsters = ["goblin", "orc", "skeleton", "wolf", "spider"]
            
            if difficulty >= 3:
                available_monsters.extend(["troll", "bandit"])
            if difficulty >= 4:
                available_monsters.append("dragon")
            
            for _ in range(monster_count):
                monster_key = random.choice(available_monsters)
                monster = Monster(**self.monsters_db[monster_key].__dict__)
                room["monsters"].append(monster)
        
        # Add items based on room type and difficulty
        if random.random() < 0.4:  # 40% chance of items
            if room_type == "treasury":
                # Treasury rooms have better loot
                treasure_items = ["ruby", "emerald", "diamond", "steel_sword", "dragon_armor"]
                item_key = random.choice(treasure_items)
            elif room_type == "armory":
                # Armory rooms have weapons and armor
                weapon_items = ["iron_sword", "steel_sword", "chain_mail", "plate_armor"]
                item_key = random.choice(weapon_items)
            else:
                # Regular loot distribution
                all_items = list(self.items_db.keys())
                item_key = random.choice(all_items)
            
            item = Item(**self.items_db[item_key].__dict__)
            room["items"].append(item)
        
        return room
    
    def get_room(self, location: Tuple[int, int]):
        return self.rooms.get(location)

class Game:
    def __init__(self):
        self.player = None
        self.world = GameWorld()
        self.game_over = False
        self.commands = {
            "look": self.cmd_look,
            "l": self.cmd_look,
            "go": self.cmd_go,
            "north": lambda: self.cmd_go("north"),
            "south": lambda: self.cmd_go("south"),
            "east": lambda: self.cmd_go("east"),
            "west": lambda: self.cmd_go("west"),
            "n": lambda: self.cmd_go("north"),
            "s": lambda: self.cmd_go("south"),
            "e": lambda: self.cmd_go("east"),
            "w": lambda: self.cmd_go("west"),
            "inventory": self.cmd_inventory,
            "i": self.cmd_inventory,
            "stats": self.cmd_stats,
            "fight": self.cmd_fight,
            "f": self.cmd_fight,
            "take": self.cmd_take,
            "get": self.cmd_take,
            "use": self.cmd_use,
            "equip": self.cmd_equip,
            "unequip": self.cmd_unequip,
            "shop": self.cmd_shop,
            "help": self.cmd_help,
            "quit": self.cmd_quit,
            "save": self.cmd_save,
            "load": self.cmd_load,
        }
    
    def start_game(self):
        print("🐉 Welcome to Dragon's Quest! 🐉")
        print("=" * 50)
        
        name = input("Enter your character's name: ").strip()
        if not name:
            name = "Adventurer"
        
        self.player = Player(name)
        
        print(f"\nWelcome, {self.player.name}!")
        print("Type 'help' for a list of commands.")
        print("Your adventure begins in a peaceful village...")
        
        self.cmd_look()
        
        while not self.game_over:
            try:
                command = input(f"\n[{self.player.name}] > ").strip().lower()
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0]
                args = parts[1:] if len(parts) > 1 else []
                
                if cmd in self.commands:
                    if args and cmd in ["go", "take", "get", "use", "equip", "unequip"]:
                        self.commands[cmd](" ".join(args))
                    else:
                        self.commands[cmd]()
                else:
                    print("Unknown command. Type 'help' for available commands.")
                
                # Check if player died
                if self.player.health <= 0:
                    print("\n💀 You have died! Game Over.")
                    print(f"Final level: {self.player.level}")
                    print(f"Gold collected: {self.player.gold}")
                    self.game_over = True
                    
            except KeyboardInterrupt:
                print("\n\nThanks for playing Dragon's Quest!")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
    
    def cmd_look(self):
        current_room = self.world.get_room(self.player.location)
        if not current_room:
            print("You are in an unknown location.")
            return
        
        print(f"\n📍 {current_room['type'].title()}")
        print(f"   {current_room['description']}")
        
        if current_room['monsters']:
            print(f"\n⚔️  Enemies present:")
            for monster in current_room['monsters']:
                health_bar = self._create_health_bar(monster.health, monster.max_health)
                print(f"   • {monster.name} {health_bar}")
        
        if current_room['items']:
            print(f"\n💰 Items here:")
            for item in current_room['items']:
                print(f"   • {item.name}: {item.description}")
        
        if current_room.get('special') == 'shop':
            print(f"\n🏪 There's a merchant here. Type 'shop' to browse wares.")
        
        # Show available exits
        exits = []
        x, y = self.player.location
        for direction, (dx, dy) in [("north", (0, 1)), ("south", (0, -1)), 
                                   ("east", (1, 0)), ("west", (-1, 0))]:
            if (x + dx, y + dy) in self.world.rooms:
                exits.append(direction)
        
        if exits:
            print(f"\n🚪 Exits: {', '.join(exits)}")
    
    def cmd_go(self, direction: str = None):
        if not direction:
            print("Go where? (north, south, east, west)")
            return
        
        direction = direction.lower()
        direction_map = {
            "north": (0, 1), "south": (0, -1),
            "east": (1, 0), "west": (-1, 0),
            "n": (0, 1), "s": (0, -1),
            "e": (1, 0), "w": (-1, 0)
        }
        
        if direction not in direction_map:
            print("Invalid direction. Use north, south, east, or west.")
            return
        
        current_room = self.world.get_room(self.player.location)
        if current_room and current_room['monsters']:
            print("You cannot leave while enemies are present! Fight or flee!")
            return
        
        dx, dy = direction_map[direction]
        new_x = self.player.location[0] + dx
        new_y = self.player.location[1] + dy
        new_location = (new_x, new_y)
        
        if new_location not in self.world.rooms:
            print("You cannot go that way.")
            return
        
        self.player.location = new_location
        print(f"You travel {direction}...")
        time.sleep(1)
        self.cmd_look()
    
    def cmd_inventory(self):
        if not self.player.inventory:
            print("Your inventory is empty.")
            return
        
        print(f"\n🎒 {self.player.name}'s Inventory:")
        print(f"   Gold: {self.player.gold}")
        
        if self.player.equipped_weapon:
            print(f"   Weapon: {self.player.equipped_weapon.name} (+{self.player.equipped_weapon.effect} attack)")
        if self.player.equipped_armor:
            print(f"   Armor: {self.player.equipped_armor.name} (+{self.player.equipped_armor.effect} defense)")
        
        print("\n   Items:")
        for item in self.player.inventory:
            print(f"   • {item.name}: {item.description}")
    
    def cmd_stats(self):
        weapon_bonus = self.player.equipped_weapon.effect if self.player.equipped_weapon else 0
        armor_bonus = self.player.equipped_armor.effect if self.player.equipped_armor else 0
        
        health_bar = self._create_health_bar(self.player.health, self.player.max_health)
        exp_bar = self._create_exp_bar(self.player.exp, self.player.exp_to_next)
        
        print(f"\n📊 {self.player.name}'s Stats:")
        print(f"   Level: {self.player.level}")
        print(f"   Health: {health_bar} ({self.player.health}/{self.player.max_health})")
        print(f"   Experience: {exp_bar} ({self.player.exp}/{self.player.exp_to_next})")
        print(f"   Attack: {self.player.attack} (+{weapon_bonus}) = {self.player.get_total_attack()}")
        print(f"   Defense: {self.player.defense} (+{armor_bonus}) = {self.player.get_total_defense()}")
        print(f"   Gold: {self.player.gold}")
    
    def cmd_fight(self):
        current_room = self.world.get_room(self.player.location)
        if not current_room or not current_room['monsters']:
            print("There are no enemies to fight here.")
            return
        
        monster = current_room['monsters'][0]  # Fight first monster
        print(f"\n⚔️  Battle begins with {monster.name}!")
        print(f"   {monster.description}")
        
        while monster.health > 0 and self.player.health > 0:
            # Player's turn
            print(f"\n{self.player.name}: {self._create_health_bar(self.player.health, self.player.max_health)}")
            print(f"{monster.name}: {self._create_health_bar(monster.health, monster.max_health)}")
            
            action = input("Choose action: (a)ttack, (r)un, (u)se item: ").lower()
            
            if action == 'a' or action == 'attack':
                # Player attacks
                damage = random.randint(self.player.get_total_attack() - 3, self.player.get_total_attack() + 3)
                actual_damage = max(1, damage - monster.defense)
                monster.health -= actual_damage
                print(f"You deal {actual_damage} damage to {monster.name}!")
                
                if monster.health <= 0:
                    print(f"\n🎉 You defeated {monster.name}!")
                    
                    # Reward exp and gold
                    self.player.exp += monster.exp_value
                    gold_reward = random.randint(*monster.gold_drop)
                    self.player.gold += gold_reward
                    
                    print(f"   +{monster.exp_value} EXP, +{gold_reward} gold")
                    
                    # Remove monster from room
                    current_room['monsters'].remove(monster)
                    
                    # Check for level up
                    if self.player.level_up():
                        pass  # Level up message already printed
                    
                    break
            
            elif action == 'r' or action == 'run':
                if random.random() < 0.7:  # 70% chance to run successfully
                    print("You successfully fled from battle!")
                    return
                else:
                    print("You failed to escape!")
            
            elif action == 'u' or action == 'use':
                potions = [item for item in self.player.inventory if item.type == ItemType.POTION]
                if not potions:
                    print("You have no potions to use!")
                    continue
                
                print("Available potions:")
                for i, potion in enumerate(potions):
                    print(f"   {i + 1}. {potion.name}")
                
                try:
                    choice = int(input("Choose potion (number): ")) - 1
                    if 0 <= choice < len(potions):
                        potion = potions[choice]
                        healed = self.player.heal(potion.effect)
                        self.player.inventory.remove(potion)
                        print(f"You used {potion.name} and restored {healed} health!")
                    else:
                        print("Invalid choice!")
                        continue
                except ValueError:
                    print("Invalid input!")
                    continue
            else:
                print("Invalid action!")
                continue
            
            # Monster's turn (if still alive)
            if monster.health > 0:
                damage = random.randint(monster.attack - 2, monster.attack + 2)
                actual_damage = self.player.take_damage(damage)
                print(f"{monster.name} attacks you for {actual_damage} damage!")
                
                if self.player.health <= 0:
                    return  # Player died, will be handled in main loop
    
    def cmd_take(self, item_name: str = None):
        if not item_name:
            print("Take what?")
            return
        
        current_room = self.world.get_room(self.player.location)
        if not current_room or not current_room['items']:
            print("There are no items here.")
            return
        
        item_name = item_name.lower()
        for item in current_room['items'][:]:  # Copy list to avoid modification issues
            if item_name in item.name.lower():
                self.player.inventory.append(item)
                current_room['items'].remove(item)
                print(f"You picked up {item.name}.")
                return
        
        print("That item is not here.")
    
    def cmd_use(self, item_name: str = None):
        if not item_name:
            print("Use what?")
            return
        
        item_name = item_name.lower()
        for item in self.player.inventory[:]:
            if item_name in item.name.lower():
                if item.type == ItemType.POTION:
                    healed = self.player.heal(item.effect)
                    self.player.inventory.remove(item)
                    print(f"You used {item.name} and restored {healed} health!")
                    return
                else:
                    print("You cannot use that item.")
                    return
        
        print("You don't have that item.")
    
    def cmd_equip(self, item_name: str = None):
        if not item_name:
            print("Equip what?")
            return
        
        item_name = item_name.lower()
        for item in self.player.inventory:
            if item_name in item.name.lower():
                if item.type == ItemType.WEAPON:
                    if self.player.equipped_weapon:
                        self.player.inventory.append(self.player.equipped_weapon)
                    self.player.equipped_weapon = item
                    self.player.inventory.remove(item)
                    print(f"You equipped {item.name}.")
                    return
                elif item.type == ItemType.ARMOR:
                    if self.player.equipped_armor:
                        self.player.inventory.append(self.player.equipped_armor)
                    self.player.equipped_armor = item
                    self.player.inventory.remove(item)
                    print(f"You equipped {item.name}.")
                    return
                else:
                    print("You cannot equip that item.")
                    return
        
        print("You don't have that item.")
    
    def cmd_unequip(self, item_type: str = None):
        if not item_type:
            print("Unequip what? (weapon/armor)")
            return
        
        item_type = item_type.lower()
        if item_type in ["weapon", "sword"]:
            if self.player.equipped_weapon:
                self.player.inventory.append(self.player.equipped_weapon)
                print(f"You unequipped {self.player.equipped_weapon.name}.")
                self.player.equipped_weapon = None
            else:
                print("You don't have a weapon equipped.")
        elif item_type == "armor":
            if self.player.equipped_armor:
                self.player.inventory.append(self.player.equipped_armor)
                print(f"You unequipped {self.player.equipped_armor.name}.")
                self.player.equipped_armor = None
            else:
                print("You don't have armor equipped.")
        else:
            print("Invalid item type. Use 'weapon' or 'armor'.")
    
    def cmd_shop(self):
        current_room = self.world.get_room(self.player.location)
        if not current_room or current_room.get('special') != 'shop':
            print("There's no shop here.")
            return
        
        shop_items = [
            self.world.items_db["health_potion"],
            self.world.items_db["greater_health_potion"],
            self.world.items_db["leather_armor"],
            self.world.items_db["iron_sword"],
        ]
        
        while True:
            print(f"\n🏪 Welcome to the Village Shop!")
            print(f"   Your gold: {self.player.gold}")
            print(f"\n   Items for sale:")
            
            for i, item in enumerate(shop_items):
                print(f"   {i + 1}. {item.name} - {item.value} gold")
                print(f"      {item.description}")
            
            print(f"\n   0. Leave shop")
            
            try:
                choice = int(input("What would you like to buy? "))
                if choice == 0:
                    print("Thanks for visiting!")
                    break
                elif 1 <= choice <= len(shop_items):
                    item = shop_items[choice - 1]
                    if self.player.gold >= item.value:
                        self.player.gold -= item.value
                        # Create a copy of the item
                        new_item = Item(**item.__dict__)
                        self.player.inventory.append(new_item)
                        print(f"You bought {item.name}!")
                    else:
                        print("You don't have enough gold!")
                else:
                    print("Invalid choice!")
            except ValueError:
                print("Invalid input!")
    
    def cmd_help(self):
        print("\n📖 Available Commands:")
        print("   Movement: north/n, south/s, east/e, west/w, go <direction>")
        print("   Combat: fight/f")
        print("   Items: take/get <item>, use <item>, equip <item>, unequip <type>")
        print("   Information: look/l, inventory/i, stats")
        print("   Other: shop (in villages), help, save, load, quit")
    
    def cmd_quit(self):
        print("Thanks for playing Dragon's Quest!")
        self.game_over = True
    
    def cmd_save(self):
        try:
            save_data = {
                "player": {
                    "name": self.player.name,
                    "health": self.player.health,
                    "max_health": self.player.max_health,
                    "attack": self.player.attack,
                    "defense": self.player.defense,
                    "level": self.player.level,
                    "exp": self.player.exp,
                    "exp_to_next": self.player.exp_to_next,
                    "gold": self.player.gold,
                    "location": self.player.location,
                    "inventory": [item.__dict__ for item in self.player.inventory],
                    "equipped_weapon": self.player.equipped_weapon.__dict__ if self.player.equipped_weapon else None,
                    "equipped_armor": self.player.equipped_armor.__dict__ if self.player.equipped_armor else None,
                }
            }
            
            with open("dragonquest_save.json", "w") as f:
                json.dump(save_data, f, indent=2)
            print("Game saved successfully!")
        except Exception as e:
            print(f"Failed to save game: {e}")
    
    def cmd_load(self):
        try:
            with open("dragonquest_save.json", "r") as f:
                save_data = json.load(f)
            
            player_data = save_data["player"]
            self.player = Player(player_data["name"])
            
            # Restore player stats
            for key, value in player_data.items():
                if key in ["inventory", "equipped_weapon", "equipped_armor"]:
                    continue
                setattr(self.player, key, value)
            
            # Restore inventory
            self.player.inventory = []
            for item_data in player_data["inventory"]:
                item = Item(**item_data)
                self.player.inventory.append(item)
            
            # Restore equipped items
            if player_data["equipped_weapon"]:
                self.player.equipped_weapon = Item(**player_data["equipped_weapon"])
            if player_data["equipped_armor"]:
                self.player.equipped_armor = Item(**player_data["equipped_armor"])
            
            print("Game loaded successfully!")
            self.cmd_look()
        except FileNotFoundError:
            print("No save file found.")
        except Exception as e:
            print(f"Failed to load game: {e}")
    
    def _create_health_bar(self, current: int, maximum: int, length: int = 20):
        if maximum <= 0:
            return "[ERROR]"
        
        filled = int((current / maximum) * length)
        bar = "█" * filled + "░" * (length - filled)
        percentage = int((current / maximum) * 100)
        
        # Color coding for health
        if percentage > 75:
            color = "🟢"
        elif percentage > 50:
            color = "🟡"
        elif percentage > 25:
            color = "🟠"
        else:
            color = "🔴"
        
        return f"{color}[{bar}] {current}/{maximum}"
    
    def _create_exp_bar(self, current: int, maximum: int, length: int = 15):
        if maximum <= 0:
            return "[ERROR]"
        
        filled = int((current / maximum) * length)
        bar = "▓" * filled + "▒" * (length - filled)
        percentage = int((current / maximum) * 100)
        
        return f"⭐[{bar}] {percentage}%"

# Additional game systems and features

class QuestSystem:
    def __init__(self):
        self.active_quests = []
        self.completed_quests = []
        self.available_quests = {
            "goblin_slayer": {
                "name": "Goblin Slayer",
                "description": "Defeat 5 goblins terrorizing the countryside",
                "type": "kill",
                "target": "goblin",
                "count": 5,
                "reward_gold": 100,
                "reward_exp": 50,
                "current_count": 0
            },
            "treasure_hunter": {
                "name": "Treasure Hunter",
                "description": "Find and collect 3 precious gems",
                "type": "collect",
                "target": ["ruby", "emerald", "diamond"],
                "count": 3,
                "reward_gold": 200,
                "reward_exp": 75,
                "current_count": 0
            },
            "dragon_slayer": {
                "name": "Dragon Slayer",
                "description": "Defeat the ancient dragon",
                "type": "kill",
                "target": "dragon",
                "count": 1,
                "reward_gold": 1000,
                "reward_exp": 500,
                "current_count": 0
            }
        }

class WeatherSystem:
    def __init__(self):
        self.current_weather = "clear"
        self.weather_effects = {
            "clear": {"visibility": 1.0, "combat_modifier": 1.0, "description": "The sky is clear and bright."},
            "rain": {"visibility": 0.8, "combat_modifier": 0.9, "description": "Rain falls steadily from gray clouds."},
            "storm": {"visibility": 0.6, "combat_modifier": 0.8, "description": "A fierce storm rages with lightning and thunder."},
            "fog": {"visibility": 0.5, "combat_modifier": 1.0, "description": "Thick fog obscures the landscape."},
            "snow": {"visibility": 0.7, "combat_modifier": 0.9, "description": "Soft snow drifts down from the sky."}
        }
    
    def change_weather(self):
        weather_types = list(self.weather_effects.keys())
        # 70% chance to keep current weather, 30% to change
        if random.random() < 0.3:
            self.current_weather = random.choice(weather_types)
    
    def get_weather_description(self):
        return self.weather_effects[self.current_weather]["description"]
    
    def get_combat_modifier(self):
        return self.weather_effects[self.current_weather]["combat_modifier"]

class CraftingSystem:
    def __init__(self):
        self.recipes = {
            "improved_sword": {
                "name": "Improved Sword",
                "materials": {"iron_sword": 1, "ruby": 1},
                "result": "steel_sword",
                "description": "Enhance an iron sword with a ruby"
            },
            "reinforced_armor": {
                "name": "Reinforced Armor",
                "materials": {"chain_mail": 1, "emerald": 1},
                "result": "plate_armor",
                "description": "Strengthen chain mail with an emerald"
            },
            "super_potion": {
                "name": "Super Health Potion",
                "materials": {"health_potion": 2, "diamond": 1},
                "result": "greater_health_potion",
                "description": "Combine potions with diamond dust for greater effect"
            }
        }

# Enhanced Game class with additional systems
def enhance_game_class():
    # Add new attributes to Game.__init__
    original_init = Game.__init__
    
    def new_init(self):
        original_init(self)
        self.quest_system = QuestSystem()
        self.weather_system = WeatherSystem()
        self.crafting_system = CraftingSystem()
        self.turn_count = 0
        
        # Add new commands
        self.commands.update({
            "quests": self.cmd_quests,
            "q": self.cmd_quests,
            "weather": self.cmd_weather,
            "craft": self.cmd_craft,
            "recipes": self.cmd_recipes,
            "time": self.cmd_time,
            "rest": self.cmd_rest,
        })
    
    Game.__init__ = new_init

# New command methods for Game class
def add_new_commands():
    def cmd_quests(self):
        if not self.quest_system.active_quests and not self.quest_system.available_quests:
            print("No quests available.")
            return
        
        print("\n📋 Quest Log:")
        
        if self.quest_system.active_quests:
            print("\n   Active Quests:")
            for quest_id, quest in self.quest_system.active_quests:
                progress = f"({quest['current_count']}/{quest['count']})"
                print(f"   • {quest['name']} {progress}")
                print(f"     {quest['description']}")
        
        if self.quest_system.available_quests:
            print("\n   Available Quests:")
            for quest_id, quest in self.quest_system.available_quests.items():
                reward_text = f"{quest['reward_gold']} gold, {quest['reward_exp']} exp"
                print(f"   • {quest['name']} - Reward: {reward_text}")
                print(f"     {quest['description']}")
        
        if self.quest_system.completed_quests:
            print(f"\n   Completed Quests: {len(self.quest_system.completed_quests)}")
    
    def cmd_weather(self):
        weather_desc = self.weather_system.get_weather_description()
        combat_mod = self.weather_system.get_combat_modifier()
        
        print(f"\n🌤️  Current Weather: {self.weather_system.current_weather.title()}")
        print(f"   {weather_desc}")
        
        if combat_mod != 1.0:
            modifier_text = "bonus" if combat_mod > 1.0 else "penalty"
            percentage = abs(int((combat_mod - 1.0) * 100))
            print(f"   Combat {modifier_text}: {percentage}%")
    
    def cmd_craft(self, recipe_name: str = None):
        if not recipe_name:
            print("What would you like to craft? Use 'recipes' to see available recipes.")
            return
        
        recipe_name = recipe_name.lower().replace(" ", "_")
        
        if recipe_name not in self.crafting_system.recipes:
            print("Unknown recipe. Use 'recipes' to see available recipes.")
            return
        
        recipe = self.crafting_system.recipes[recipe_name]
        
        # Check if player has required materials
        player_items = {}
        for item in self.player.inventory:
            item_key = item.name.lower().replace(" ", "_")
            player_items[item_key] = player_items.get(item_key, 0) + 1
        
        can_craft = True
        for material, needed_count in recipe["materials"].items():
            if player_items.get(material, 0) < needed_count:
                can_craft = False
                break
        
        if not can_craft:
            print(f"You don't have the required materials for {recipe['name']}:")
            for material, count in recipe["materials"].items():
                have = player_items.get(material, 0)
                material_name = material.replace("_", " ").title()
                print(f"   • {material_name}: {have}/{count}")
            return
        
        # Remove materials from inventory
        for material, needed_count in recipe["materials"].items():
            removed_count = 0
            for item in self.player.inventory[:]:
                item_key = item.name.lower().replace(" ", "_")
                if item_key == material and removed_count < needed_count:
                    self.player.inventory.remove(item)
                    removed_count += 1
        
        # Add crafted item
        result_item = Item(**self.world.items_db[recipe["result"]].__dict__)
        self.player.inventory.append(result_item)
        
        print(f"✨ Successfully crafted {result_item.name}!")
    
    def cmd_recipes(self):
        print("\n📖 Available Recipes:")
        for recipe_id, recipe in self.crafting_system.recipes.items():
            print(f"\n   {recipe['name']}:")
            print(f"   {recipe['description']}")
            print(f"   Materials needed:")
            for material, count in recipe["materials"].items():
                material_name = material.replace("_", " ").title()
                print(f"     • {material_name} x{count}")
    
    def cmd_time(self):
        time_of_day = ["Dawn", "Morning", "Midday", "Afternoon", "Evening", "Night"]
        current_time = time_of_day[self.turn_count % 6]
        
        print(f"\n🕐 Time: {current_time}")
        print(f"   Turns elapsed: {self.turn_count}")
        
        # Show time-based effects
        if current_time in ["Evening", "Night"]:
            print(f"   🌙 Monsters are more active during {current_time.lower()}.")
        elif current_time == "Dawn":
            print(f"   🌅 A new day begins. You feel refreshed.")
    
    def cmd_rest(self):
        current_room = self.world.get_room(self.player.location)
        if current_room and current_room['monsters']:
            print("You cannot rest while enemies are nearby!")
            return
        
        if current_room and current_room['type'] != 'village':
            if random.random() < 0.3:  # 30% chance of being interrupted
                print("You try to rest, but strange noises keep you awake.")
                return
        
        # Resting restores some health and advances time
        heal_amount = random.randint(10, 25)
        actual_heal = self.player.heal(heal_amount)
        self.turn_count += 2
        self.weather_system.change_weather()
        
        print(f"💤 You rest and recover {actual_heal} health.")
        print("Time passes...")
        
        # Small chance of finding something while resting in certain areas
        if current_room and current_room['type'] in ['forest', 'ruins'] and random.random() < 0.1:
            found_items = ['health_potion', 'gold_coins']
            found_item_key = random.choice(found_items)
            found_item = Item(**self.world.items_db[found_item_key].__dict__)
            
            if found_item_key == 'gold_coins':
                gold_amount = random.randint(5, 15)
                self.player.gold += gold_amount
                print(f"🪙 While resting, you found {gold_amount} gold coins!")
            else:
                self.player.inventory.append(found_item)
                print(f"🎁 While resting, you found a {found_item.name}!")
    
    # Add methods to Game class
    Game.cmd_quests = cmd_quests
    Game.cmd_weather = cmd_weather
    Game.cmd_craft = cmd_craft
    Game.cmd_recipes = cmd_recipes
    Game.cmd_time = cmd_time
    Game.cmd_rest = cmd_rest

# Enhanced combat system
def enhance_combat_system():
    original_fight = Game.cmd_fight
    
    def enhanced_fight(self):
        current_room = self.world.get_room(self.player.location)
        if not current_room or not current_room['monsters']:
            print("There are no enemies to fight here.")
            return
        
        monster = current_room['monsters'][0]
        
        # Apply weather effects to combat
        weather_modifier = self.weather_system.get_combat_modifier()
        
        print(f"\n⚔️  Battle begins with {monster.name}!")
        print(f"   {monster.description}")
        
        if weather_modifier != 1.0:
            weather_desc = self.weather_system.get_weather_description()
            print(f"   Weather: {weather_desc}")
        
        combat_round = 1
        
        while monster.health > 0 and self.player.health > 0:
            print(f"\n--- Round {combat_round} ---")
            print(f"{self.player.name}: {self._create_health_bar(self.player.health, self.player.max_health)}")
            print(f"{monster.name}: {self._create_health_bar(monster.health, monster.max_health)}")
            
            action = input("\nChoose action: (a)ttack, (d)efend, (r)un, (u)se item: ").lower()
            
            if action == 'a' or action == 'attack':
                # Player attacks with weather modifier
                base_damage = random.randint(self.player.get_total_attack() - 3, self.player.get_total_attack() + 3)
                modified_damage = int(base_damage * weather_modifier)
                actual_damage = max(1, modified_damage - monster.defense)
                
                # Critical hit chance
                if random.random() < 0.1:  # 10% crit chance
                    actual_damage *= 2
                    print(f"💥 CRITICAL HIT! You deal {actual_damage} damage to {monster.name}!")
                else:
                    print(f"You deal {actual_damage} damage to {monster.name}!")
                
                monster.health -= actual_damage
                
                if monster.health <= 0:
                    print(f"\n🎉 You defeated {monster.name}!")
                    
                    # Enhanced rewards
                    base_exp = monster.exp_value
                    base_gold = random.randint(*monster.gold_drop)
                    
                    # Bonus for quick victory
                    if combat_round <= 3:
                        exp_bonus = int(base_exp * 0.2)
                        gold_bonus = int(base_gold * 0.3)
                        print(f"   ⚡ Quick Victory Bonus!")
                        base_exp += exp_bonus
                        base_gold += gold_bonus
                    
                    self.player.exp += base_exp
                    self.player.gold += base_gold
                    print(f"   +{base_exp} EXP, +{base_gold} gold")
                    
                    # Chance to find loot
                    if random.random() < 0.3:
                        loot_items = ['health_potion', 'ruby', 'iron_sword', 'leather_armor']
                        loot = random.choice(loot_items)
                        found_item = Item(**self.world.items_db[loot].__dict__)
                        self.player.inventory.append(found_item)
                        print(f"   🎁 You found {found_item.name}!")
                    
                    current_room['monsters'].remove(monster)
                    self.player.level_up()
                    self.turn_count += 1
                    return
            
            elif action == 'd' or action == 'defend':
                print("You raise your guard, reducing incoming damage this turn.")
                defend_this_turn = True
            
            elif action == 'r' or action == 'run':
                escape_chance = 0.7 - (monster.attack / 100)  # Harder to escape from strong monsters
                if random.random() < escape_chance:
                    print("You successfully fled from battle!")
                    self.turn_count += 1
                    return
                else:
                    print("You failed to escape!")
            
            elif action == 'u' or action == 'use':
                potions = [item for item in self.player.inventory if item.type == ItemType.POTION]
                if not potions:
                    print("You have no potions to use!")
                    continue
                
                print("Available potions:")
                for i, potion in enumerate(potions):
                    print(f"   {i + 1}. {potion.name}")
                
                try:
                    choice = int(input("Choose potion (number): ")) - 1
                    if 0 <= choice < len(potions):
                        potion = potions[choice]
                        healed = self.player.heal(potion.effect)
                        self.player.inventory.remove(potion)
                        print(f"You used {potion.name} and restored {healed} health!")
                    else:
                        print("Invalid choice!")
                        continue
                except ValueError:
                    print("Invalid input!")
                    continue
            else:
                print("Invalid action!")
                continue
            
            # Monster's turn
            if monster.health > 0:
                damage = random.randint(monster.attack - 2, monster.attack + 2)
                
                # Apply defend reduction
                if 'defend_this_turn' in locals() and defend_this_turn:
                    damage = int(damage * 0.5)
                    print(f"{monster.name} attacks, but your defense reduces the damage!")
                    defend_this_turn = False
                
                actual_damage = self.player.take_damage(damage)
                print(f"{monster.name} attacks you for {actual_damage} damage!")
                
                if self.player.health <= 0:
                    return
            
            combat_round += 1
        
        self.turn_count += 1
    
    Game.cmd_fight = enhanced_fight

# Initialize the enhanced game systems
enhance_game_class()
add_new_commands()
enhance_combat_system()

# Main execution
if __name__ == "__main__":
    print("🐉 Dragon's Quest RPG - Enhanced Edition 🐉")
    print("=" * 60)
    print("A complete text-based RPG adventure with:")
    print("• Turn-based combat with critical hits and weather effects")
    print("• Crafting system to create powerful items")
    print("• Quest system with multiple objectives")
    print("• Dynamic weather that affects gameplay")
    print("• Save/load game functionality")
    print("• Rich inventory and equipment system")
    print("• Procedurally generated world to explore")
    print("=" * 60)
    
    game = Game()
    game.start_game()
