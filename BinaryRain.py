import random, time, os

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def binary_rain():
    w, h = 60, 20
    columns = [0] * w
    while True:
        clear()
        for y in range(h):
            line = ''
            for x in range(w):
                if random.random() < 0.05:
                    line += str(random.randint(0, 1))
                else:
                    line += ' '
            print(line)
        time.sleep(0.07)

try:
    binary_rain()
except KeyboardInterrupt:
    print("\nBye.")
