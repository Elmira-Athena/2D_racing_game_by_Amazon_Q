import pygame
import random
import math

class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def add_particle(self, x, y, color, size, speed, direction, lifetime, alpha=255, type="circle"):
        """
        Add a particle to the system
        
        Parameters:
        - x, y: Position
        - color: RGB tuple
        - size: Particle size
        - speed: Movement speed
        - direction: Angle in radians
        - lifetime: How many frames the particle lives
        - alpha: Transparency (0-255)
        - type: "circle" or "rect"
        """
        self.particles.append({
            'x': x,
            'y': y,
            'color': color,
            'size': size,
            'speed': speed,
            'direction': direction,
            'lifetime': lifetime,
            'max_lifetime': lifetime,
            'alpha': alpha,
            'type': type
        })
    
    def add_flame(self, x, y):
        """Add exhaust flame particles"""
        colors = [
            (255, 60, 0),   # Orange
            (255, 150, 0),  # Yellow-orange
            (255, 220, 0),  # Yellow
        ]
        
        for _ in range(3):
            self.add_particle(
                x, y,
                random.choice(colors),
                random.uniform(3, 8),
                random.uniform(1, 4),
                math.pi + random.uniform(-0.3, 0.3),
                random.randint(10, 30),
                200
            )
    
    def add_smoke(self, x, y):
        """Add tire smoke particles"""
        gray = random.randint(180, 220)
        
        for _ in range(2):
            self.add_particle(
                x, y,
                (gray, gray, gray),
                random.uniform(5, 10),
                random.uniform(0.5, 2),
                random.uniform(0, 2 * math.pi),
                random.randint(30, 60),
                150
            )
    
    def add_sparks(self, x, y, count=10):
        """Add spark particles (for collisions, boost, etc)"""
        colors = [
            (255, 255, 0),  # Yellow
            (255, 200, 0),  # Gold
            (255, 150, 0),  # Orange
        ]
        
        for _ in range(count):
            self.add_particle(
                x, y,
                random.choice(colors),
                random.uniform(1, 4),
                random.uniform(2, 6),
                random.uniform(0, 2 * math.pi),
                random.randint(10, 25),
                255,
                "rect" if random.random() > 0.7 else "circle"
            )
    
    def add_air_stream(self, x, y):
        """Add air stream particles for flying effect"""
        colors = [
            (200, 200, 255),  # Light blue
            (220, 220, 255),  # Lighter blue
            (180, 180, 255),  # Slightly darker blue
        ]
        
        for _ in range(5):
            self.add_particle(
                x, y,
                random.choice(colors),
                random.uniform(2, 5),
                random.uniform(3, 7),
                math.pi + random.uniform(-0.2, 0.2),
                random.randint(10, 20),
                150,
                "rect" if random.random() > 0.5 else "circle"
            )
    
    def add_boost_trail(self, x, y):
        """Add enhanced boost trail particles"""
        colors = [
            (255, 100, 0),   # Orange
            (255, 50, 0),    # Red-orange
            (255, 200, 0),   # Yellow
            (255, 255, 100), # Light yellow
        ]
        
        for _ in range(8):
            size = random.uniform(3, 10)
            self.add_particle(
                x + random.uniform(-5, 5), 
                y + random.uniform(-5, 5),
                random.choice(colors),
                size,
                random.uniform(2, 5),
                math.pi + random.uniform(-0.5, 0.5),
                random.randint(15, 35),
                200,
                "circle"
            )
            
            # Add smaller "spark" particles
            if random.random() > 0.7:
                self.add_particle(
                    x + random.uniform(-10, 10), 
                    y + random.uniform(-10, 10),
                    (255, 255, 200),
                    random.uniform(1, 3),
                    random.uniform(3, 8),
                    random.uniform(0, 2 * math.pi),
                    random.randint(5, 15),
                    255,
                    "rect"
                )
    
    def update(self):
        """Update all particles"""
        for particle in self.particles[:]:
            # Move particle
            particle['x'] += math.cos(particle['direction']) * particle['speed']
            particle['y'] += math.sin(particle['direction']) * particle['speed']
            
            # Decrease lifetime
            particle['lifetime'] -= 1
            
            # Remove dead particles
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface):
        """Draw all particles"""
        for particle in self.particles:
            # Calculate fade based on lifetime
            fade_ratio = particle['lifetime'] / particle['max_lifetime']
            current_alpha = int(particle['alpha'] * fade_ratio)
            current_size = max(1, particle['size'] * fade_ratio)
            
            # Create a surface for the particle with alpha
            particle_surface = pygame.Surface((int(current_size * 2), int(current_size * 2)), pygame.SRCALPHA)
            
            # Draw the particle
            color_with_alpha = (*particle['color'], current_alpha)
            
            if particle['type'] == "circle":
                pygame.draw.circle(
                    particle_surface, 
                    color_with_alpha, 
                    (int(current_size), int(current_size)), 
                    int(current_size)
                )
            else:  # rect
                pygame.draw.rect(
                    particle_surface,
                    color_with_alpha,
                    (0, 0, int(current_size * 2), int(current_size * 2))
                )
            
            # Draw to main surface
            surface.blit(particle_surface, (int(particle['x'] - current_size), int(particle['y'] - current_size)))
