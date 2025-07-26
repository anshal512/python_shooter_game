import pygame
import math
import random
import time

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 128, 0)
BROWN = (139, 69, 19)

class Tank:
    def __init__(self, x, y, color, is_player=False):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 3 if is_player else 2
        self.max_health = 100
        self.health = self.max_health
        self.color = color
        self.size = 25
        self.is_player = is_player
        self.last_shot = 0
        self.shot_delay = 300 if is_player else 800
        self.bullets = []
        
        # Power-up effects
        self.speed_boost_end = 0
        self.rapid_fire_end = 0
        
    def update(self):
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.x < 0 or bullet.x > SCREEN_WIDTH or bullet.y < 0 or bullet.y > SCREEN_HEIGHT:
                self.bullets.remove(bullet)
        
        # Reset power-ups when they expire
        current_time = pygame.time.get_ticks()
        if current_time > self.speed_boost_end:
            self.speed = 3 if self.is_player else 2
        if current_time > self.rapid_fire_end:
            self.shot_delay = 300 if self.is_player else 800
    
    def move(self, dx, dy):
        # Keep tank within screen bounds
        new_x = max(self.size, min(SCREEN_WIDTH - self.size, self.x + dx * self.speed))
        new_y = max(self.size, min(SCREEN_HEIGHT - self.size, self.y + dy * self.speed))
        self.x = new_x
        self.y = new_y
    
    def aim_at(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        self.angle = math.atan2(dy, dx)
    
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shot_delay:
            bullet = Bullet(self.x, self.y, self.angle, self.color)
            self.bullets.append(bullet)
            self.last_shot = current_time
            return True
        return False
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0
    
    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
    
    def apply_speed_boost(self, duration=5000):
        self.speed = 5
        self.speed_boost_end = pygame.time.get_ticks() + duration
    
    def apply_rapid_fire(self, duration=5000):
        self.shot_delay = 100
        self.rapid_fire_end = pygame.time.get_ticks() + duration
    
    def draw(self, screen):
        # Draw tank body
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.size, 2)
        
        # Draw tank cannon
        cannon_length = self.size + 10
        end_x = self.x + math.cos(self.angle) * cannon_length
        end_y = self.y + math.sin(self.angle) * cannon_length
        pygame.draw.line(screen, BLACK, (self.x, self.y), (end_x, end_y), 5)
        
        # Draw health bar for player
        if self.is_player:
            bar_width = 50
            bar_height = 8
            bar_x = self.x - bar_width // 2
            bar_y = self.y - self.size - 15
            
            # Background
            pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
            # Health
            health_width = int((self.health / self.max_health) * bar_width)
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(screen)

class EnemyTank(Tank):
    def __init__(self, x, y, tank_type="basic"):
        colors = {"basic": RED, "fast": ORANGE, "heavy": BROWN}
        super().__init__(x, y, colors.get(tank_type, RED), False)
        
        self.tank_type = tank_type
        self.target = None
        self.last_direction_change = 0
        self.direction_x = random.choice([-1, 0, 1])
        self.direction_y = random.choice([-1, 0, 1])
        
        # Adjust stats based on type
        if tank_type == "fast":
            self.speed = 4
            self.shot_delay = 600
            self.size = 20
            self.health = 60
            self.max_health = 60
        elif tank_type == "heavy":
            self.speed = 1.5
            self.shot_delay = 1200
            self.size = 35
            self.health = 200
            self.max_health = 200
    
    def ai_update(self, player_tank):
        current_time = pygame.time.get_ticks()
        
        # Change direction randomly
        if current_time - self.last_direction_change > random.randint(1000, 3000):
            self.direction_x = random.choice([-1, 0, 1])
            self.direction_y = random.choice([-1, 0, 1])
            self.last_direction_change = current_time
        
        # Move
        self.move(self.direction_x, self.direction_y)
        
        # Aim at player
        self.aim_at(player_tank.x, player_tank.y)
        
        # Shoot at player if in range
        distance = math.sqrt((self.x - player_tank.x)**2 + (self.y - player_tank.y)**2)
        if distance < 300:
            self.shoot()

class Bullet:
    def __init__(self, x, y, angle, color):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 8
        self.color = color
        self.size = 4
        
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.power_type = power_type  # "health", "speed", "rapid_fire"
        self.size = 15
        self.spawn_time = pygame.time.get_ticks()
        self.duration = 15000  # 15 seconds before disappearing
        
        colors = {
            "health": GREEN,
            "speed": BLUE,
            "rapid_fire": YELLOW
        }
        self.color = colors.get(power_type, WHITE)
    
    def update(self):
        # Remove if expired
        return pygame.time.get_ticks() - self.spawn_time < self.duration
    
    def draw(self, screen):
        # Draw pulsing effect
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 5 + 10
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(pulse))
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), int(pulse), 2)
        
        # Draw symbol
        if self.power_type == "health":
            # Draw cross
            pygame.draw.rect(screen, WHITE, (self.x-8, self.y-2, 16, 4))
            pygame.draw.rect(screen, WHITE, (self.x-2, self.y-8, 4, 16))
        elif self.power_type == "speed":
            # Draw arrow
            points = [(self.x+8, self.y), (self.x-4, self.y-6), (self.x-4, self.y+6)]
            pygame.draw.polygon(screen, WHITE, points)
        elif self.power_type == "rapid_fire":
            # Draw bullets
            for i in range(3):
                pygame.draw.circle(screen, WHITE, (int(self.x-4+i*4), int(self.y)), 2)

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.start_time = pygame.time.get_ticks()
        self.duration = 500
        
    def update(self):
        return pygame.time.get_ticks() - self.start_time < self.duration
    
    def draw(self, screen):
        elapsed = pygame.time.get_ticks() - self.start_time
        progress = elapsed / self.duration
        
        if progress < 1:
            size = int(30 * (1 - progress))
            alpha = int(255 * (1 - progress))
            
            # Create multiple circles for explosion effect
            for i in range(3):
                color_intensity = max(0, 255 - i * 85)
                color = (color_intensity, color_intensity // 2, 0)  # Orange to red
                radius = size - i * 5
                if radius > 0:
                    pygame.draw.circle(screen, color, (int(self.x), int(self.y)), radius)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tank Battle Arena")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.reset_game()
        
    def reset_game(self):
        self.player = Tank(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, DARK_GREEN, True)
        self.enemies = []
        self.power_ups = []
        self.explosions = []
        self.score = 0
        self.level = 1
        self.enemies_killed = 0
        self.game_over = False
        self.victory = False
        self.last_power_up_spawn = 0
        
        self.spawn_enemies()
    
    def spawn_enemies(self):
        self.enemies.clear()
        enemy_count = 2 + self.level
        
        for _ in range(enemy_count):
            # Spawn enemies away from player
            while True:
                x = random.randint(50, SCREEN_WIDTH - 50)
                y = random.randint(50, SCREEN_HEIGHT - 50)
                distance = math.sqrt((x - self.player.x)**2 + (y - self.player.y)**2)
                if distance > 200:  # Minimum distance from player
                    break
            
            # Choose enemy type based on level
            if self.level >= 3 and random.random() < 0.3:
                enemy_type = "heavy"
            elif self.level >= 2 and random.random() < 0.4:
                enemy_type = "fast"
            else:
                enemy_type = "basic"
                
            enemy = EnemyTank(x, y, enemy_type)
            self.enemies.append(enemy)
    
    def spawn_power_up(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_power_up_spawn > 10000:  # Every 10 seconds
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            power_type = random.choice(["health", "speed", "rapid_fire"])
            self.power_ups.append(PowerUp(x, y, power_type))
            self.last_power_up_spawn = current_time
    
    def check_collisions(self):
        # Player bullets vs enemies
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies[:]:
                distance = math.sqrt((bullet.x - enemy.x)**2 + (bullet.y - enemy.y)**2)
                if distance < enemy.size:
                    self.player.bullets.remove(bullet)
                    if enemy.take_damage(50):
                        self.enemies.remove(enemy)
                        self.explosions.append(Explosion(enemy.x, enemy.y))
                        self.enemies_killed += 1
                        
                        # Score based on enemy type
                        if enemy.tank_type == "heavy":
                            self.score += 200
                        elif enemy.tank_type == "fast":
                            self.score += 150
                        else:
                            self.score += 100
                    break
        
        # Enemy bullets vs player
        for enemy in self.enemies:
            for bullet in enemy.bullets[:]:
                distance = math.sqrt((bullet.x - self.player.x)**2 + (bullet.y - self.player.y)**2)
                if distance < self.player.size:
                    enemy.bullets.remove(bullet)
                    if self.player.take_damage(25):
                        self.game_over = True
                    break
        
        # Player vs power-ups
        for power_up in self.power_ups[:]:
            distance = math.sqrt((power_up.x - self.player.x)**2 + (power_up.y - self.player.y)**2)
            if distance < self.player.size + power_up.size:
                self.power_ups.remove(power_up)
                
                if power_up.power_type == "health":
                    self.player.heal(50)
                elif power_up.power_type == "speed":
                    self.player.apply_speed_boost()
                elif power_up.power_type == "rapid_fire":
                    self.player.apply_rapid_fire()
                
                self.score += 50
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Movement
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1
        
        if dx != 0 or dy != 0:
            self.player.move(dx, dy)
        
        # Aiming
        self.player.aim_at(mouse_x, mouse_y)
        
        # Shooting
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0]:  # Left click
            self.player.shoot()
    
    def update(self):
        if self.game_over or self.victory:
            return
        
        # Update player
        self.player.update()
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update()
            enemy.ai_update(self.player)
        
        # Update power-ups
        self.power_ups = [pu for pu in self.power_ups if pu.update()]
        
        # Update explosions
        self.explosions = [exp for exp in self.explosions if exp.update()]
        
        # Check collisions
        self.check_collisions()
        
        # Spawn power-ups
        self.spawn_power_up()
        
        # Check level completion
        if len(self.enemies) == 0:
            self.level += 1
            if self.level > 10:
                self.victory = True
            else:
                self.spawn_enemies()
                self.player.heal(25)  # Small heal between levels
    
    def draw_ui(self):
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Level
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (10, 50))
        
        # Health
        health_text = self.font.render(f"Health: {self.player.health}/{self.player.max_health}", True, WHITE)
        self.screen.blit(health_text, (10, 90))
        
        # Enemies remaining
        enemies_text = self.font.render(f"Enemies: {len(self.enemies)}", True, WHITE)
        self.screen.blit(enemies_text, (10, 130))
        
        # Power-up indicators
        y_offset = 170
        current_time = pygame.time.get_ticks()
        
        if current_time < self.player.speed_boost_end:
            boost_text = self.small_font.render("SPEED BOOST", True, BLUE)
            self.screen.blit(boost_text, (10, y_offset))
            y_offset += 25
            
        if current_time < self.player.rapid_fire_end:
            rapid_text = self.small_font.render("RAPID FIRE", True, YELLOW)
            self.screen.blit(rapid_text, (10, y_offset))
        
        # Instructions
        if self.level == 1 and len(self.enemies) > 0:
            inst_text = self.small_font.render("WASD: Move | Mouse: Aim & Shoot", True, WHITE)
            self.screen.blit(inst_text, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 30))
    
    def draw(self):
        self.screen.fill(GRAY)
        
        # Draw game objects
        self.player.draw(self.screen)
        
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        for power_up in self.power_ups:
            power_up.draw(self.screen)
        
        for explosion in self.explosions:
            explosion.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        
        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill(BLACK)
            overlay.set_alpha(128)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("GAME OVER", True, RED)
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.small_font.render("Press R to Restart or Q to Quit", True, WHITE)
            
            self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(score_text, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2))
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - 140, SCREEN_HEIGHT//2 + 50))
        
        # Victory screen
        if self.victory:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill(BLACK)
            overlay.set_alpha(128)
            self.screen.blit(overlay, (0, 0))
            
            victory_text = self.font.render("VICTORY!", True, YELLOW)
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.small_font.render("Press R to Restart or Q to Quit", True, WHITE)
            
            self.screen.blit(victory_text, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(score_text, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2))
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - 140, SCREEN_HEIGHT//2 + 50))
    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_r and (self.game_over or self.victory):
                        self.reset_game()
            
            if not (self.game_over or self.victory):
                self.handle_input()
            
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run() 