import sys
import time
import math
import random
from dataclasses import dataclass

@dataclass
class Spark:
    """A small particle that drifts off the comet."""
    x: float
    y: float
    life: float
    char: str

def comet(width: int = 80, height: int = 20, trail_length: int = 12) -> None:
    """
    Renders a comet with a trailing tail flying across the terminal.
    """
    # ANSI escape codes
    HIDE_CURSOR = '\033[?25l'
    SHOW_CURSOR = '\033[?25h'
    CLEAR_SCREEN = '\033[2J'
    HOME = '\033[H'
    
    # Visual characters (head → tail)
    HEAD = '@'
    TRAIL_CHARS = ['*', '*', 'o', 'o', '.', '.', '·', '·', '-', '-', ' ']
    SPARK_CHARS = ['·', '.', '+', '*']
    
    sparks: list[Spark] = []
    
    sys.stdout.write(CLEAR_SCREEN + HIDE_CURSOR)
    
    try:
        while True:
            t = time.time()
            
            # Head position: moves right with a sine wave vertical motion
            cycle_width = width + trail_length + 20
            head_x = int(t * 18) % cycle_width - 10
            head_y = height // 2 + int(math.sin(t * 1.5) * (height // 3))
            head_y = max(0, min(height - 1, head_y))
            
            # Initialize screen buffer
            screen = [[' '] * width for _ in range(height)]
            
            # Spawn random sparks near the head
            if random.random() < 0.4 and 0 <= head_x < width:
                sparks.append(Spark(
                    x=float(head_x),
                    y=float(head_y) + random.uniform(-1, 1),
                    life=random.uniform(0.3, 0.8),
                    char=random.choice(SPARK_CHARS)
                ))
            
            # Update and draw sparks
            surviving_sparks = []
            for spark in sparks:
                spark.life -= 0.05
                spark.x -= random.uniform(0.3, 0.8)  # drift left (behind comet)
                spark.y += random.uniform(-0.4, 0.4)  # flutter up/down
                
                if spark.life > 0:
                    sx, sy = int(spark.x), int(spark.y)
                    if 0 <= sx < width and 0 <= sy < height:
                        screen[sy][sx] = spark.char
                    surviving_sparks.append(spark)
            sparks = surviving_sparks
            
            # Draw trail (follows the head's wave path with delay)
            for i in range(trail_length, 0, -1):
                trail_x = head_x - i
                trail_t = t - i * 0.025  # time delay for trailing effect
                trail_y = height // 2 + int(math.sin(trail_t * 1.5) * (height // 3))
                trail_y = max(0, min(height - 1, trail_y))
                
                if 0 <= trail_x < width:
                    char_idx = min(i - 1, len(TRAIL_CHARS) - 1)
                    screen[trail_y][trail_x] = TRAIL_CHARS[char_idx]
            
            # Draw head (on top of everything)
            if 0 <= head_x < width:
                screen[head_y][head_x] = HEAD
            
            # Render entire frame at once
            sys.stdout.write(HOME)
            frame = '\n'.join(''.join(row) for row in screen)
            sys.stdout.write(frame + '\n')
            sys.stdout.flush()
            
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\nComet vanished.")
    finally:
        # Always restore cursor visibility
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.flush()


if __name__ == '__main__':
    comet(width=70, height=18, trail_length=15)
