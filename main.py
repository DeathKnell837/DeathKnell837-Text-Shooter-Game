import pygame
import json
import random
import sys

CONFIG_FILE = "config.json"

# --- Load Configuration ---
def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Create a default config if it doesn't exist
        default_config = {
            "player_speed": 5,
            "player_lives": 3,
            "enemy_speed": 2,
            "enemy_spawn_rate": 1, # Per second
            "bullet_speed": 10,
            "powerup_chance": 15 # Percentage
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_config, f, indent=4)
        return default_config

# --- Game Classes ---
class Player(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        # Draw a triangle for the player ship
        pygame.draw.polygon(self.image, (0, 150, 255), [(0, 40), (25, 0), (50, 40)])
        self.rect = self.image.get_rect(center=(400, 550))
        self.speed = speed
        self.powerup_timer = 0

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < 800:
            self.rect.x += self.speed
        
        if self.powerup_timer > 0:
            self.powerup_timer -= 1

    def shoot(self, bullet_speed, all_sprites, bullets):
        if self.powerup_timer > 0:
            # Triple shot power-up
            all_sprites.add(Bullet(self.rect.centerx, self.rect.top, bullet_speed))
            all_sprites.add(Bullet(self.rect.left, self.rect.centery, bullet_speed))
            all_sprites.add(Bullet(self.rect.right, self.rect.centery, bullet_speed))
            bullets.add(all_sprites.sprites()[-3:]) # Add all three
        else:
            bullet = Bullet(self.rect.centerx, self.rect.top, bullet_speed)
            all_sprites.add(bullet)
            bullets.add(bullet)

    def activate_powerup(self):
        self.powerup_timer = 300 # 5 seconds at 60fps

class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(
            center=(random.randint(20, 780), random.randint(-100, -40))
        )
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 600:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 165, 0), (15, 15), 15)
        self.rect = self.image.get_rect(center=center)
        self.lifetime = 10 # Animation duration

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 255, 0), (12, 12), 12)
        self.rect = self.image.get_rect(center=center)

    def update(self):
        self.rect.y += 2
        if self.rect.top > 600:
            self.kill()

# --- UI & Screens ---
def draw_text(surface, text, size, x, y, color=(255, 255, 255)):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

def show_menu_screen(screen, screen_width, screen_height):
    screen.fill((20, 20, 40))
    draw_text(screen, "GRAPHICAL SHOOTER", 64, screen_width / 2, screen_height / 4)
    draw_text(screen, "Arrow keys to move, Space to shoot", 22, screen_width / 2, screen_height / 2)
    draw_text(screen, "Press any key to begin", 18, screen_width / 2, screen_height * 0.75)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                waiting = False

# --- Main Game Function ---
def main():
    config = load_config()
    pygame.init()
    pygame.mixer.init()

    # Load sounds (placeholders)
    try:
        shoot_sound = pygame.mixer.Sound("assets/shoot.wav")
        explosion_sound = pygame.mixer.Sound("assets/explosion.wav")
        player_hit_sound = pygame.mixer.Sound("assets/player_hit.wav")
    except pygame.error:
        print("Warning: Sound files not found in 'assets/'. Game will be silent.")
        # Create dummy sound objects
        class DummySound: def play(self): pass
        shoot_sound = explosion_sound = player_hit_sound = DummySound()

    # Screen setup
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Graphical Shooter")
    clock = pygame.time.Clock()

    game_over = True
    running = True
    while running:
        if game_over:
            show_menu_screen(screen, screen_width, screen_height)
            game_over = False
            # Game variables
            score = 0
            lives = config["player_lives"]
            # Sprite Groups
            all_sprites = pygame.sprite.Group()
            enemies = pygame.sprite.Group()
            bullets = pygame.sprite.Group()
            powerups = pygame.sprite.Group()
            player = Player(config["player_speed"])
            all_sprites.add(player)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot(config["bullet_speed"], all_sprites, bullets)
                    shoot_sound.play()
        
        # Dynamic difficulty
        spawn_rate = config["enemy_spawn_rate"] + (score // 100)
        if random.randint(0, int(60 / spawn_rate)) == 0:
            enemy = Enemy(config["enemy_speed"] + (score // 200))
            all_sprites.add(enemy)
            enemies.add(enemy)

        # Update
        keys = pygame.key.get_pressed()
        all_sprites.update()
        player.update(keys)

        # Collision: Bullets and Enemies
        hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
        for hit_enemy in hits.values():
            score += 10
            explosion_sound.play()
            all_sprites.add(Explosion(hit_enemy[0].rect.center))
            if random.randint(1, 100) <= config["powerup_chance"]:
                powerup = PowerUp(hit_enemy[0].rect.center)
                all_sprites.add(powerup)
                powerups.add(powerup)

        # Collision: Player and Enemies
        player_hits = pygame.sprite.spritecollide(player, enemies, True)
        if player_hits:
            player_hit_sound.play()
            lives -= 1
            if lives <= 0:
                game_over = True

        # Collision: Player and Powerups
        powerup_hits = pygame.sprite.spritecollide(player, powerups, True)
        if powerup_hits:
            player.activate_powerup()

        # Draw / Render
        screen.fill((20, 20, 40))
        all_sprites.draw(screen)
        draw_text(screen, f"Score: {score}", 24, 50, 20)
        draw_text(screen, f"Lives: {lives}", 24, screen_width - 50, 20)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
