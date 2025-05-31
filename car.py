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
        self.original_y = y  # Store original y position for landing
        
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
        
        # Jump/ramp properties
        self.in_air = False
        self.jump_height = 0
        self.jump_velocity = 0
        self.gravity = 0.5
        self.rotation = 0  # For rotation in air
        self.air_time = 0  # Track time in air for effects
        
        # Oil spill effect
        self.spinning = False
        self.spin_time = 0
        self.spin_duration = 60  # 1 second at 60 FPS
        self.spin_angle = 0
        
        # Traffic light penalty
        self.penalized = False
        self.penalty_time = 0
        self.penalty_duration = 120  # 2 seconds at 60 FPS
        
        # Particles
        self.particles = ParticleSystem()
    
    def update(self, race_active=True, ramps=None, oil_spills=None, traffic_lights=None):
        # Only update physics if race is active
        if race_active and not self.finished:
            # Handle traffic light penalty
            if self.penalized:
                self.penalty_time += 1
                # Force car to stop during penalty
                self.speed = 0
                self.acceleration = 0
                
                # Add penalty particles (red flashing)
                if self.penalty_time % 10 < 5:  # Flash every 5 frames
                    for _ in range(2):
                        self.particles.add_particle(
                            self.x + random.uniform(-20, 20),
                            self.y + random.uniform(-20, 20),
                            (255, 0, 0),
                            random.uniform(3, 6),
                            random.uniform(0.5, 1.5),
                            random.uniform(0, 2 * math.pi),
                            random.randint(10, 20),
                            150
                        )
                
                # End penalty after duration
                if self.penalty_time >= self.penalty_duration:
                    self.penalized = False
                    self.penalty_time = 0
                    
                # Don't process other physics while penalized
                return
            
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
            
            # Apply drag (less drag when in air)
            if self.in_air:
                self.speed -= (self.drag * 0.5) * self.speed
            else:
                self.speed -= self.drag * self.speed
            
            # Clamp speed
            if self.speed > self.max_speed:
                self.speed = self.max_speed
            elif self.speed < 0:
                self.speed = 0
            
            # Handle spinning from oil
            if self.spinning:
                self.spin_time += 1
                self.spin_angle += 15  # Rotate 15 degrees per frame
                
                # Slow down while spinning
                self.speed *= 0.95
                
                # Add oil particles
                if random.random() > 0.7:
                    self.particles.add_particle(
                        self.x + random.uniform(-20, 20),
                        self.y + 35,
                        (30, 30, 30),
                        random.uniform(3, 6),
                        random.uniform(0.5, 1.5),
                        random.uniform(0, 2 * math.pi),
                        random.randint(20, 40),
                        150
                    )
                
                # End spinning after duration
                if self.spin_time >= self.spin_duration:
                    self.spinning = False
                    self.spin_time = 0
                    self.spin_angle = 0
            
            # Update position
            old_distance = self.distance
            self.distance += self.speed
            
            # Check for traffic light violations
            if traffic_lights:
                for light in traffic_lights:
                    # Check if we just crossed this light
                    if old_distance < light["position"] and self.distance >= light["position"]:
                        if light["state"] == "red":
                            # Apply penalty for running a red light
                            self.penalized = True
                            self.penalty_time = 0
                            
                            # Add penalty effect particles
                            for _ in range(20):
                                self.particles.add_particle(
                                    self.x,
                                    self.y,
                                    (255, 0, 0),
                                    random.uniform(3, 8),
                                    random.uniform(1, 3),
                                    random.uniform(0, 2 * math.pi),
                                    random.randint(20, 40),
                                    200
                                )
            
            # Update boost cooldown
            if not self.boost_available and not self.boosting:
                self.boost_timer -= 1
                if self.boost_timer <= 0:
                    self.boost_available = True
            
            # Check for ramp collisions
            if ramps and not self.in_air:
                for ramp in ramps:
                    if abs(self.distance - ramp['position']) < 30:
                        self.jump_velocity = 15 + (self.speed * 0.8)  # Jump height based on speed
                        self.in_air = True
                        self.air_time = 0
                        break
            
            # Check for oil spill collisions
            if oil_spills and not self.in_air and not self.spinning:
                for spill in oil_spills:
                    if abs(self.distance - spill['position']) < 30 and self.lane == spill['lane']:
                        self.spinning = True
                        self.spin_time = 0
                        
                        # Add oil splash particles
                        for _ in range(15):
                            self.particles.add_particle(
                                self.x + random.uniform(-20, 20),
                                self.y + 35,
                                (30, 30, 30),
                                random.uniform(3, 8),
                                random.uniform(1, 3),
                                random.uniform(0, 2 * math.pi),
                                random.randint(20, 40),
                                180
                            )
                        break
            
            # Handle jumping/flying physics
            if self.in_air:
                self.air_time += 1
                self.jump_height += self.jump_velocity
                self.jump_velocity -= self.gravity
                
                # Rotate car in air
                self.rotation = min(30, self.rotation + 1) if self.jump_velocity > 0 else max(-30, self.rotation - 1)
                
                # Add air effects
                self.add_air_effects()
                
                # Check for landing
                if self.jump_height <= 0 and self.jump_velocity < 0:
                    self.in_air = False
                    self.jump_height = 0
                    self.jump_velocity = 0
                    self.rotation = 0
                    
                    # Add landing effects
                    for _ in range(10):
                        self.particles.add_smoke(
                            self.x + random.uniform(-20, 20),
                            self.original_y + 35
                        )
        
        # Update bounce animation (only when not in air)
        if not self.in_air and not self.spinning and not self.penalized:
            self.bounce_offset += self.bounce_direction * self.bounce_speed * (0.5 + self.speed / self.max_speed)
            if abs(self.bounce_offset) > self.bounce_max:
                self.bounce_direction *= -1
        
        # Update particles
        self.particles.update()
    
    def add_air_effects(self):
        """Add special effects when car is in the air"""
        # Air stream particles
        if random.random() > 0.5:
            for _ in range(3):
                self.particles.add_particle(
                    self.x + random.uniform(-30, 30),
                    self.y + random.uniform(-10, 30),
                    (200, 200, 255),
                    random.uniform(1, 3),
                    random.uniform(2, 4),
                    math.pi + random.uniform(-0.3, 0.3),
                    random.randint(10, 20),
                    150,
                    "rect" if random.random() > 0.7 else "circle"
                )
        
        # Add extra boost effects if boosting in air
        if self.boosting:
            for _ in range(5):
                self.particles.add_particle(
                    self.x + 10 + random.uniform(-10, 10),
                    self.y + 30 + random.uniform(-5, 5),
                    (255, 150, 50),
                    random.uniform(3, 8),
                    random.uniform(3, 6),
                    math.pi + random.uniform(-0.5, 0.5),
                    random.randint(15, 30),
                    200
                )
    
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
        if self.acceleration > 0.1 and self.speed < 5 and not self.in_air:
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
        
        # Calculate draw position
        draw_y = self.y + self.bounce_offset
        
        # Apply jump height if in air
        if self.in_air:
            draw_y -= self.jump_height
        
        # Create a rotated copy of the car image if in air or spinning
        if self.in_air or self.spinning:
            # Use rotation angle for air, or spin angle for spinning
            angle = self.rotation if self.in_air else self.spin_angle
            rotated_image = pygame.transform.rotate(self.image, angle)
            # Adjust position to account for rotation
            rect = rotated_image.get_rect(center=self.image.get_rect(topleft=(self.x - camera_offset, draw_y)).center)
            surface.blit(rotated_image, rect.topleft)
        else:
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
        
        # Draw air effect indicator when in air
        if self.in_air:
            # Draw air stream lines
            for i in range(3):
                start_x = self.x - camera_offset - 20 - (i * 10)
                start_y = draw_y + 20 + (i * 5) - (i * 5)
                end_x = start_x - 20
                end_y = start_y
                pygame.draw.line(surface, (200, 200, 255, 150), 
                                (start_x, start_y), (end_x, end_y), 2)
        
        # Draw spinning indicator
        if self.spinning:
            spin_text = pygame.font.SysFont(None, 24).render("SPINNING!", True, (255, 50, 50))
            surface.blit(spin_text, (self.x - camera_offset - 20, draw_y - 30))
            
        # Draw penalty indicator
        if self.penalized:
            penalty_text = pygame.font.SysFont(None, 24).render("PENALTY!", True, (255, 0, 0))
            surface.blit(penalty_text, (self.x - camera_offset - 20, draw_y - 50))
            
            # Draw red flashing rectangle around car
            if self.penalty_time % 10 < 5:  # Flash every 5 frames
                pygame.draw.rect(surface, (255, 0, 0), 
                               (self.x - camera_offset - 10, draw_y - 10, 
                                self.image.get_width() + 20, self.image.get_height() + 20), 
                               2)

class PlayerCar(Car):
    def __init__(self, x, y, image, lane, player_num=1):
        super().__init__(x, y, image, lane)
        self.player_num = player_num  # 1 or 2
    
    def handle_input(self, keys):
        # Different controls based on player number
        if self.player_num == 1:
            # Player 1 controls: Arrow keys
            if keys[pygame.K_RIGHT] or keys[pygame.K_UP]:
                self.acceleration = self.base_acceleration
                self.add_effects()
            else:
                self.acceleration = 0
            
            # Boost
            if keys[pygame.K_SPACE]:
                if self.activate_boost():
                    # Add extra boost effects
                    if self.in_air:
                        # Enhanced air boost effects
                        for _ in range(15):
                            self.particles.add_boost_trail(
                                self.x + 10 + random.uniform(-10, 10),
                                self.y + 30 + random.uniform(-5, 5)
                            )
                    else:
                        self.add_effects()
        else:
            # Player 2 controls: WASD
            if keys[pygame.K_d] or keys[pygame.K_w]:
                self.acceleration = self.base_acceleration
                self.add_effects()
            else:
                self.acceleration = 0
            
            # Boost
            if keys[pygame.K_LSHIFT]:
                if self.activate_boost():
                    # Add extra boost effects
                    if self.in_air:
                        # Enhanced air boost effects
                        for _ in range(15):
                            self.particles.add_boost_trail(
                                self.x + 10 + random.uniform(-10, 10),
                                self.y + 30 + random.uniform(-5, 5)
                            )
                    else:
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
    
    def update(self, race_active=True, ramps=None, oil_spills=None, traffic_lights=None):
        super().update(race_active, ramps, oil_spills, traffic_lights)
        
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
