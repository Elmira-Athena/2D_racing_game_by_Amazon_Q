import pygame
import os
import random
import math

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CAR_WIDTH = 100  # Increased for more detailed car
CAR_HEIGHT = 45  # Slightly taller

def create_pixel_car(width, height, main_color, secondary_color, car_type="default"):
    """Create a pixel art car surface"""
    car = pygame.Surface((width, height), pygame.SRCALPHA)
    
    if car_type == "gtr":
        # Nissan GTR-inspired pixel art
        # Main body
        pygame.draw.rect(car, main_color, (5, 12, width-10, height-20))
        
        # Front bumper (slightly extended)
        pygame.draw.rect(car, (50, 50, 50), (width-20, 15, 15, height-25))
        
        # Hood
        pygame.draw.rect(car, main_color, (20, 8, width-45, 10))
        
        # Roof and windows
        pygame.draw.rect(car, secondary_color, (25, 5, 40, 10))  # Windshield
        pygame.draw.rect(car, main_color, (35, 2, 25, 8))  # Roof
        
        # Iconic GTR taillights (red rectangles)
        pygame.draw.rect(car, (200, 0, 0), (5, 15, 8, 8))  # Upper taillight
        pygame.draw.rect(car, (200, 0, 0), (5, 25, 8, 8))  # Lower taillight
        
        # Headlights
        pygame.draw.rect(car, (220, 220, 220), (width-15, 15, 10, 8))  # Main headlight
        pygame.draw.rect(car, (220, 220, 255), (width-12, 15, 7, 8))  # Headlight glow
        
        # Wheels - larger and more detailed
        wheel_color = (20, 20, 20)
        wheel_rim = (180, 180, 180)
        # Front wheel
        pygame.draw.rect(car, wheel_color, (width-30, height-12, 18, 12))
        pygame.draw.rect(car, wheel_rim, (width-26, height-9, 10, 6))
        # Rear wheel
        pygame.draw.rect(car, wheel_color, (15, height-12, 18, 12))
        pygame.draw.rect(car, wheel_rim, (19, height-9, 10, 6))
        
        # Spoiler (iconic GTR feature)
        pygame.draw.rect(car, (30, 30, 30), (10, 5, 15, 5))
        
        # Side details
        pygame.draw.line(car, (50, 50, 50), (20, height-15), (width-20, height-15), 2)
        
    else:
        # Default car design
        # Main body
        pygame.draw.rect(car, main_color, (5, 10, width-10, height-20))
        
        # Cockpit
        pygame.draw.rect(car, secondary_color, (width//2-5, 5, 15, height-10))
        
        # Wheels
        wheel_color = (40, 40, 40)
        pygame.draw.rect(car, wheel_color, (10, height-8, 15, 8))
        pygame.draw.rect(car, wheel_color, (width-25, height-8, 15, 8))
        
        # Details
        pygame.draw.rect(car, (220, 220, 220), (width-10, height//2-5, 5, 10))  # Headlight
        pygame.draw.rect(car, (200, 0, 0), (5, height//2-5, 5, 10))  # Taillight
    
    return car

def create_flame_particle(size):
    """Create a flame particle for exhaust effects"""
    colors = [
        (255, 60, 0),   # Orange
        (255, 150, 0),  # Yellow-orange
        (255, 220, 0),  # Yellow
    ]
    
    flame = pygame.Surface((size, size), pygame.SRCALPHA)
    color = random.choice(colors)
    pygame.draw.circle(flame, color, (size//2, size//2), size//2)
    return flame

def create_smoke_particle(size):
    """Create a smoke particle for tire effects"""
    gray = random.randint(150, 220)
    smoke = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(smoke, (gray, gray, gray, 150), (size//2, size//2), size//2)
    return smoke

def create_spark_particle(size):
    """Create a spark particle for collision effects"""
    colors = [
        (255, 255, 0),  # Yellow
        (255, 200, 0),  # Gold
        (255, 150, 0),  # Orange
    ]
    
    spark = pygame.Surface((size, size), pygame.SRCALPHA)
    color = random.choice(colors)
    pygame.draw.circle(spark, color, (size//2, size//2), size//2)
    return spark

def load_assets():
    """Load all game assets"""
    assets = {}
    
    # Create player car (Nissan GTR style - metallic gray)
    assets['player_car'] = create_pixel_car(CAR_WIDTH, CAR_HEIGHT, (80, 90, 100), (30, 30, 40), car_type="gtr")
    
    # Create opponent car (red sports car)
    assets['opponent_car'] = create_pixel_car(CAR_WIDTH, CAR_HEIGHT, (220, 30, 30), (30, 30, 30))
    
    # Create backgrounds for different seasons
    assets['background_spring'] = create_background("spring")
    assets['background_summer'] = create_background("summer")
    assets['background_autumn'] = create_background("autumn")
    assets['background_winter'] = create_background("winter")
    
    # Create UI elements
    font = pygame.font.SysFont(None, 48)
    assets['font'] = font
    
    return assets

def create_background(season="summer"):
    """Create the game background with different seasons"""
    bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # Sky gradient - different for each season
    if season == "spring":
        # Spring - light blue with some clouds
        for y in range(SCREEN_HEIGHT//2):
            # Light blue gradient
            color = (135 + y//5, 206 + y//10, 235)
            pygame.draw.line(bg, color, (0, y), (SCREEN_WIDTH, y))
        
        # Add some fluffy clouds
        for _ in range(6):
            cloud_x = random.randint(0, SCREEN_WIDTH)
            cloud_y = random.randint(20, SCREEN_HEIGHT//3)
            cloud_size = random.randint(20, 50)
            for i in range(5):  # Multiple circles for each cloud
                offset_x = random.randint(-15, 15)
                offset_y = random.randint(-10, 10)
                pygame.draw.circle(bg, (250, 250, 250), 
                                  (cloud_x + offset_x, cloud_y + offset_y), 
                                  cloud_size // 2)
    
    elif season == "summer":
        # Summer - bright blue sky
        for y in range(SCREEN_HEIGHT//2):
            # Bright blue gradient
            color = (100 + y//3, 150 + y//3, 235)
            pygame.draw.line(bg, color, (0, y), (SCREEN_WIDTH, y))
        
        # Add a bright sun
        sun_x = SCREEN_WIDTH - 100
        sun_y = 80
        pygame.draw.circle(bg, (255, 240, 100), (sun_x, sun_y), 40)
        pygame.draw.circle(bg, (255, 255, 200), (sun_x, sun_y), 30)
    
    elif season == "autumn":
        # Autumn - orange/red sunset sky
        for y in range(SCREEN_HEIGHT//2):
            # Gradient from orange to light blue
            r = min(255, 180 + (SCREEN_HEIGHT//2 - y) // 2)
            g = min(255, 100 + y // 3)
            b = min(255, 50 + y)
            pygame.draw.line(bg, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Add some scattered clouds
        for _ in range(4):
            cloud_x = random.randint(0, SCREEN_WIDTH)
            cloud_y = random.randint(30, SCREEN_HEIGHT//3)
            cloud_width = random.randint(60, 120)
            cloud_height = random.randint(15, 30)
            pygame.draw.ellipse(bg, (200, 150, 150), 
                               (cloud_x, cloud_y, cloud_width, cloud_height))
    
    else:  # winter
        # Winter - light gray sky with snow
        for y in range(SCREEN_HEIGHT//2):
            # Cold blue-gray gradient
            color = (200 + y//10, 200 + y//10, 220 + y//10)
            pygame.draw.line(bg, color, (0, y), (SCREEN_WIDTH, y))
        
        # Add some snowflakes
        for _ in range(50):
            snow_x = random.randint(0, SCREEN_WIDTH)
            snow_y = random.randint(0, SCREEN_HEIGHT//2)
            snow_size = random.randint(1, 3)
            pygame.draw.circle(bg, (255, 255, 255), (snow_x, snow_y), snow_size)
    
    # Mountains - different colors based on season
    if season == "spring":
        mountain_colors = [(70, 120, 70), (80, 130, 80), (90, 140, 90)]
    elif season == "summer":
        mountain_colors = [(60, 100, 60), (70, 110, 70), (80, 120, 80)]
    elif season == "autumn":
        mountain_colors = [(120, 90, 60), (140, 100, 60), (160, 110, 70)]
    else:  # winter
        mountain_colors = [(220, 220, 240), (200, 200, 220), (180, 180, 200)]
    
    for i in range(5):
        height = random.randint(50, 150)
        width = random.randint(200, 400)
        x = random.randint(-100, SCREEN_WIDTH)
        
        points = [
            (x, SCREEN_HEIGHT//2),
            (x + width//2, SCREEN_HEIGHT//2 - height),
            (x + width, SCREEN_HEIGHT//2)
        ]
        
        color = random.choice(mountain_colors)
        pygame.draw.polygon(bg, color, points)
    
    # Ground - different for each season
    if season == "spring":
        ground_color = (100, 180, 100)  # Bright green
        grass_colors = [(130, 200, 100), (120, 190, 90), (140, 210, 110)]
    elif season == "summer":
        ground_color = (80, 150, 80)  # Deep green
        grass_colors = [(100, 170, 80), (90, 160, 70), (110, 180, 90)]
    elif season == "autumn":
        ground_color = (170, 140, 80)  # Brownish
        grass_colors = [(180, 130, 60), (190, 140, 70), (170, 120, 50)]
    else:  # winter
        ground_color = (230, 230, 240)  # Snow white
        grass_colors = [(210, 210, 220), (220, 220, 230), (200, 200, 210)]
    
    pygame.draw.rect(bg, ground_color, (0, SCREEN_HEIGHT//2, SCREEN_WIDTH, SCREEN_HEIGHT//2))
    
    # Add some ground details based on season
    for _ in range(100):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(SCREEN_HEIGHT//2, SCREEN_HEIGHT)
        size = random.randint(2, 6)
        color = random.choice(grass_colors)
        
        if season == "autumn":
            # Draw small leaf-like shapes
            if random.random() > 0.7:
                points = [
                    (x, y),
                    (x + size, y - size),
                    (x + size*2, y),
                    (x + size, y + size)
                ]
                pygame.draw.polygon(bg, color, points)
        elif season == "winter":
            # Draw snow patches
            if random.random() > 0.8:
                pygame.draw.circle(bg, (255, 255, 255), (x, y), size)
        else:
            # Draw grass tufts
            if random.random() > 0.8:
                pygame.draw.line(bg, color, (x, y), (x, y - size*2), 2)
    
    # Road - same for all seasons but with weather effects
    road_y = SCREEN_HEIGHT//2 + 50
    road_height = 100
    
    # Base road
    road_color = (40, 40, 40)
    if season == "winter":
        # Slightly lighter road with snow
        road_color = (60, 60, 65)
    
    pygame.draw.rect(bg, road_color, (0, road_y, SCREEN_WIDTH, road_height))
    
    # Road markings
    for i in range(40):  # More markings for longer track
        if season == "winter" and random.random() > 0.7:
            # Some markings covered by snow
            continue
            
        pygame.draw.rect(bg, (255, 255, 255), (i * 50, road_y + road_height//2, 30, 5))
    
    # Add season-specific road effects
    if season == "autumn":
        # Scattered leaves on the road
        for _ in range(15):
            leaf_x = random.randint(0, SCREEN_WIDTH)
            leaf_y = random.randint(road_y, road_y + road_height)
            leaf_size = random.randint(2, 4)
            leaf_color = random.choice([(200, 100, 50), (220, 120, 40), (180, 80, 30)])
            pygame.draw.circle(bg, leaf_color, (leaf_x, leaf_y), leaf_size)
    
    elif season == "winter":
        # Snow patches on the road
        for _ in range(20):
            snow_x = random.randint(0, SCREEN_WIDTH)
            snow_y = random.randint(road_y, road_y + road_height)
            snow_width = random.randint(10, 30)
            snow_height = random.randint(5, 15)
            pygame.draw.ellipse(bg, (200, 200, 210), 
                               (snow_x, snow_y, snow_width, snow_height))
    
    return bg
