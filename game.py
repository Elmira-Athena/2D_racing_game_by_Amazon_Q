import pygame
import sys
import random
import math
from pygame.locals import *
from assets import load_assets, SCREEN_WIDTH, SCREEN_HEIGHT
from particles import ParticleSystem
from car import PlayerCar, AICar

# Initialize pygame
pygame.init()

# Game constants
FPS = 60
RACE_DISTANCE = 6000  # Extended race distance (was 3000)
LANE_HEIGHT = 80

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pixel Art Drag Race")
clock = pygame.time.Clock()

class DragRaceGame:
    def __init__(self):
        self.assets = load_assets()
        self.game_state = "title"  # title, ready, countdown, racing, finished
        self.countdown = 3
        self.countdown_timer = 0
        self.race_start_time = 0
        self.camera_offset = 0
        
        # Season tracking
        self.seasons = ["spring", "summer", "autumn", "winter"]
        self.current_season = 0
        self.season_change_distance = RACE_DISTANCE / len(self.seasons)
        
        # Create ramps
        self.ramps = [
            {"position": 1000, "height": 30},
            {"position": 2500, "height": 50},
            {"position": 4000, "height": 70},
            {"position": 5500, "height": 40}
        ]
        
        # Create lanes
        self.lanes = [
            {"y": SCREEN_HEIGHT - 180},  # Player lane
            {"y": SCREEN_HEIGHT - 260}   # Opponent lane
        ]
        
        # Create cars
        self.player = PlayerCar(100, self.lanes[0]["y"], self.assets['player_car'], 0)
        self.opponent = AICar(100, self.lanes[1]["y"], self.assets['opponent_car'], 1, difficulty=1.0)
        
        # Create global particle system for environment effects
        self.particles = ParticleSystem()
        
        # Create finish line
        self.finish_line_x = RACE_DISTANCE
        
        # UI elements
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 24)
    
    def start_countdown(self):
        self.game_state = "countdown"
        self.countdown = 3
        self.countdown_timer = pygame.time.get_ticks()
    
    def start_race(self):
        self.game_state = "racing"
        self.race_start_time = pygame.time.get_ticks()
        self.player.start_time = self.race_start_time
        self.opponent.start_time = self.race_start_time
    
    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Handle countdown
        if self.game_state == "countdown":
            if current_time - self.countdown_timer > 1000:
                self.countdown -= 1
                self.countdown_timer = current_time
                
                # Add countdown effects
                for _ in range(20):
                    self.particles.add_sparks(
                        SCREEN_WIDTH // 2,
                        SCREEN_HEIGHT // 2 + 50,
                        30
                    )
                
                if self.countdown <= 0:
                    self.start_race()
        
        # Update cars
        race_active = self.game_state == "racing"
        self.player.update(race_active, self.ramps)
        self.opponent.update(race_active, self.ramps)
        
        # Check for finish
        if race_active:
            # Update camera to follow player
            target_offset = max(0, self.player.distance - 300)
            self.camera_offset += (target_offset - self.camera_offset) * 0.1
            
            # Check if player finished
            if self.player.distance >= RACE_DISTANCE and not self.player.finished:
                self.player.finished = True
                self.player.finish_time = current_time
                
                # Add finish effects
                for _ in range(50):
                    self.particles.add_sparks(
                        SCREEN_WIDTH - 100 + random.uniform(-20, 20),
                        self.player.y + random.uniform(-20, 20),
                        50
                    )
            
            # Check if opponent finished
            if self.opponent.distance >= RACE_DISTANCE and not self.opponent.finished:
                self.opponent.finished = True
                self.opponent.finish_time = current_time
                
                # Add finish effects
                for _ in range(50):
                    self.particles.add_sparks(
                        SCREEN_WIDTH - 100 + random.uniform(-20, 20),
                        self.opponent.y + random.uniform(-20, 20),
                        50
                    )
            
            # Check if race is over
            if self.player.finished and self.opponent.finished:
                self.game_state = "finished"
        
        # Update particles
        self.particles.update()
        
        # Add random environment particles
        if random.random() < 0.1 and self.game_state in ["racing", "countdown"]:
            self.particles.add_particle(
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT // 2),
                (255, 255, 255),
                random.uniform(1, 3),
                random.uniform(0.5, 2),
                math.pi / 2 + random.uniform(-0.2, 0.2),
                random.randint(30, 90),
                100
            )
    
    def draw(self):
        # Determine which season background to use based on player's progress
        if self.game_state == "racing" or self.game_state == "finished":
            progress = min(1.0, self.player.distance / RACE_DISTANCE)
            season_index = min(3, int(progress * 4))
            current_season = self.seasons[season_index]
            
            # Draw the appropriate seasonal background
            if current_season == "spring":
                screen.blit(self.assets['background_spring'], (0, 0))
            elif current_season == "summer":
                screen.blit(self.assets['background_summer'], (0, 0))
            elif current_season == "autumn":
                screen.blit(self.assets['background_autumn'], (0, 0))
            else:  # winter
                screen.blit(self.assets['background_winter'], (0, 0))
                
            # Add season transition effects
            if self.game_state == "racing":
                # Calculate if we're near a season boundary
                for i in range(1, 4):
                    boundary = i * self.season_change_distance
                    if abs(self.player.distance - boundary) < 100:
                        # Add particles for season transition
                        for _ in range(5):
                            x = random.randint(0, SCREEN_WIDTH)
                            y = random.randint(0, SCREEN_HEIGHT // 2)
                            
                            if i == 1:  # Spring to Summer
                                color = (255, 255, 100)  # Yellow for summer sun
                            elif i == 2:  # Summer to Autumn
                                color = (200, 100, 50)  # Orange for autumn leaves
                            else:  # Autumn to Winter
                                color = (255, 255, 255)  # White for winter snow
                                
                            self.particles.add_particle(
                                x, y,
                                color,
                                random.uniform(2, 5),
                                random.uniform(1, 3),
                                math.pi / 2 + random.uniform(-0.5, 0.5),
                                random.randint(30, 60),
                                150
                            )
        else:
            # Default to summer background for menus
            screen.blit(self.assets['background_summer'], (0, 0))
        
        # Draw ramps
        for ramp in self.ramps:
            ramp_x = ramp["position"] - self.camera_offset
            if 0 <= ramp_x <= SCREEN_WIDTH:
                # Draw ramp base
                ramp_width = 80
                ramp_height = ramp["height"]
                
                # Draw ramp with gradient
                for i in range(ramp_width):
                    height_at_point = int((i / ramp_width) * ramp_height)
                    
                    # Calculate color based on season
                    progress = min(1.0, self.player.distance / RACE_DISTANCE)
                    season_index = min(3, int(progress * 4))
                    current_season = self.seasons[season_index]
                    
                    if current_season == "spring":
                        ramp_color = (100, 180, 100)  # Green
                    elif current_season == "summer":
                        ramp_color = (180, 140, 60)   # Brown
                    elif current_season == "autumn":
                        ramp_color = (170, 90, 40)    # Dark brown
                    else:  # winter
                        ramp_color = (200, 200, 220)  # Light gray (snow-covered)
                    
                    # Draw ramp segment
                    pygame.draw.line(
                        screen, 
                        ramp_color,
                        (ramp_x + i, SCREEN_HEIGHT - 100 - height_at_point),
                        (ramp_x + i, SCREEN_HEIGHT - 100),
                        1
                    )
                
                # Add decorative elements to ramp
                if current_season == "winter":
                    # Add snow on top
                    pygame.draw.line(
                        screen,
                        (255, 255, 255),
                        (ramp_x, SCREEN_HEIGHT - 100 - ramp_height),
                        (ramp_x + ramp_width, SCREEN_HEIGHT - 100),
                        3
                    )
                else:
                    # Add highlight on top
                    pygame.draw.line(
                        screen,
                        (255, 255, 255, 100),
                        (ramp_x, SCREEN_HEIGHT - 100 - ramp_height),
                        (ramp_x + ramp_width, SCREEN_HEIGHT - 100),
                        1
                    )
                
                # Add ramp particles for visual interest
                if random.random() > 0.9:
                    particle_x = ramp_x + random.randint(0, ramp_width)
                    particle_y = SCREEN_HEIGHT - 100 - (ramp_height * (particle_x - ramp_x) / ramp_width)
                    
                    if current_season == "spring":
                        color = (120, 200, 120)  # Bright green
                    elif current_season == "summer":
                        color = (200, 180, 100)  # Tan
                    elif current_season == "autumn":
                        color = (200, 100, 50)   # Orange
                    else:  # winter
                        color = (255, 255, 255)  # White
                        
                    self.particles.add_particle(
                        particle_x,
                        particle_y,
                        color,
                        random.uniform(1, 3),
                        random.uniform(0.5, 1.5),
                        -math.pi/2 + random.uniform(-0.3, 0.3),
                        random.randint(20, 40),
                        150
                    )
        
        # Draw finish line
        finish_x = self.finish_line_x - self.camera_offset
        if 0 <= finish_x <= SCREEN_WIDTH:
            for y in range(0, SCREEN_HEIGHT, 20):
                color = (255, 255, 255) if (y // 10) % 2 == 0 else (0, 0, 0)
                pygame.draw.rect(screen, color, (finish_x, y, 10, 10))
        
        # Draw distance markers
        for i in range(1, int(RACE_DISTANCE / 500) + 1):
            marker_x = i * 500 - self.camera_offset
            if 0 <= marker_x <= SCREEN_WIDTH:
                pygame.draw.line(screen, (200, 200, 200), (marker_x, SCREEN_HEIGHT - 300), (marker_x, SCREEN_HEIGHT))
                text = self.small_font.render(f"{i*500}m", True, (255, 255, 255))
                screen.blit(text, (marker_x - text.get_width() // 2, SCREEN_HEIGHT - 320))
        
        # Draw environment particles
        self.particles.draw(screen)
        
        # Draw cars with camera offset
        self.player.x = 100 + self.player.distance
        self.opponent.x = 100 + self.opponent.distance
        self.player.draw(screen, self.camera_offset)
        self.opponent.draw(screen, self.camera_offset)
        
        # Draw UI
        if self.game_state == "title":
            # Title screen
            title = self.font.render("PIXEL DRAG RACE", True, (255, 255, 0))
            subtitle = self.small_font.render("Press SPACE to start", True, (255, 255, 255))
            
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
            screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 160))
            
            # Instructions
            instructions = [
                "Controls:",
                "RIGHT/UP: Accelerate",
                "SPACE: Boost (when green light is on)",
                "R: Restart race"
            ]
            
            for i, line in enumerate(instructions):
                text = self.small_font.render(line, True, (200, 200, 200))
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 250 + i * 30))
        
        elif self.game_state == "ready":
            text = self.font.render("Ready?", True, (255, 255, 255))
            subtitle = self.small_font.render("Press SPACE to start countdown", True, (255, 255, 255))
            
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 100))
            screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 160))
        
        elif self.game_state == "countdown":
            text = self.font.render(str(self.countdown), True, (255, 0, 0))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 100))
        
        elif self.game_state == "racing" or self.game_state == "finished":
            # Draw speed
            speed_text = self.small_font.render(f"Speed: {int(self.player.speed * 20)} km/h", True, (255, 255, 255))
            screen.blit(speed_text, (20, 20))
            
            # Draw distance
            distance_text = self.small_font.render(f"Distance: {int(self.player.distance)} / {RACE_DISTANCE}", True, (255, 255, 255))
            screen.blit(distance_text, (20, 50))
            
            # Draw boost status
            if self.player.boost_available:
                boost_text = self.small_font.render("BOOST: READY", True, (0, 255, 0))
            elif self.player.boosting:
                boost_text = self.small_font.render("BOOST: ACTIVE", True, (255, 165, 0))
            else:
                boost_text = self.small_font.render("BOOST: CHARGING", True, (150, 150, 150))
            screen.blit(boost_text, (20, 80))
            
            # Draw current season
            progress = min(1.0, self.player.distance / RACE_DISTANCE)
            season_index = min(3, int(progress * 4))
            season_text = self.small_font.render(f"Season: {self.seasons[season_index].capitalize()}", True, (255, 255, 255))
            screen.blit(season_text, (20, 110))
            
            # Draw air status if player is in air
            if self.player.in_air:
                air_text = self.small_font.render("AIR TIME!", True, (100, 200, 255))
                screen.blit(air_text, (20, 140))
            
            # Draw race time
            if self.game_state == "racing":
                elapsed = (pygame.time.get_ticks() - self.race_start_time) / 1000
                time_text = self.small_font.render(f"Time: {elapsed:.2f}s", True, (255, 255, 255))
                screen.blit(time_text, (SCREEN_WIDTH - 150, 20))
        
        # Draw finish screen
        if self.game_state == "finished":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            player_time = (self.player.finish_time - self.race_start_time) / 1000
            opponent_time = (self.opponent.finish_time - self.race_start_time) / 1000
            
            if player_time < opponent_time:
                result = "YOU WIN!"
                color = (0, 255, 0)
            elif opponent_time < player_time:
                result = "YOU LOSE!"
                color = (255, 0, 0)
            else:
                result = "IT'S A TIE!"
                color = (255, 255, 0)
            
            result_text = self.font.render(result, True, color)
            player_time_text = self.small_font.render(f"Your Time: {player_time:.2f}s", True, (255, 255, 255))
            opponent_time_text = self.small_font.render(f"Opponent Time: {opponent_time:.2f}s", True, (255, 255, 255))
            restart_text = self.small_font.render("Press R to restart or ESC to quit", True, (200, 200, 200))
            
            screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            screen.blit(player_time_text, (SCREEN_WIDTH // 2 - player_time_text.get_width() // 2, SCREEN_HEIGHT // 2))
            screen.blit(opponent_time_text, (SCREEN_WIDTH // 2 - opponent_time_text.get_width() // 2, SCREEN_HEIGHT // 2 + 30))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 80))
    
    def reset(self):
        self.__init__()
        self.game_state = "ready"

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
                if event.key == K_ESCAPE:
                    running = False
                
                if event.key == K_SPACE:
                    if game.game_state == "title":
                        game.game_state = "ready"
                    elif game.game_state == "ready":
                        game.start_countdown()
                
                if event.key == K_r and game.game_state in ["finished", "racing"]:
                    game.reset()
        
        # Handle player input
        keys = pygame.key.get_pressed()
        if game.game_state == "racing":
            game.player.handle_input(keys)
        
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
