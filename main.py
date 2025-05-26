#!/usr/bin/env python3
"""
Pixel Art Drag Race
A 2D racing game with pixel art graphics and colorful effects
"""

import pygame
import sys
from game_new import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit()
    except Exception as e:
        print(f"Error: {e}")
        pygame.quit()
        sys.exit(1)
