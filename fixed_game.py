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
        
        # Game mode
        self.two_player_mode = False
        
        # Season tracking
        self.seasons = ["spring", "summer", "autumn", "winter"]
        self.current_season = 0
        self.season_change_distance = RACE_DISTANCE / len(self.seasons)
        
        # Create ramps
        self.ramps = [
            {"position": 1000, "height": 80},
            {"position": 2500, "height": 100},
            {"position": 4000, "height": 120},
            {"position": 5500, "height": 90}
        ]
        
        # Create oil spills
        self.oil_spills = []
        self.next_oil_spawn = 0
        self.oil_spawn_interval = 300  # Frames between oil spawn attempts
        self.max_oil_spills = 5
        
        # Create traffic lights
        self.traffic_lights = [
            {"position": 1500, "state": "green", "timer": 0, "cycle_time": 180},  # 3 seconds at 60 FPS
            {"position": 3000, "state": "green", "timer": 60, "cycle_time": 180},
            {"position": 4500, "state": "green", "timer": 120, "cycle_time": 180}
        ]
        
        # Create lanes
        self.lanes = [
            {"y": SCREEN_HEIGHT - 180},  # Player 1 lane
            {"y": SCREEN_HEIGHT - 260}   # Player 2/AI lane
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
        
        # Update traffic lights
        if self.game_state == "racing":
            for light in self.traffic_lights:
                light["timer"] += 1
                if light["timer"] >= light["cycle_time"]:
                    light["timer"] = 0
                    # Cycle through states: green -> yellow -> red -> green
                    if light["state"] == "green":
                        light["state"] = "yellow"
                    elif light["state"] == "yellow":
                        light["state"] = "red"
                    else:  # red
                        light["state"] = "green"
        
        # Update cars
        race_active = self.game_state == "racing"
        self.player.update(race_active, self.ramps, self.oil_spills, self.traffic_lights)
        self.opponent.update(race_active, self.ramps, self.oil_spills, self.traffic_lights)
        
        # Spawn oil spills randomly during race
        if race_active and len(self.oil_spills) < self.max_oil_spills:
            self.next_oil_spawn -= 1
            if self.next_oil_spawn <= 0:
                # Reset timer
                self.next_oil_spawn = self.oil_spawn_interval
                
                # Random chance to spawn oil
                if random.random() < 0.3:  # 30% chance
                    # Find a position that's not too close to existing obstacles
                    valid_position = False
                    position = 0
                    lane = 0
                    
                    for _ in range(10):  # Try 10 times to find a valid position
                        # Random position between 800 and RACE_DISTANCE - 800
                        position = random.randint(800, int(RACE_DISTANCE - 800))
                        lane = random.randint(0, 1)  # Random lane
                        
                        # Check if too close to ramps
                        too_close_to_ramp = False
                        for ramp in self.ramps:
                            if abs(position - ramp["position"]) < 300:
                                too_close_to_ramp = True
                                break
                        
                        # Check if too close to other oil spills
                        too_close_to_oil = False
                        for spill in self.oil_spills:
                            if abs(position - spill["position"]) < 500:
                                too_close_to_oil = True
                                break
                                
                        # Check if too close to traffic lights
                        too_close_to_light = False
                        for light in self.traffic_lights:
                            if abs(position - light["position"]) < 300:
                                too_close_to_light = True
                                break
                        
                        if not too_close_to_ramp and not too_close_to_oil and not too_close_to_light:
                            valid_position = True
                            break
                    
                    if valid_position:
                        self.oil_spills.append({
                            "position": position,
                            "lane": lane,
                            "time": current_time
                        })
        
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
                ramp_width = 120
                ramp_height = ramp["height"]
                
                # Calculate color based on season
                progress = min(1.0, self.player.distance / RACE_DISTANCE)
                season_index = min(3, int(progress * 4))
                current_season = self.seasons[season_index]
                
                if current_season == "spring":
                    ramp_color = (100, 180, 100)  # Green
                    outline_color = (80, 140, 80)  # Darker green
                elif current_season == "summer":
                    ramp_color = (180, 140, 60)   # Brown
                    outline_color = (140, 100, 40)  # Darker brown
                elif current_season == "autumn":
                    ramp_color = (170, 90, 40)    # Dark brown
                    outline_color = (130, 70, 30)  # Darker brown
                else:  # winter
                    ramp_color = (200, 200, 220)  # Light gray (snow-covered)
                    outline_color = (170, 170, 190)  # Darker gray
                
                # Draw filled ramp
                points = [
                    (ramp_x, SCREEN_HEIGHT - 100),  # Bottom left
                    (ramp_x + ramp_width, SCREEN_HEIGHT - 100),  # Bottom right
                    (ramp_x + ramp_width, SCREEN_HEIGHT - 100 - ramp_height//3),  # Middle right
                    (ramp_x, SCREEN_HEIGHT - 100 - ramp_height)  # Top left
                ]
                pygame.draw.polygon(screen, ramp_color, points)
                
                # Draw ramp outline
                pygame.draw.lines(screen, outline_color, False, points, 3)
                
                # Add "RAMP" text
                ramp_text = self.small_font.render("RAMP", True, (255, 255, 255))
                text_x = ramp_x + (ramp_width // 2) - (ramp_text.get_width() // 2)
                text_y = SCREEN_HEIGHT - 100 - (ramp_height // 2)
                screen.blit(ramp_text, (text_x, text_y))
                
                # Add decorative elements to ramp
                if current_season == "winter":
                    # Add snow on top
                    pygame.draw.line(
                        screen,
                        (255, 255, 255),
                        (ramp_x, SCREEN_HEIGHT - 100 - ramp_height),
                        (ramp_x + ramp_width, SCREEN_HEIGHT - 100 - ramp_height//3),
                        3
                    )
                else:
                    # Add highlight on top
                    pygame.draw.line(
                        screen,
                        (255, 255, 255),
                        (ramp_x, SCREEN_HEIGHT - 100 - ramp_height),
                        (ramp_x + ramp_width, SCREEN_HEIGHT - 100 - ramp_height//3),
                        2
                    )
                
                # Add warning stripes
                stripe_count = 5
                stripe_width = ramp_width // stripe_count
                for i in range(stripe_count):
                    if i % 2 == 0:
                        stripe_color = (255, 255, 0)  # Yellow
                    else:
                        stripe_color = (0, 0, 0)  # Black
                    
                    stripe_x = ramp_x + (i * stripe_width)
                    stripe_height = int((i / stripe_count) * ramp_height // 3)
                    
                    pygame.draw.rect(
                        screen,
                        stripe_color,
                        (stripe_x, SCREEN_HEIGHT - 105, stripe_width, 5)
                    )
                
                # Add ramp particles for visual interest
                if random.random() > 0.8:
                    particle_x = ramp_x + random.randint(0, ramp_width)
                    particle_y = SCREEN_HEIGHT - 100 - (ramp_height * (particle_x - ramp_x) / ramp_width // 2)
                    
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
            
            # Game mode indicator
            mode_text = "TWO PLAYER MODE" if self.two_player_mode else "ONE PLAYER MODE"
            mode_color = (0, 255, 255) if self.two_player_mode else (255, 255, 255)
            mode_render = self.small_font.render(mode_text, True, mode_color)
            screen.blit(mode_render, (SCREEN_WIDTH // 2 - mode_render.get_width() // 2, 200))
            
            toggle_text = self.small_font.render("Press T to toggle game mode", True, (200, 200, 200))
            screen.blit(toggle_text, (SCREEN_WIDTH // 2 - toggle_text.get_width() // 2, 230))
            
            # Instructions
            if self.two_player_mode:
                instructions = [
                    "Player 1 Controls:",
                    "RIGHT/UP: Accelerate, SPACE: Boost",
                    "Player 2 Controls:",
                    "W/D: Accelerate, LEFT SHIFT: Boost",
                    "R: Restart race"
                ]
            else:
                instructions = [
                    "Controls:",
                    "RIGHT/UP: Accelerate",
                    "SPACE: Boost (when green light is on)",
                    "R: Restart race"
                ]
            
            for i, line in enumerate(instructions):
                text = self.small_font.render(line, True, (200, 200, 200))
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 270 + i * 30))
        
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
                
            # Draw spinning status if player is spinning
            if self.player.spinning:
                spin_text = self.small_font.render("SPINNING!", True, (255, 50, 50))
                screen.blit(spin_text, (20, 170))
                
            # Draw penalty status if player is penalized
            if self.player.penalized:
                penalty_text = self.small_font.render("RED LIGHT PENALTY!", True, (255, 0, 0))
                screen.blit(penalty_text, (20, 200))
                
                # Show remaining penalty time
                remaining = (self.player.penalty_duration - self.player.penalty_time) / 60  # Convert to seconds
                time_text = self.small_font.render(f"Stop: {remaining:.1f}s", True, (255, 0, 0))
                screen.blit(time_text, (20, 230))
            
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
        # Keep the two_player_mode setting
        two_player_mode = self.two_player_mode
        self.__init__()
        self.two_player_mode = two_player_mode
        self.game_state = "ready"
        
        # If in two-player mode, replace AI with a second player
        if self.two_player_mode:
            self.opponent = PlayerCar(100, self.lanes[1]["y"], self.assets['opponent_car'], 1, player_num=2)

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
                    
                # Toggle two-player mode
                if event.key == K_t and game.game_state == "title":
                    if hasattr(game, 'toggle_two_player_mode'):
                        game.toggle_two_player_mode()
        
        # Handle player input
        keys = pygame.key.get_pressed()
        if game.game_state == "racing":
            game.player.handle_input(keys)
            
            # If in two-player mode, handle player 2 input
            if hasattr(game, 'two_player_mode') and game.two_player_mode and isinstance(game.opponent, PlayerCar):
                game.opponent.handle_input(keys)
        
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
    def toggle_two_player_mode(self):
        """Toggle between one and two player modes"""
        self.two_player_mode = not self.two_player_mode
        
        # Replace opponent with player 2 or AI based on mode
        if self.two_player_mode:
            self.opponent = PlayerCar(100, self.lanes[1]["y"], self.assets['opponent_car'], 1, player_num=2)
        else:
            self.opponent = AICar(100, self.lanes[1]["y"], self.assets['opponent_car'], 1, difficulty=1.0)
            
        return self.two_player_mode
    def draw_title_screen(self):
        """Draw the title screen with game mode options"""
        # Title
        title = self.font.render("PIXEL DRAG RACE", True, (255, 255, 0))
        subtitle = self.small_font.render("Press SPACE to start", True, (255, 255, 255))
        
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 160))
        
        # Game mode indicator
        mode_text = "TWO PLAYER MODE" if self.two_player_mode else "ONE PLAYER MODE"
        mode_color = (0, 255, 255) if self.two_player_mode else (255, 255, 255)
        mode_render = self.small_font.render(mode_text, True, mode_color)
        screen.blit(mode_render, (SCREEN_WIDTH // 2 - mode_render.get_width() // 2, 200))
        
        toggle_text = self.small_font.render("Press T to toggle game mode", True, (200, 200, 200))
        screen.blit(toggle_text, (SCREEN_WIDTH // 2 - toggle_text.get_width() // 2, 230))
        
        # Instructions
        if self.two_player_mode:
            instructions = [
                "Player 1 Controls:",
                "RIGHT/UP: Accelerate, SPACE: Boost",
                "Player 2 Controls:",
                "W/D: Accelerate, LEFT SHIFT: Boost",
                "R: Restart race"
            ]
        else:
            instructions = [
                "Controls:",
                "RIGHT/UP: Accelerate",
                "SPACE: Boost (when green light is on)",
                "R: Restart race"
            ]
        
        for i, line in enumerate(instructions):
            text = self.small_font.render(line, True, (200, 200, 200))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 270 + i * 30))
    def toggle_two_player_mode(self):
        """Toggle between one and two player modes"""
        self.two_player_mode = not self.two_player_mode
        
        # Replace opponent with player 2 or AI based on mode
        if self.two_player_mode:
            self.opponent = PlayerCar(100, self.lanes[1]["y"], self.assets['opponent_car'], 1, player_num=2)
        else:
            self.opponent = AICar(100, self.lanes[1]["y"], self.assets['opponent_car'], 1, difficulty=1.0)
            
        return self.two_player_mode
        # Draw ramps
        for ramp in self.ramps:
            ramp_x = ramp["position"] - self.camera_offset
            if 0 <= ramp_x <= SCREEN_WIDTH:
                # Draw ramp base
                ramp_width = 120
                ramp_height = ramp["height"]
                
                # Calculate color based on season
                progress = min(1.0, self.player.distance / RACE_DISTANCE)
                season_index = min(3, int(progress * 4))
                current_season = self.seasons[season_index]
                
                if current_season == "spring":
                    ramp_color = (100, 180, 100)  # Green
                    outline_color = (80, 140, 80)  # Darker green
                elif current_season == "summer":
                    ramp_color = (180, 140, 60)   # Brown
                    outline_color = (140, 100, 40)  # Darker brown
                elif current_season == "autumn":
                    ramp_color = (170, 90, 40)    # Dark brown
                    outline_color = (130, 70, 30)  # Darker brown
                else:  # winter
                    ramp_color = (200, 200, 220)  # Light gray (snow-covered)
                    outline_color = (170, 170, 190)  # Darker gray
                
                # Draw filled ramp - corrected direction
                road_y = self.lanes[0]["y"] + 35  # Position ramp at player's lane height + adjustment
                points = [
                    (ramp_x, road_y),  # Bottom left
                    (ramp_x + ramp_width, road_y),  # Bottom right
                    (ramp_x + ramp_width, road_y - ramp_height),  # Top right
                    (ramp_x + ramp_width//3, road_y - ramp_height//3)  # Top left
                ]
                pygame.draw.polygon(screen, ramp_color, points)
                
                # Draw ramp outline
                pygame.draw.lines(screen, outline_color, True, points, 3)
                
                # Add "RAMP" text
                ramp_text = self.small_font.render("RAMP", True, (255, 255, 255))
                text_x = ramp_x + (ramp_width // 2) - (ramp_text.get_width() // 2)
                text_y = road_y - (ramp_height // 2) - 10
                screen.blit(ramp_text, (text_x, text_y))
                
                # Add decorative elements to ramp
                if current_season == "winter":
                    # Add snow on top
                    pygame.draw.line(
                        screen,
                        (255, 255, 255),
                        (ramp_x + ramp_width//3, road_y - ramp_height//3),
                        (ramp_x + ramp_width, road_y - ramp_height),
                        3
                    )
                else:
                    # Add highlight on top
                    pygame.draw.line(
                        screen,
                        (255, 255, 255),
                        (ramp_x + ramp_width//3, road_y - ramp_height//3),
                        (ramp_x + ramp_width, road_y - ramp_height),
                        2
                    )
                
                # Add warning stripes
                stripe_count = 5
                stripe_width = ramp_width // stripe_count
                for i in range(stripe_count):
                    if i % 2 == 0:
                        stripe_color = (255, 255, 0)  # Yellow
                    else:
                        stripe_color = (0, 0, 0)  # Black
                    
                    stripe_x = ramp_x + (i * stripe_width)
                    
                    pygame.draw.rect(
                        screen,
                        stripe_color,
                        (stripe_x, road_y - 5, stripe_width, 5)
                    )
                
                # Add ramp particles for visual interest
                if random.random() > 0.8:
                    particle_x = ramp_x + random.randint(0, ramp_width)
                    particle_y = road_y - (ramp_height * (particle_x - ramp_x) / ramp_width // 2)
                    
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
        # Draw oil spills
        for spill in self.oil_spills:
            spill_x = spill["position"] - self.camera_offset
            if 0 <= spill_x <= SCREEN_WIDTH:
                # Determine which lane to draw in
                spill_y = self.lanes[spill["lane"]]["y"] + 35
                
                # Draw oil spill
                oil_radius = 25
                oil_color = (20, 20, 20)  # Almost black
                
                # Draw main oil puddle
                pygame.draw.ellipse(screen, oil_color, (spill_x - oil_radius, spill_y - oil_radius//2, oil_radius*2, oil_radius))
                
                # Draw oil shine
                shine_color = (40, 40, 40)  # Slightly lighter
                pygame.draw.ellipse(screen, shine_color, (spill_x - oil_radius//2, spill_y - oil_radius//4, oil_radius, oil_radius//2))
                
                # Add random oil particles
                if random.random() > 0.9:
                    self.particles.add_particle(
                        spill_x + random.uniform(-oil_radius, oil_radius),
                        spill_y + random.uniform(-oil_radius//2, oil_radius//2),
                        (30, 30, 30),
                        random.uniform(1, 3),
                        random.uniform(0.2, 0.5),
                        random.uniform(0, 2 * math.pi),
                        random.randint(10, 30),
                        150
                    )
        
        # Draw traffic lights
        for light in self.traffic_lights:
            light_x = light["position"] - self.camera_offset
            if 0 <= light_x <= SCREEN_WIDTH:
                # Draw traffic light pole
                pole_height = 150
                pole_width = 10
                pole_color = (100, 100, 100)  # Gray
                
                # Draw pole
                pygame.draw.rect(screen, pole_color, 
                               (light_x - pole_width//2, SCREEN_HEIGHT - 300, pole_width, pole_height))
                
                # Draw traffic light housing
                housing_width = 30
                housing_height = 80
                housing_color = (50, 50, 50)  # Dark gray
                
                housing_x = light_x - housing_width//2
                housing_y = SCREEN_HEIGHT - 300 - housing_height
                
                pygame.draw.rect(screen, housing_color, 
                               (housing_x, housing_y, housing_width, housing_height))
                pygame.draw.rect(screen, (30, 30, 30), 
                               (housing_x, housing_y, housing_width, housing_height), 2)
                
                # Draw lights
                light_radius = 10
                light_spacing = 25
                
                # Red light
                red_color = (255, 0, 0) if light["state"] == "red" else (100, 0, 0)
                pygame.draw.circle(screen, red_color, 
                                 (light_x, housing_y + 15), light_radius)
                
                # Yellow light
                yellow_color = (255, 255, 0) if light["state"] == "yellow" else (100, 100, 0)
                pygame.draw.circle(screen, yellow_color, 
                                 (light_x, housing_y + 40), light_radius)
                
                # Green light
                green_color = (0, 255, 0) if light["state"] == "green" else (0, 100, 0)
                pygame.draw.circle(screen, green_color, 
                                 (light_x, housing_y + 65), light_radius)
                
                # Add light glow effect
                if light["state"] == "red":
                    glow_color = (255, 100, 100, 100)
                    glow_pos = (light_x, housing_y + 15)
                elif light["state"] == "yellow":
                    glow_color = (255, 255, 100, 100)
                    glow_pos = (light_x, housing_y + 40)
                else:  # green
                    glow_color = (100, 255, 100, 100)
                    glow_pos = (light_x, housing_y + 65)
                
                # Create glow surface
                glow_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, glow_color, (20, 20), 15)
                screen.blit(glow_surface, (glow_pos[0] - 20, glow_pos[1] - 20))
    def toggle_two_player_mode(self):
        """Toggle between one and two player modes"""
        self.two_player_mode = not self.two_player_mode
        
        # Replace opponent with player 2 or AI based on mode
        if self.two_player_mode:
            self.opponent = PlayerCar(100, self.lanes[1]["y"], self.assets['opponent_car'], 1, player_num=2)
        else:
            self.opponent = AICar(100, self.lanes[1]["y"], self.assets['opponent_car'], 1, difficulty=1.0)
            
        return self.two_player_mode
        # Draw traffic lights
        for light in self.traffic_lights:
            light_x = light["position"] - self.camera_offset
            if 0 <= light_x <= SCREEN_WIDTH:
                # Draw traffic light pole
                pole_height = 150
                pole_width = 10
                pole_color = (100, 100, 100)  # Gray
                
                # Draw pole
                pygame.draw.rect(screen, pole_color, 
                               (light_x - pole_width//2, SCREEN_HEIGHT - 300, pole_width, pole_height))
                
                # Draw traffic light housing
                housing_width = 30
                housing_height = 80
                housing_color = (50, 50, 50)  # Dark gray
                
                housing_x = light_x - housing_width//2
                housing_y = SCREEN_HEIGHT - 300 - housing_height
                
                pygame.draw.rect(screen, housing_color, 
                               (housing_x, housing_y, housing_width, housing_height))
                pygame.draw.rect(screen, (30, 30, 30), 
                               (housing_x, housing_y, housing_width, housing_height), 2)
                
                # Draw lights
                light_radius = 10
                light_spacing = 25
                
                # Red light
                red_color = (255, 0, 0) if light["state"] == "red" else (100, 0, 0)
                pygame.draw.circle(screen, red_color, 
                                 (light_x, housing_y + 15), light_radius)
                
                # Yellow light
                yellow_color = (255, 255, 0) if light["state"] == "yellow" else (100, 100, 0)
                pygame.draw.circle(screen, yellow_color, 
                                 (light_x, housing_y + 40), light_radius)
                
                # Green light
                green_color = (0, 255, 0) if light["state"] == "green" else (0, 100, 0)
                pygame.draw.circle(screen, green_color, 
                                 (light_x, housing_y + 65), light_radius)
                
                # Add light glow effect
                if light["state"] == "red":
                    glow_color = (255, 100, 100, 100)
                    glow_pos = (light_x, housing_y + 15)
                elif light["state"] == "yellow":
                    glow_color = (255, 255, 100, 100)
                    glow_pos = (light_x, housing_y + 40)
                else:  # green
                    glow_color = (100, 255, 100, 100)
                    glow_pos = (light_x, housing_y + 65)
                
                # Create glow surface
                glow_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, glow_color, (20, 20), 15)
                screen.blit(glow_surface, (glow_pos[0] - 20, glow_pos[1] - 20))
        # Draw oil spills
        for spill in self.oil_spills:
            spill_x = spill["position"] - self.camera_offset
            if 0 <= spill_x <= SCREEN_WIDTH:
                # Determine which lane to draw in
                spill_y = self.lanes[spill["lane"]]["y"] + 35
                
                # Draw oil spill
                oil_radius = 25
                oil_color = (20, 20, 20)  # Almost black
                
                # Draw main oil puddle
                pygame.draw.ellipse(screen, oil_color, (spill_x - oil_radius, spill_y - oil_radius//2, oil_radius*2, oil_radius))
                
                # Draw oil shine
                shine_color = (40, 40, 40)  # Slightly lighter
                pygame.draw.ellipse(screen, shine_color, (spill_x - oil_radius//2, spill_y - oil_radius//4, oil_radius, oil_radius//2))
                
                # Add random oil particles
                if random.random() > 0.9:
                    self.particles.add_particle(
                        spill_x + random.uniform(-oil_radius, oil_radius),
                        spill_y + random.uniform(-oil_radius//2, oil_radius//2),
                        (30, 30, 30),
                        random.uniform(1, 3),
                        random.uniform(0.2, 0.5),
                        random.uniform(0, 2 * math.pi),
                        random.randint(10, 30),
                        150
                    )
