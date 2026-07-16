import os, time, math

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def wave_cursor():
    w = 60
    while True:
        clear()
        t = time.time()
        for i in range(20):
            x = int(w/2 + math.cos(t + i/3) * (w/3))
            print(' ' * x + 'o')
        time.sleep(0.05)

try:
    wave_cursor()
except KeyboardInterrupt:
    print("\nStopped.")
