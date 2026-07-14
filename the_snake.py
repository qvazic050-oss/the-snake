from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10

pygame.init()

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс игры"""

    def __init__(self):
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = None

    def draw(self):
        """Рисуем объект на экране"""
        pass


class Apple(GameObject):
    """Класс яблока"""

    def __init__(self):
        """Инициализация яблока"""
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position()

    def randomize_position(self):
        """Случайным образом размещаем яблоко на игровом поле"""
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
        )

    def draw(self):
        """Рисуем яблоко на экране"""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс змейки"""

    def __init__(self):
        """Инициализация змейки"""
        super().__init__()
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.body_color = SNAKE_COLOR
        self.last = None

    def get_head_position(self):
        """Возвращаем позицию головы змейки"""
        return self.positions[0]

    def move(self):
        """Перемещаем змейку"""
        head_x, head_y = self.get_head_position()

        new_head = (
            (head_x + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head)
        self.last = None

        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def reset(self):
        """Сбрасываем змейку в начальное состояние"""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.length = 1
        self.positions = [self.position]
        self.direction = choice((UP, DOWN, LEFT, RIGHT))
        self.next_direction = None
        self.last = None

    def draw(self):
        """Рисуем змейку на экране"""
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def update_direction(self):
        """Обновляем направление движения змейки"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


class Obstacle(GameObject):
    """Класс препятствия."""

    def __init__(self):
        super().__init__()
        self.body_color = (120, 120, 120)
        self.visible = False
        self.cells = []

    def randomize(self, snake, apple):
        """Создает новое препятствие."""
        self.visible = choice([True, False])

        if not self.visible:
            self.cells = []
            return
        while True:
            size = randint(1, 3)

            x = randint(0, GRID_WIDTH - size) * GRID_SIZE
            y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE

            cells = [
                (x + i * GRID_SIZE, y)
                for i in range(size)
            ]
            if (
                all(cell not in snake.positions for cell in cells)
                and apple.position not in cells
            ):
                self.cells = cells
                break

    def draw(self):
        """Рисует препятствие на экране."""
        if not self.visible:
            return

        for cell in self.cells:
            rect = pygame.Rect(cell, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


def place_apple(apple, snake, obstacle):
    """Размещает яблоко в свободной клетке."""
    apple.randomize_position()

    while (
        apple.position in obstacle.cells
        or apple.position in snake.positions
    ):
        apple.randomize_position()


def reset_game(snake, apple, obstacle):
    """Сбрасывает игру после столкновения."""
    snake.reset()
    place_apple(apple, snake, obstacle)
    obstacle.randomize(snake, apple)


def main():
    """Запуск игры"""
    snake = Snake()
    apple = Apple()
    obstacle = Obstacle()
    place_apple(apple, snake, obstacle)
    obstacle.randomize(snake, apple)
    last_obstacle_update = pygame.time.get_ticks()

    while True:
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        current_time = pygame.time.get_ticks()

        if current_time - last_obstacle_update >= 5000:
            obstacle.randomize(snake, apple)
            last_obstacle_update = current_time

        if snake.get_head_position() == apple.position:
            snake.length += 1
            place_apple(apple, snake, obstacle)
        if (
            snake.get_head_position() in snake.positions[1:]
            or snake.get_head_position() in obstacle.cells
        ):
            reset_game(snake, apple, obstacle)
        screen.fill(BOARD_BACKGROUND_COLOR)

        obstacle.draw()
        apple.draw()
        snake.draw()

        pygame.display.update()
        clock.tick(SPEED)


def handle_keys(game_object):
    """Обработка нажатий клавиш"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


if __name__ == '__main__':
    main()
