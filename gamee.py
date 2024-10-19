import pygame
import random

# Инициализация pygame
pygame.init()

# Размеры окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)

# Скорость движения
PLAYER_SPEED = 3
NPC_SPEED = 1
CAR_SPEED = 5

# Размеры трассы
LANE_WIDTH = WIDTH // 4
PEDESTRIAN_LANE_WIDTH = WIDTH // 2

# Класс для игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.health = 100

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_UP]:
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            self.rect.y += PLAYER_SPEED

# Класс для NPC (пешеходов)
class NPC(pygame.sprite.Sprite):
    def __init__(self, mood, phrases, interaction_phrases):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(random.randint(WIDTH // 2 - 30, WIDTH // 2 + 30), random.randint(HEIGHT // 4, 3 * HEIGHT // 4)))
        self.mood = mood
        self.phrases = phrases
        self.interaction_phrases = interaction_phrases
        self.speed = NPC_SPEED
        self.direction = pygame.Vector2(0, random.choice([-1, 1]))  # Движение по вертикали
        self.last_phrase = None

    def change_direction(self):
        self.direction.y = random.choice([-1, 1])

    def update(self):
        self.rect.y += self.direction.y * self.speed

        # Изменение настроения и поведения
        if self.mood == "happy":
            self.speed = NPC_SPEED + 1
        elif self.mood == "angry":
            self.speed = NPC_SPEED - 1
        elif self.mood == "neutral":
            self.speed = NPC_SPEED

        # Ограничение движения NPC на пешеходном переходе
        if self.rect.top < HEIGHT // 4 or self.rect.bottom > 3 * HEIGHT // 4:
            self.direction.y *= -1

        # Периодически менять направление
        if random.randint(0, 100) < 2:
            self.change_direction()

    def say_phrase(self):
        self.last_phrase = random.choice(self.phrases)

    def interact(self, other_npc):
        return random.choice(self.interaction_phrases)

# Класс для автомобилей
class Car(pygame.sprite.Sprite):
    def __init__(self, lane, direction):
        super().__init__()
        self.image = pygame.Surface((60, 30))
        self.image.fill(GRAY)
        self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
        self.speed = CAR_SPEED
        self.direction = direction  # 1 - направо, -1 - налево
        self.lane = lane  # Верхняя или нижняя полоса
        self.stopped = False  # Статус остановки автомобиля

    def update(self):
        if not self.stopped:  # Если автомобиль не остановлен
            self.rect.x += self.speed * self.direction
            if self.direction == 1 and self.rect.left > WIDTH:
                self.rect.right = 0
            elif self.direction == -1 and self.rect.right < 0:
                self.rect.left = WIDTH

        # Перемещение автомобиля по полосе
        if self.lane == "top":
            self.rect.centery = HEIGHT // 3
        else:
            self.rect.centery = 3 * HEIGHT // 5

    def stop(self):
        self.stopped = True  # Остановка автомобиля

    def go(self):
        self.stopped = False  # Возобновление движения автомобиля

# Группы спрайтов
all_sprites = pygame.sprite.Group()
npcs = pygame.sprite.Group()
cars = pygame.sprite.Group()

# Создание игрока
player = Player()
all_sprites.add(player)

# Фразы для NPC
phrases = ["Не толкай!", "Осторожно!", "Следи за собой!"]
interaction_phrases = ["Привет, как дела?", "Что ты думаешь о погоде?", "Не очень-то и приятно здесь!", "Согласен, тут слишком людно."]

# Создание NPC с разными настроениями
for i in range(4):
    npc = NPC(random.choice(["happy", "angry", "neutral"]), phrases, interaction_phrases)
    npcs.add(npc)
    all_sprites.add(npc)

# Создание автомобилей
for i in range(3):
    car1 = Car("top", 1)  # Автомобиль едет по верхней полосе направо
    car2 = Car("bottom", -1)  # Автомобиль едет по нижней полосе налево
    cars.add(car1, car2)
    all_sprites.add(car1, car2)

# Основной цикл игры
running = True
clock = pygame.time.Clock()

while running:
    clock.tick(60)
    keys = pygame.key.get_pressed()

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Обновление игрока
    player.update(keys)

    # Обновление NPC и автомобилей
    npcs.update()
    cars.update()

    # Проверка на столкновения NPC с игроком и вывод фраз
    for npc in npcs:
        if pygame.sprite.collide_rect(npc, player):
            npc.say_phrase()  # NPC говорит фразу при столкновении

    # Проверка на взаимодействие между NPC
    for npc1 in npcs:
        for npc2 in npcs:
            if npc1 != npc2 and npc1.rect.colliderect(npc2.rect):  # Проверка на близость
                npc1.last_phrase = npc1.interact(npc2)  # NPC говорит фразу другому NPC

    # Проверка на столкновения NPC с автомобилями
    for car in cars:
        for npc in npcs:
            if pygame.sprite.collide_rect(car, npc):
                car.stop()  # Остановка автомобиля если NPC перед ним
            else:
                car.go()  # Возобновление движения автомобиля

    # Проверка на столкновения игрока с автомобилями
    if pygame.sprite.spritecollide(player, cars, False):
        player.health -= 1  # Уменьшение здоровья игрока при столкновении с автомобилем

    # Отображение
    screen.fill(GRAY)

    # Рисуем дорожные полосы
    pygame.draw.rect(screen, BLACK, (0, HEIGHT // 4, WIDTH, LANE_WIDTH))  # Верхняя полоса
    pygame.draw.rect(screen, BLACK, (0, 3 * HEIGHT // 4 - LANE_WIDTH, WIDTH, LANE_WIDTH))  # Нижняя полоса

    # Рисуем пешеходный переход (вертикальные белые полосы)
    for i in range(15):
        pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 40, HEIGHT // 4 + i * 20 + 10, 80, 10))

    all_sprites.draw(screen)

    # Отображение здоровья игрока
    font = pygame.font.Font(None, 36)
    text = font.render(f"Health: {player.health}", True, WHITE)
    screen.blit(text, (10, 10))

    # Отображение фраз NPC
    for npc in npcs:
        if npc.last_phrase:
            phrase_text = font.render(npc.last_phrase, True, WHITE)
            screen.blit(phrase_text, (npc.rect.x, npc.rect.y - 20))

    pygame.display.flip()

pygame.quit()
