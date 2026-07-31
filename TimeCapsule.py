import json
import os
import time
from datetime import datetime

DATA_FILE = "capsules.json"

def load_capsules():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_capsules(capsules):
    with open(DATA_FILE, "w") as f:
        json.dump(capsules, f, indent=2)

def create_capsule():
    print("📦 Let's create a new time capsule.")
    msg = input("What message do you want to send to your future self?\n> ")
    date_str = input("When should it unlock? (YYYY-MM-DD)\n> ")
    try:
        unlock_time = datetime.strptime(date_str, "%Y-%m-%d")
        if unlock_time <= datetime.now():
            print("⛔ That date is in the past!")
            return
    except ValueError:
        print("Invalid date format.")
        return

    capsule = {
        "message": msg,
        "unlock_time": unlock_time.isoformat(),
        "created": datetime.now().isoformat(),
        "opened": False
    }
    capsules = load_capsules()
    capsules.append(capsule)
    save_capsules(capsules)
    print("✅ Time capsule sealed. Come back later!")

def open_capsules():
    print("🔓 Checking for capsules to open...")
    now = datetime.now()
    capsules = load_capsules()
    found = False
    for cap in capsules:
        unlock_time = datetime.fromisoformat(cap["unlock_time"])
        if not cap["opened"] and now >= unlock_time:
            print(f"\n🕰️ Capsule from {cap['created']}:\n> {cap['message']}\n")
            cap["opened"] = True
            found = True
    if not found:
        print("⏳ No capsules are ready yet.")
    save_capsules(capsules)

def main():
    os.system("cls" if os.name == "nt" else "clear")
    print("=== 🕰️ Terminal Time Capsule ===")
    print("1. Create a time capsule")
    print("2. Open ready capsules")
    print("3. Exit")
    choice = input("> ")

    if choice == "1":
        create_capsule()
    elif choice == "2":
        open_capsules()
    else:
        print("Goodbye.")

if __name__ == "__main__":
    main()
