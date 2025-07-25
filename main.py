import pygame
import json
import random
import sys
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
CONFIG_FILE = "config.json"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
DARK_BLUE = (20, 20, 40)
LIGHT_BLUE = (0, 150, 255)

class GameConfig:
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        default_config = {
            "player_speed": 5,
            "player_lives": 3,
            "enemy_speed": 2,
            "enemy_spawn_rate": 1.0,
            "bullet_speed": 10,
            "powerup_chance": 15,
            "powerup_duration": 300
        }
        
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                # Ensure all default keys exist
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except (FileNotFoundError, json.JSONDecodeError):
            with open(CONFIG_FILE, "w") as f:
                json.dump(default_config, f, indent=4)
            return default_config
    
    def get(self, key):
        return self.config.get(key)

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.load_sounds()
    
    def load_sounds(self):
        sound_files = {
            'shoot': 'assets/shoot.wav',
            'explosion': 'assets/explosion.wav',
            'player_hit': 'assets/player_hit.wav'
        }
        
        for name, filepath in sound_files.items():
            try:
                if os.path.exists(filepath):
                    self.sounds[name] = pygame.mixer.Sound(filepath)
                else:
                    self.sounds[name] = self.create_dummy_sound()
                    print(f"Warning: {filepath} not found. Using silent mode.")
            except pygame.error as e:
                print(f"Error loading {filepath}: {e}")
                self.sounds[name] = self.create_dummy_sound()
    
    def create_dummy_sound(self):
        class DummySound:
            def play(self): pass
            def set_volume(self, volume): pass
        return DummySound()
    
    def play(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        # Draw a sleek triangular ship
        points = [(25, 0), (0, 40), (15, 30), (35, 30), (50, 40)]
        pygame.draw.polygon(self.image, LIGHT_BLUE, points)
        pygame.draw.polygon(self.image, WHITE, points, 2)
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = speed
        self.powerup_timer = 0
        self.shoot_delay = 0
        
    def update(self):
        # Handle movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        
        # Update timers
        if self.powerup_timer > 0:
            self.powerup_timer -= 1
        if self.shoot_delay > 0:
            self.shoot_delay -= 1
    
    def shoot(self, bullet_group, all_sprites, bullet_speed):
        if self.shoot_delay > 0:
            return False
            
        self.shoot_delay = 5  # Shooting cooldown
        
        if self.powerup_timer > 0:
            # Triple shot
            bullets = [
                Bullet(self.rect.centerx, self.rect.top, bullet_speed),
                Bullet(self.rect.centerx - 20, self.rect.top + 5, bullet_speed),
                Bullet(self.rect.centerx + 20, self.rect.top + 5, bullet_speed)
            ]
        else:
            # Single shot
            bullets = [Bullet(self.rect.centerx, self.rect.top, bullet_speed)]
        
        for bullet in bullets:
            bullet_group.add(bullet)
            all_sprites.add(bullet)
        
        return True
    
    def activate_powerup(self, duration):
        self.powerup_timer = duration
    
    def has_powerup(self):
        return self.powerup_timer > 0

class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        pygame.draw.rect(self.image, RED, (0, 0, 40, 30))
        pygame.draw.rect(self.image, ORANGE, (5, 5, 30, 20))
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = speed
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = speed
    
    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = []
        # Create explosion animation frames
        for size in [10, 20, 30, 25, 15, 5]:
            image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(image, ORANGE, (size, size), size)
            pygame.draw.circle(image, YELLOW, (size, size), size // 2)
            self.images.append(image)
        
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.frame = 0
        self.frame_rate = 3
        self.frame_count = 0
    
    def update(self):
        self.frame_count += 1
        if self.frame_count >= self.frame_rate:
            self.frame_count = 0
            self.frame += 1
            if self.frame >= len(self.images):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.images[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GREEN, (10, 10), 10)
        pygame.draw.circle(self.image, WHITE, (10, 10), 10, 2)
        # Draw a "P" for powerup
        font = pygame.font.Font(None, 16)
        text = font.render("P", True, WHITE)
        text_rect = text.get_rect(center=(10, 10))
        self.image.blit(text, text_rect)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 2
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Shooter")
        self.clock = pygame.time.Clock()
        self.config = GameConfig()
        self.sound_manager = SoundManager()
        
        # Game state
        self.game_state = "menu"  # menu, playing, game_over
        self.score = 0
        self.lives = 0
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        self.player = None
        self.enemy_spawn_timer = 0
    
    def new_game(self):
        # Clear all sprites
        self.all_sprites.empty()
        self.enemies.empty()
        self.bullets.empty()
        self.explosions.empty()
        self.powerups.empty()
        
        # Reset game variables
        self.score = 0
        self.lives = self.config.get("player_lives")
        self.enemy_spawn_timer = 0
        
        # Create player
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, self.config.get("player_speed"))
        self.all_sprites.add(self.player)
        
        self.game_state = "playing"
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.game_state == "menu":
                    if event.key == pygame.K_SPACE:
                        self.new_game()
                elif self.game_state == "playing":
                    if event.key == pygame.K_SPACE:
                        if self.player.shoot(self.bullets, self.all_sprites, self.config.get("bullet_speed")):
                            self.sound_manager.play('shoot')
                elif self.game_state == "game_over":
                    if event.key == pygame.K_SPACE:
                        self.game_state = "menu"
        
        return True
    
    def update(self):
        if self.game_state != "playing":
            return
        
        # Update all sprites
        self.all_sprites.update()
        
        # Spawn enemies
        spawn_rate = self.config.get("enemy_spawn_rate") + (self.score // 500) * 0.5
        self.enemy_spawn_timer += spawn_rate
        
        if self.enemy_spawn_timer >= 60:  # Spawn based on frame rate
            self.enemy_spawn_timer = 0
            enemy_speed = self.config.get("enemy_speed") + (self.score // 1000)
            enemy = Enemy(enemy_speed)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
        
        # Collision detection
        self.check_collisions()
        
        # Check game over
        if self.lives <= 0:
            self.game_state = "game_over"
    
    def check_collisions(self):
        # Bullets vs Enemies
        hits = pygame.sprite.groupcollide(self.bullets, self.enemies, True, True)
        for bullet, enemy_list in hits.items():
            for enemy in enemy_list:
                self.score += 10
                self.sound_manager.play('explosion')
                
                # Create explosion
                explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)
                self.explosions.add(explosion)
                self.all_sprites.add(explosion)
                
                # Maybe spawn powerup
                if random.randint(1, 100) <= self.config.get("powerup_chance"):
                    powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery)
                    self.powerups.add(powerup)
                    self.all_sprites.add(powerup)
        
        # Player vs Enemies
        hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
        if hits:
            self.sound_manager.play('player_hit')
            self.lives -= 1
            # Create explosion at player position
            explosion = Explosion(self.player.rect.centerx, self.player.rect.centery)
            self.explosions.add(explosion)
            self.all_sprites.add(explosion)
        
        # Player vs Powerups
        hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        if hits:
            self.player.activate_powerup(self.config.get("powerup_duration"))
    
    def draw_text(self, text, size, x, y, color=WHITE):
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)
    
    def draw(self):
        self.screen.fill(DARK_BLUE)
        
        if self.game_state == "menu":
            self.draw_text("SPACE SHOOTER", 72, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, CYAN)
            self.draw_text("Arrow Keys: Move", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            self.draw_text("Space: Shoot", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            self.draw_text("Collect green powerups for triple shot!", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            self.draw_text("Press SPACE to Start", 48, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4, GREEN)
        
        elif self.game_state == "playing":
            # Draw all sprites
            self.all_sprites.draw(self.screen)
            
            # Draw UI
            score_text = f"Score: {self.score}"
            lives_text = f"Lives: {self.lives}"
            
            text_surface = self.small_font.render(score_text, True, WHITE)
            self.screen.blit(text_surface, (10, 10))
            
            text_surface = self.small_font.render(lives_text, True, WHITE)
            self.screen.blit(text_surface, (SCREEN_WIDTH - 100, 10))
            
            # Draw powerup indicator
            if self.player and self.player.has_powerup():
                powerup_text = f"TRIPLE SHOT: {self.player.powerup_timer // 60 + 1}s"
                text_surface = self.small_font.render(powerup_text, True, GREEN)
                self.screen.blit(text_surface, (10, 40))
        
        elif self.game_state == "game_over":
            self.draw_text("GAME OVER", 72, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, RED)
            self.draw_text(f"Final Score: {self.score}", 48, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            self.draw_text("Press SPACE to return to menu", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3, GREEN)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
