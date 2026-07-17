"""Реализация игры «Змейка» на Pygame."""

from random import randint
import pygame


SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

DIRECTION_MAP = {
    (pygame.K_UP, LEFT): UP,
    (pygame.K_UP, RIGHT): UP,

    (pygame.K_DOWN, LEFT): DOWN,
    (pygame.K_DOWN, RIGHT): DOWN,

    (pygame.K_LEFT, UP): LEFT,
    (pygame.K_LEFT, DOWN): LEFT,

    (pygame.K_RIGHT, UP): RIGHT,
    (pygame.K_RIGHT, DOWN): RIGHT,
}

BOARD_BACKGROUND_COLOR = (0, 0, 0)

BORDER_COLOR = (93, 216, 228)

APPLE_COLOR = (255, 0, 0)

SNAKE_COLOR = (0, 255, 0)

SPEED = 10

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

pygame.display.set_caption('Змейка')

clock = pygame.time.Clock()


class GameObject:
    """Базовый класс игры."""

    def __init__(self):
        """Инициализация объекта."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = None

    def _draw_cell(self, position=None, color=None):
        """Отрисовывает одну клетку игрового поля."""
        position = position or self.position
        color = color or self.body_color

        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Отрисовывает игровой объект."""
        raise NotImplementedError(
            'Метод draw() должен быть реализован в дочерних классах. '
        )


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self, occupied_cells=None):
        """Инициализация яблока."""
        super().__init__()
        self.body_color = APPLE_COLOR

        if occupied_cells is not None:
            self.randomize_position(occupied_cells)

    def randomize_position(self, occupied_cells):
        """Случайным образом размещает яблоко на игровом поле."""
        occupied_cells = occupied_cells or set()

        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if self.position not in occupied_cells:
                break

    def draw(self):
        """Отрисовывает яблоко на экране."""
        self._draw_cell()


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self):
        """Инициализация змейки."""
        super().__init__()
        self.length = 1
        self.body_color = SNAKE_COLOR
        self.reset()

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def move(self):
        """Перемещает змейку."""
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction

        new_head = (
            (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.positions.pop()

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None

    def draw(self):
        """Отрисовывает змейку."""
        for position in self.positions:
            self._draw_cell(position)

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


def place_apple(apple, snake):
    """Размещает яблоко в свободной клетке."""
    occupied_cells = set(snake.positions)
    apple.randomize_position(occupied_cells)


def reset_game(snake, apple):
    """Перезапуск игры."""
    snake.reset()
    place_apple(apple, snake)
    screen.fill(BOARD_BACKGROUND_COLOR)


def main():
    """Запуск игры."""
    snake = Snake()
    apple = Apple()

    place_apple(apple, snake)

    while True:
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        screen.fill(BOARD_BACKGROUND_COLOR)

        if snake.get_head_position() == apple.position:
            snake.length += 1
            place_apple(apple, snake)

        if snake.get_head_position() in snake.positions[1:]:
            reset_game(snake, apple)
            continue

        apple.draw()
        snake.draw()

        pygame.display.update()
        clock.tick(SPEED)


def handle_keys(game_object):
    """Обработка нажатий клавиш."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit("Игра завершена пользователем.")

        if event.type == pygame.KEYDOWN:
            key = event.key

            new_direction = DIRECTION_MAP.get(
                (key, game_object.direction),
                game_object.direction,
            )

            if new_direction != game_object.direction:
                game_object.next_direction = new_direction


if __name__ == '__main__':
    main()
