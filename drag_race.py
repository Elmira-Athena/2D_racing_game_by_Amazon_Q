import pygame
import sys
import random
import math
from pygame.locals import *

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
ROAD_COLOR = (50, 50, 50)
LINE_COLOR = (255, 255, 255)
SKY_COLOR = (135, 206, 235)
GRASS_COLOR = (76, 153, 0)

# Car properties
CAR_WIDTH = 80
CAR_HEIGHT = 40
PLAYER_START_POS = (100, SCREEN_HEIGHT - 150)
OPPONENT_START_POS = (100, SCREEN_HEIGHT - 250)
MAX_SPEED = 15
ACCELERATION = 0.2
DRAG = 0.05

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pixel Art Drag Race")
clock = pygame.time.Clock()

# Load assets
def load_assets():
    # We'll create placeholder assets for now
    # In a real game, you'd load actual pixel art images
    player_car = pygame.Surface((CAR_WIDTH, CAR_HEIGHT))
    player_car.fill((255, 0, 0))  # Red car
    
    opponent_car = pygame.Surface((CAR_WIDTH, CAR_HEIGHT))
    opponent_car.fill((0, 0, 255))  # Blue car
    
    # Create simple pixel art for the cars
    pygame.draw.rect(player_car, (200, 0, 0), (10, 5, 60, 30))
    pygame.draw.rect(player_car, (100, 100, 100), (15, 10, 20, 20))
    pygame.draw.rect(player_car, (100, 100, 100), (60, 10, 15, 20))
    
    pygame.draw.rect(opponent_car, (0, 0, 200), (10, 5, 60, 30))
    pygame.draw.rect(opponent_car, (100, 100, 100), (15, 10, 20, 20))
    pygame.draw.rect(opponent_car, (100, 100, 100), (60, 10, 15, 20))
    
    return {
        'player_car': player_car,
        'opponent_car': opponent_car
    }

# Particle system for effects
class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def add_particle(self, x, y, color, size, speed, direction, lifetime):
        self.particles.append({
            'x': x,
            'y': y,
            'color': color,
            'size': size,
            'speed': speed,
            'direction': direction,
            'lifetime': lifetime,
            'age': 0
        })
    
    def update(self):
        for particle in self.particles[:]:
            particle['x'] += math.cos(particle['direction']) * particle['speed']
            particle['y'] += math.sin(particle['direction']) * particle['speed']
            particle['age'] += 1
            
            # Remove particles that have exceeded their lifetime
            if particle['age'] >= particle['lifetime']:
                self.particles.remove(particle)
    
    def draw(self, surface):
        for particle in self.particles:
            # Fade out as the particle ages
            alpha = 255 * (1 - particle['age'] / particle['lifetime'])
            size = max(1, particle['size'] * (1 - particle['age'] / particle['lifetime']))
            
            # Create a surface for the particle with alpha
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                particle_surface, 
                (*particle['color'], alpha), 
                (size, size), 
                size
            )
            surface.blit(particle_surface, (particle['x'] - size, particle['y'] - size))

# Car class
class Car:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.speed = 0
        self.acceleration = 0
        self.finished = False
        self.finish_time = 0
        self.start_time = 0
    
    def update(self):
        # Apply acceleration and drag
        self.speed += self.acceleration
        self.speed -= self.drag * self.speed
        
        # Clamp speed
        if self.speed > MAX_SPEED:
            self.speed = MAX_SPEED
        elif self.speed < 0:
            self.speed = 0
            
        # Move car
        self.x += self.speed
        
        # Check if car has finished
        if self.x >= SCREEN_WIDTH - CAR_WIDTH and not self.finished:
            self.finished = True
            self.finish_time = pygame.time.get_ticks()
    
    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

# Game class
class DragRaceGame:
    def __init__(self):
        self.assets = load_assets()
        self.player = Car(PLAYER_START_POS[0], PLAYER_START_POS[1], self.assets['player_car'])
        self.opponent = Car(OPPONENT_START_POS[0], OPPONENT_START_POS[1], self.assets['opponent_car'])
        self.particles = ParticleSystem()
        self.game_state = "ready"  # ready, countdown, racing, finished
        self.countdown = 3
        self.countdown_timer = 0
        self.race_start_time = 0
        self.font = pygame.font.SysFont(None, 48)
    
    def start_countdown(self):
        self.game_state = "countdown"
        self.countdown = 3
        self.countdown_timer = pygame.time.get_ticks()
    
    def start_race(self):
        self.game_state = "racing"
        self.race_start_time = pygame.time.get_ticks()
        self.player.start_time = self.race_start_time
        self.opponent.start_time = self.race_start_time
        
        # Set AI opponent behavior
        self.opponent.acceleration = ACCELERATION * random.uniform(0.8, 1.1)
        self.opponent.drag = DRAG * random.uniform(0.9, 1.1)
    
    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Handle countdown
        if self.game_state == "countdown":
            if current_time - self.countdown_timer > 1000:
                self.countdown -= 1
                self.countdown_timer = current_time
                
                if self.countdown <= 0:
                    self.start_race()
        
        # Update cars
        if self.game_state == "racing":
            self.player.update()
            self.opponent.update()
            
            # Create exhaust particles for player
            if self.player.speed > 0:
                for _ in range(int(self.player.speed)):
                    self.particles.add_particle(
                        self.player.x + 10,
                        self.player.y + CAR_HEIGHT - 10,
                        (200, 200, 200),
                        random.uniform(2, 5),
                        random.uniform(1, 3),
                        math.pi + random.uniform(-0.3, 0.3),
                        random.randint(20, 40)
                    )
            
            # Create exhaust particles for opponent
            if self.opponent.speed > 0:
                for _ in range(int(self.opponent.speed)):
                    self.particles.add_particle(
                        self.opponent.x + 10,
                        self.opponent.y + CAR_HEIGHT - 10,
                        (200, 200, 200),
                        random.uniform(2, 5),
                        random.uniform(1, 3),
                        math.pi + random.uniform(-0.3, 0.3),
                        random.randint(20, 40)
                    )
            
            # Check if race is finished
            if self.player.finished and self.opponent.finished:
                self.game_state = "finished"
        
        # Update particles
        self.particles.update()
        
        # Check for race finish
        if self.player.finished and self.opponent.finished and self.game_state == "racing":
            self.game_state = "finished"
    
    def draw(self):
        # Draw background
        screen.fill(SKY_COLOR)
        
        # Draw grass
        pygame.draw.rect(screen, GRASS_COLOR, (0, SCREEN_HEIGHT - 300, SCREEN_WIDTH, 100))
        pygame.draw.rect(screen, GRASS_COLOR, (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
        
        # Draw road
        pygame.draw.rect(screen, ROAD_COLOR, (0, SCREEN_HEIGHT - 200, SCREEN_WIDTH, 100))
        
        # Draw lane dividers
        for i in range(20):
            pygame.draw.rect(screen, LINE_COLOR, (i * 50, SCREEN_HEIGHT - 150, 30, 5))
        
        # Draw finish line
        pygame.draw.rect(screen, LINE_COLOR, (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 200, 10, 100))
        
        # Draw particles
        self.particles.draw(screen)
        
        # Draw cars
        self.player.draw(screen)
        self.opponent.draw(screen)
        
        # Draw UI
        if self.game_state == "ready":
            text = self.font.render("Press SPACE to start!", True, (255, 255, 255))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 100))
        
        elif self.game_state == "countdown":
            text = self.font.render(str(self.countdown), True, (255, 0, 0))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 100))
        
        elif self.game_state == "racing":
            elapsed = (pygame.time.get_ticks() - self.race_start_time) / 1000
            text = self.font.render(f"Time: {elapsed:.2f}s", True, (255, 255, 255))
            screen.blit(text, (20, 20))
        
        elif self.game_state == "finished":
            player_time = (self.player.finish_time - self.player.start_time) / 1000
            opponent_time = (self.opponent.finish_time - self.opponent.start_time) / 1000
            
            if player_time < opponent_time:
                result = "You Win!"
                color = (0, 255, 0)
            elif opponent_time < player_time:
                result = "You Lose!"
                color = (255, 0, 0)
            else:
                result = "It's a Tie!"
                color = (255, 255, 0)
            
            text1 = self.font.render(result, True, color)
            text2 = self.font.render(f"Your Time: {player_time:.2f}s", True, (255, 255, 255))
            text3 = self.font.render(f"Opponent Time: {opponent_time:.2f}s", True, (255, 255, 255))
            text4 = self.font.render("Press R to restart", True, (255, 255, 255))
            
            screen.blit(text1, (SCREEN_WIDTH // 2 - text1.get_width() // 2, 100))
            screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, 150))
            screen.blit(text3, (SCREEN_WIDTH // 2 - text3.get_width() // 2, 200))
            screen.blit(text4, (SCREEN_WIDTH // 2 - text4.get_width() // 2, 250))
    
    def reset(self):
        self.__init__()

# Main game loop
def main():
    game = DragRaceGame()
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            
            if event.type == KEYDOWN:
                if event.key == K_SPACE and game.game_state == "ready":
                    game.start_countdown()
                
                if event.key == K_r and game.game_state == "finished":
                    game.reset()
        
        # Handle player input
        keys = pygame.key.get_pressed()
        if game.game_state == "racing":
            if keys[K_RIGHT] or keys[K_UP]:
                game.player.acceleration = ACCELERATION
            else:
                game.player.acceleration = 0
                game.player.drag = DRAG
        
        # Update game state
        game.update()
        
        # Draw everything
        game.draw()
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
