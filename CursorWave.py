import sys
import time
import math

def wave_cursor(width: int = 60, height: int = 20, speed: float = 1.0, symbol: str = 'o') -> None:
    """
    Renders a waving animation in the terminal.
    
    :param width: Maximum width of the wave.
    :param height: Number of lines in the wave.
    :param speed: Speed multiplier for the wave animation.
    :param symbol: The character(s) used to draw the wave.
    """
    # Clear screen once at the beginning
    sys.stdout.write('\033[2J')
    
    # Hide the terminal blinking cursor for a cleaner animation
    sys.stdout.write('\033[?25l') 
    
    try:
        while True:
            # Move cursor to the top-left (0,0) instead of clearing the screen
            # This completely eliminates screen flickering
            sys.stdout.write('\033[H') 
            
            t = time.time() * speed
            
            # Build the entire frame as a single string (faster than multiple prints)
            frame_lines = []
            for i in range(height):
                # Calculate X position
                x = int(width / 2 + math.cos(t + i / 3.0) * (width / 3))
                frame_lines.append(' ' * x + symbol)
                
            # Print the whole frame at once
            sys.stdout.write('\n'.join(frame_lines) + '\n')
            sys.stdout.flush()
            
            # ~20 Frames per second
            time.sleep(0.05) 
            
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        # Always restore the blinking cursor when exiting, even on errors
        sys.stdout.write('\033[?25h')

if __name__ == '__main__':
    # You can now easily tweak the parameters
    wave_cursor(width=80, height=25, speed=1.5, symbol='🌊')
