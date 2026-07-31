import time
import random
import os

def clear():
    os.system("cls" if os.name == "nt" else "clear")

class Pet:
    def __init__(self, name):
        self.name = name
        self.hunger = 50
        self.energy = 50
        self.happiness = 50

    def status(self):
        print(f"=== {self.name} STATUS ===")
        print("Hunger   :", self.hunger)
        print("Energy   :", self.energy)
        print("Happiness:", self.happiness)
        print()

    def feed(self):
        self.hunger = max(0, self.hunger - 20)
        self.happiness += 5

    def sleep(self):
        self.energy = min(100, self.energy + 30)

    def play(self):
        if self.energy >= 10:
            self.happiness += 15
            self.energy -= 10
            self.hunger += 10
        else:
            print("Too tired to play!")

    def tick(self):
        self.hunger += 5
        self.energy -= 5
        self.happiness -= 3

    def is_alive(self):
        return self.hunger < 100 and self.energy > 0 and self.happiness > 0


name = input("Apne pet ka naam daal: ")
pet = Pet(name)

while pet.is_alive():
    clear()
    pet.status()

    print("1. Feed")
    print("2. Sleep")
    print("3. Play")
    print("4. Wait")

    choice = input("Choose: ")

    if choice == "1":
        pet.feed()
    elif choice == "2":
        pet.sleep()
    elif choice == "3":
        pet.play()
    elif choice == "4":
        pass

    pet.tick()
    time.sleep(1)

clear()
print(f"{pet.name} is no more 💀")
