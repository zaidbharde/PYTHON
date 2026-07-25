import time
import random
import os
from datetime import datetime, timedelta

def clear():
    os.system("cls" if os.name == "nt" else "clear")

virtual_time = datetime.now()
speed = 1.0

try:
    while True:
        if random.random() < 0.18:
            speed = random.choice([0.25, 0.5, 1, 2, 3, 5, -1])

        if random.random() < 0.10:
            virtual_time += timedelta(seconds=random.randint(-180, 180))

        virtual_time += timedelta(seconds=speed)

        clear()
        print("=== REALITY DISTORTION CLOCK ===")
        print("Real Time      :", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("Distorted Time :", virtual_time.strftime("%Y-%m-%d %H:%M:%S"))
        print("Current Speed  :", f"{speed}x")
        print("\nCtrl+C to exit")

        time.sleep(1)

except KeyboardInterrupt:
    print("\nClock stopped.")
