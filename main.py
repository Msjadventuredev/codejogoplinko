import pygame
import pymunk
import random
import sys

# Configurações do jogo
WIDTH = 800
HEIGHT = 820
FPS = 60
BG_COLOR = (16, 32, 45)
BALL_RADIUS = 16
OBSTACLE_RADIUS = 10
MULTIPLIERS = [25, 20, 15, 10, 5, 10, 15, 20, 25]
PIN_RESET_TIME = 0.5
IMPULSE_FORCE = 20

# Cores personalizadas
MULTIPLIER_COLOR = (255, 174, 81)  # Cor de fundo #FFAE51

# Inicialização do Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Plinko")
clock = pygame.time.Clock()

# Inicialização do Pymunk
space = pymunk.Space()
space.gravity = (0, 1200)

# Função para criar os obstáculos
def create_obstacles():
    obstacles = []

    base_obstacles = 10
    top_obstacles = 8

    # Ajuste o posicionamento centralizado dos obstáculos e faça-os subir mais na tela
    spacing_x = WIDTH // (base_obstacles + 1)
    y_offset = 80  # Valor ajustável para mover os obstáculos para cima

    for i in range(top_obstacles):
        for j in range(base_obstacles - i):
            x = (j + 0.5) * spacing_x + (i + 1) * spacing_x / 2
            y = (HEIGHT - 50) - i * 50 - y_offset

            moment = pymunk.moment_for_circle(1, 0, OBSTACLE_RADIUS)
            body = pymunk.Body(1, moment, pymunk.Body.KINEMATIC)
            body.position = x, y
            shape = pymunk.Circle(body, OBSTACLE_RADIUS)
            space.add(body, shape)

            obstacle = Obstacle(x, y, shape)
            obstacles.append(obstacle)

    return obstacles

# Classe da bola
class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface(
            (BALL_RADIUS * 2, BALL_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 0, 0),
                           (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = 1  # Defina a posição Y inicial desejada
        self.speed_x = 0  # Velocidade horizontal definida como 0
        self.speed_y = 0

        moment = pymunk.moment_for_circle(1, 0, BALL_RADIUS)
        self.body = pymunk.Body(1, moment)
        self.body.position = x, 280  # Defina a posição Y inicial desejada
        self.shape = pymunk.Circle(self.body, BALL_RADIUS)
        self.shape.elasticity = 0.3
        space.add(self.body, self.shape)

    def update(self):
        self.rect.center = self.body.position
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.speed_x *= -1

# Classe do multiplicador
class Multiplier(pygame.sprite.Sprite):
    def __init__(self, x_offset, value):
        super().__init__()

        # Tamanho do retângulo
        self.width = 60
        self.height = 40

        # Cores
        self.bg_color = MULTIPLIER_COLOR
        self.text_color = (20, 20, 20)  # Cor do texto #141414

        # Superfície para desenhar o retângulo
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Desenhar o retângulo arredondado
        border_radius = 15
        rect_rect = pygame.Rect(0, 0, self.width, self.height)
        pygame.draw.rect(self.image, self.bg_color, rect_rect,
                         border_radius=border_radius)

        # Carregue a fonte Arial (substitua o caminho pelo caminho real da fonte)
        font_path = r"C:\Users\msjma\OneDrive\Documentos\Projeto Plinko para Tiktok\Teste\Fonte\arialbd.ttf"
        font_size = 24  # Tamanho da fonte
        font = pygame.font.Font(font_path, font_size)

        # Renderize o número usando a fonte
        text_surface = font.render(str(value), True, self.text_color)

        # Posicione o número no centro do retângulo
        text_rect = text_surface.get_rect(
            center=(self.width // 2, self.height // 2))

        # Cole o número na superfície
        self.image.blit(text_surface, text_rect)

        # Retângulo de colisão
        self.rect = self.image.get_rect()
        self.rect.centerx = x_offset  # Use o deslocamento horizontal
        self.rect.centery = HEIGHT - 75
        self.value = value

        # Variáveis de animação
        self.animation_speed = 40  # Velocidade de animação
        self.animation_distance = 4  # Distância a ser deslocada durante a animação
        self.is_animating = True  # Flag para indicar se a animação está em andamento
        self.animation_start_time = 0  # Hora de início da animação
        self.original_y = HEIGHT - 75  # Posição original no eixo Y

    def update(self):
        if self.is_animating:
            # Calcular o deslocamento da animação com base no tempo
            elapsed_time = pygame.time.get_ticks() - self.animation_start_time
            animation_offset = self.animation_speed * elapsed_time / 1000

            # Limitar o deslocamento para a distância de animação definida
            if animation_offset >= self.animation_distance:
                animation_offset = self.animation_distance
                self.is_animating = False

            # Atualizar a posição do retângulo de colisão
            self.rect.centery = self.original_y + animation_offset

    def check_collision(self, balls):
        hits = pygame.sprite.spritecollide(self, balls, True)
        if hits:
            # Iniciar a animação quando uma colisão ocorrer
            self.is_animating = True
            self.animation_start_time = pygame.time.get_ticks()

# Classe do obstáculo
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, shape):
        super().__init__()
        self.image = pygame.Surface(
            (OBSTACLE_RADIUS * 2, OBSTACLE_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 255),
                           (OBSTACLE_RADIUS, OBSTACLE_RADIUS), OBSTACLE_RADIUS)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.shape = shape

# Reduza o número abaixo para ajustar o espaçamento entre os multiplicadores
SPACING_FACTOR = 0.85

# Calcule o espaçamento entre os multiplicadores com base no fator
spacing = WIDTH // len(MULTIPLIERS) * SPACING_FACTOR

all_sprites = pygame.sprite.Group()
multipliers = pygame.sprite.Group()
balls = pygame.sprite.Group()  # Adicione esta linha

for i, value in enumerate(MULTIPLIERS):
    x_offset = (i + 0.5) * spacing + 58  # Define o deslocamento horizontal
    multiplier = Multiplier(x_offset, value)
    all_sprites.add(multiplier)
    multipliers.add(multiplier)

obstacles = create_obstacles()
all_sprites.add(obstacles)

# Variável para alternar entre criar à direita e à esquerda
create_ball_to_right = True

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x = event.pos[0]
            if create_ball_to_right:
                ball = Ball(WIDTH // 2 + 0, HEIGHT - 50)  # Cria a bola um pouco à direita
            else:
                ball = Ball(WIDTH // 2 - 8, HEIGHT - 50)  # Cria a bola um pouco à esquerda
            # Alterna a direção da próxima bola
            create_ball_to_right = not create_ball_to_right
            balls.add(ball)
            all_sprites.add(ball)

    screen.fill(BG_COLOR)

    for ball in balls:
        hits = pygame.sprite.spritecollide(ball, obstacles, False)
        if hits:
            ball.speed_y = 0
            for hit in hits:
                repulsion_direction = ball.body.position - hit.shape.body.position
                repulsion_force = repulsion_direction.normalized() * IMPULSE_FORCE
                ball.body.apply_impulse_at_local_point(repulsion_force)

    for multiplier in multipliers:
        multiplier.check_collision(balls)  # Verifique a colisão com os multiplicadores

    for ball in balls:
        ball.speed_y += 1
        ball.rect.centery += ball.speed_y

    space.step(1/FPS)
    all_sprites.update()
    all_sprites.draw(screen)

    for obstacle in obstacles:
        pygame.draw.circle(screen, (255, 255, 255), (int(obstacle.shape.body.position.x), int(
            obstacle.shape.body.position.y)), OBSTACLE_RADIUS)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
