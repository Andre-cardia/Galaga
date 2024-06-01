import pygame
import random
import os

# Inicializa o Pygame
pygame.init()

# Inicializa o mixer para o áudio
pygame.mixer.init()

# Configurações da tela
WIDTH, HEIGHT = 800, 600
MARGIN = 50
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaga Revive")

# Diretório base para os arquivos de mídia
base_path = os.path.dirname(__file__)
assets_path = os.path.join(base_path, 'assets')

# Carregar imagens e redimensioná-las
def load_image(filename, width, height):
    filepath = os.path.join(assets_path, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
    img = pygame.image.load(filepath)
    return pygame.transform.scale(img, (width, height))

PLAYER_IMG = load_image('fighter.png', 50, 50)
BUTTERFLY_IMG = load_image('butterfly.png', 40, 40)
BASCONIAN_IMG = load_image('basconian.png', 40, 40)
BUMBLEBEE_IMG = load_image('bumblebee.png', 40, 40)
SCORPION_IMG = load_image('scorpion.png', 40, 40)
GALAXIAN_IMG = load_image('galaxian.png', 40, 40)
GALAGA_IMG = load_image('galaga.png', 40, 40)
BULLET_IMG = load_image('bullet.png', 10, 20)

# Carregar áudio
LASER_SOUND = pygame.mixer.Sound(os.path.join(assets_path, 'laser.mp3'))
EXPLOSION_SOUND = pygame.mixer.Sound(os.path.join(assets_path, 'explosion.mp3'))
INTRO_SOUND = pygame.mixer.Sound(os.path.join(assets_path, 'intro.wav'))
END_SOUND = pygame.mixer.Sound(os.path.join(assets_path, 'end.wav'))
MUSIC_SOUND = os.path.join(assets_path, 'music.wav')

# Função para exibir texto na tela
def draw_text(surface, text, size, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

# Classe do jogador
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = PLAYER_IMG
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 50)
        self.speed = 5
        self.lives = 3

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > MARGIN:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH - MARGIN:
            self.rect.x += self.speed

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        LASER_SOUND.play()

# Classe dos inimigos
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, image, speed, bullet_group):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed
        self.bullet_group = bullet_group
        self.shoot_delay = random.randint(2000, 4000)  # Intervalo de tiro ajustado
        self.last_shot = pygame.time.get_ticks()
        self.initial_y = y
        self.moving = True

    def update(self):
        if self.moving:
            self.rect.y += self.speed
            if self.rect.y >= self.initial_y:
                self.rect.y = self.initial_y
                self.moving = False

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
            self.bullet_group.add(bullet)
            all_sprites.add(bullet)

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = BULLET_IMG
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# Classe das balas
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = BULLET_IMG
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

# Configurações gerais
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# Função para criar inimigos
def create_enemy(x, y, type, speed):
    if type == 'butterfly':
        return Enemy(x, y, BUTTERFLY_IMG, speed, enemy_bullets)
    elif type == 'basconian':
        return Enemy(x, y, BASCONIAN_IMG, speed, enemy_bullets)
    elif type == 'bumblebee':
        return Enemy(x, y, BUMBLEBEE_IMG, speed, enemy_bullets)
    elif type == 'scorpion':
        return Enemy(x, y, SCORPION_IMG, speed, enemy_bullets)
    elif type == 'galaxian':
        return Enemy(x, y, GALAXIAN_IMG, speed, enemy_bullets)
    elif type == 'galaga':
        return Enemy(x, y, GALAGA_IMG, speed, enemy_bullets)

# Função para posicionar inimigos em uma formação
def position_enemies(level):
    rows = 6
    cols = 10
    x_offset = MARGIN
    y_offset = MARGIN
    speed = level + 1
    enemy_types = ['butterfly', 'basconian', 'bumblebee', 'scorpion', 'galaxian', 'galaga']
    for row in range(rows):
        for col in range(cols):
            enemy_type = enemy_types[row % len(enemy_types)]
            enemy = create_enemy(x_offset + col * 70, y_offset + row * 50, enemy_type, speed)
            all_sprites.add(enemy)
            enemies.add(enemy)

# Inicializar formação de inimigos
level = 1
position_enemies(level)

# Função para adicionar novas naves atiradoras
def add_shooting_enemy(shooting_enemies, interval):
    if pygame.time.get_ticks() - add_shooting_enemy.last_added > interval:
        add_shooting_enemy.last_added = pygame.time.get_ticks()
        if len(shooting_enemies) < len(enemies):
            new_shooter = random.choice(list(enemies))
            while new_shooter in shooting_enemies:
                new_shooter = random.choice(list(enemies))
            shooting_enemies.add(new_shooter)
add_shooting_enemy.last_added = pygame.time.get_ticks()

shooting_enemies = set()
initial_shooting_delay = 2000  # Intervalo ajustado para adicionar novas naves atiradoras

# Função para iniciar o jogo
def start_game():
    pygame.mixer.music.load(MUSIC_SOUND)
    pygame.mixer.music.play(-1)  # Reproduzir música continuamente
    main_game_loop()

# Loop principal do jogo
def main_game_loop():
    global running
    running = True
    clock = pygame.time.Clock()

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()

        all_sprites.update()

        # Adicionar novas naves atiradoras a cada 2 segundos
        add_shooting_enemy(shooting_enemies, initial_shooting_delay)

        # Fazer com que apenas naves atiradoras disparem
        for enemy in shooting_enemies:
            enemy.shoot()

        # Colisão entre balas e inimigos
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for hit in hits:
            EXPLOSION_SOUND.play()

        if not enemies:
            level += 1
            position_enemies(level)
            shooting_enemies.clear()
            add_shooting_enemy.last_added = pygame.time.get_ticks()

        # Colisão entre balas dos inimigos e o jogador
        hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        if hits:
            player.lives -= 1
            if player.lives <= 0:
                END_SOUND.play()
                draw_text(WIN, "Finish!", 64, WIDTH // 2, HEIGHT // 2)
                pygame.display.flip()
                pygame.time.wait(3000)
                running = False  # Para simplificação, terminamos o jogo se o jogador perder todas as vidas

        WIN.fill((0, 0, 0))

        # Desenhar o número de vidas
        font = pygame.font.Font(None, 36)
        lives_text = font.render(f'Lives: {player.lives}', True, (255, 255, 255))
        WIN.blit(lives_text, (WIDTH - 120, 10))

        all_sprites.draw(WIN)
        pygame.display.flip()

    pygame.quit()

# Tocar o som de introdução e exibir o título
INTRO_SOUND.play()
WIN.fill((0, 0, 0))
draw_text(WIN, "Galaga Revive", 64, WIDTH // 2, HEIGHT // 2)
pygame.display.flip()
pygame.time.wait(5000)  # Esperar 5 segundos

# Iniciar o jogo após a introdução
start_game()
