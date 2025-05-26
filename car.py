import pygame
import random
import math
from particles import ParticleSystem

class Car:
    def __init__(self, x, y, image, lane):
        self.x = x
        self.y = y
        self.image = image
        self.lane = lane  # Track which lane the car is in
        
        # Physics properties
        self.speed = 0
        self.max_speed = 15
        self.acceleration = 0
        self.base_acceleration = 0.2
        self.drag = 0.05
        
        # Race properties
        self.distance = 0
        self.finished = False
        self.start_time = 0
        self.finish_time = 0
        
        # Animation properties
        self.bounce_offset = 0
        self.bounce_direction = 1
        self.bounce_speed = 0.2
        self.bounce_max = 2
        
        # Special effects
        self.boost_available = True
        self.boosting = False
        self.boost_time = 0
        self.boost_duration = 60  # frames
        self.boost_cooldown = 180  # frames
        self.boost_timer = 0
        
        # Particles
        self.particles = ParticleSystem()
    
    def update(self, race_active=True):
        # Only update physics if race is active
        if race_active and not self.finished:
            # Apply acceleration and drag
            if self.boosting:
                self.speed += self.base_acceleration * 2
                self.boost_time -= 1
                if self.boost_time <= 0:
                    self.boosting = False
                    self.boost_available = False
                    self.boost_timer = self.boost_cooldown
            else:
                self.speed += self.acceleration
            
            # Apply drag
            self.speed -= self.drag * self.speed
            
            # Clamp speed
            if self.speed > self.max_speed:
                self.speed = self.max_speed
            elif self.speed < 0:
                self.speed = 0
            
            # Update position
            self.distance += self.speed
            
            # Update boost cooldown
            if not self.boost_available and not self.boosting:
                self.boost_timer -= 1
                if self.boost_timer <= 0:
                    self.boost_available = True
        
        # Update bounce animation (always active for visual interest)
        self.bounce_offset += self.bounce_direction * self.bounce_speed * (0.5 + self.speed / self.max_speed)
        if abs(self.bounce_offset) > self.bounce_max:
            self.bounce_direction *= -1
        
        # Update particles
        self.particles.update()
    
    def activate_boost(self):
        if self.boost_available and not self.boosting:
            self.boosting = True
            self.boost_time = self.boost_duration
            self.boost_available = False
            
            # Add boost particles
            for _ in range(20):
                self.particles.add_sparks(self.x + 10, self.y + 30, 20)
            
            return True
        return False
    
    def add_effects(self):
        # Add exhaust flames based on speed
        if self.speed > 0:
            intensity = int(self.speed / 2) + 1
            for _ in range(intensity):
                self.particles.add_flame(
                    self.x + 10, 
                    self.y + 30 + random.uniform(-3, 3)
                )
        
        # Add tire smoke when accelerating hard
        if self.acceleration > 0.1 and self.speed < 5:
            for _ in range(2):
                self.particles.add_smoke(
                    self.x + 20 + random.uniform(-5, 5),
                    self.y + 35
                )
        
        # Add boost effects
        if self.boosting:
            for _ in range(3):
                self.particles.add_sparks(
                    self.x + 10 + random.uniform(-5, 5),
                    self.y + 30 + random.uniform(-3, 3),
                    3
                )
    
    def draw(self, surface, camera_offset=0):
        # Draw particles first (behind car)
        self.particles.draw(surface)
        
        # Draw car with bounce effect
        draw_y = self.y + self.bounce_offset
        surface.blit(self.image, (self.x - camera_offset, draw_y))
        
        # Draw boost indicator
        if self.boost_available:
            pygame.draw.circle(surface, (0, 255, 0), (int(self.x - camera_offset + 70), int(draw_y + 10)), 5)
        elif self.boosting:
            pygame.draw.circle(surface, (255, 165, 0), (int(self.x - camera_offset + 70), int(draw_y + 10)), 5)
        else:
            cooldown_percent = 1 - (self.boost_timer / self.boost_cooldown)
            if cooldown_percent > 0.5:
                color = (255, 255, 0)  # Yellow when more than half ready
            else:
                color = (150, 150, 150)  # Gray when less than half ready
            pygame.draw.circle(surface, color, (int(self.x - camera_offset + 70), int(draw_y + 10)), 5)

class PlayerCar(Car):
    def __init__(self, x, y, image, lane):
        super().__init__(x, y, image, lane)
    
    def handle_input(self, keys):
        # Acceleration
        if keys[pygame.K_RIGHT] or keys[pygame.K_UP]:
            self.acceleration = self.base_acceleration
            self.add_effects()
        else:
            self.acceleration = 0
        
        # Boost
        if keys[pygame.K_SPACE]:
            if self.activate_boost():
                # Add extra boost effects
                self.add_effects()

class AICar(Car):
    def __init__(self, x, y, image, lane, difficulty=1.0):
        super().__init__(x, y, image, lane)
        
        # AI properties
        self.difficulty = difficulty  # 0.0 to 2.0, with 1.0 being "normal"
        self.reaction_time = random.uniform(30, 60) / difficulty  # Frames before AI starts
        self.reaction_timer = self.reaction_time
        self.decision_timer = 0
        self.decision_interval = random.randint(30, 90)  # How often AI makes decisions
        
        # Adjust car properties based on difficulty
        self.base_acceleration *= difficulty
        self.drag *= (2 - difficulty) * 0.8  # Lower drag for higher difficulty
    
    def update(self, race_active=True):
        super().update(race_active)
        
        if race_active and not self.finished:
            # Handle AI reaction time at start
            if self.reaction_timer > 0:
                self.reaction_timer -= 1
                self.acceleration = 0
            else:
                # Basic AI: accelerate most of the time
                self.acceleration = self.base_acceleration * random.uniform(0.8, 1.0)
                self.add_effects()
                
                # Occasionally use boost
                self.decision_timer += 1
                if self.decision_timer >= self.decision_interval:
                    self.decision_timer = 0
                    self.decision_interval = random.randint(30, 90)
                    
                    # Higher chance to boost with higher difficulty
                    if random.random() < 0.3 * self.difficulty:
                        if self.activate_boost():
                            self.add_effects()
