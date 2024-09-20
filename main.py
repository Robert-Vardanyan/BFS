import pygame
import random
from collections import deque

# Инициализация Pygame
pygame.init()

# Определение размеров окна приложения
width, height = 1200, 600
grid_width, grid_height = 800, 600  # Размеры области сетки
grid_size = 20  # Размер одной ячейки сетки
button_size = (150, 40)  # Размеры кнопок
screen = pygame.display.set_mode((width, height))  # Установка размеров окна
icon = pygame.image.load('search-location.png')  # Загрузка иконки
pygame.display.set_icon(icon)  # Установка иконки окна
pygame.display.set_caption("BFS by ROVA")  # Установка заголовка окна

# Определение цветов в RGB
BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BUTTON_COLOR = (0, 100, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
OBSTACLE_COLOR = (128, 128, 128)

# Хранение клеток и их состояния
all_cells = {}  # Словарь для хранения состояния клеток
path = []  # Список для хранения найденного пути
visited_cells = []  # Список посещенных клеток
searching_started = False  # Флаг, указывающий, начат ли поиск
search_text_color = WHITE  # Цвет текста состояния поиска

# Переменные для пользовательского ввода
obstacle_count = 200  # Количество препятствий по умолчанию
search_delay = 2  # Задержка поиска в миллисекундах
active_input = None  # Поле ввода, активное в данный момент
input_fields = {'obstacle': '200', 'delay': '2'}  # Значения в полях ввода

# Функция для инициализации всех клеток (по умолчанию 0 — не выделена)
def all_cells_0():
    global all_cells
    all_cells = {(j, i): 0 for i in range(30) for j in range(40)}  # Инициализация клеток

# Функция генерации точек (черной и красной)
def point_genetration():
    black_point = (random.randint(0, 39), random.randint(0, 29))  # Случайная позиция черной точки
    while True:
        red_point = (random.randint(0, 39), random.randint(0, 29))  # Случайная позиция красной точки
        if red_point != black_point:  # Убедимся, что точки разные
            break
    return black_point, red_point

# Инициализация точек
black_point, red_point = (5, 5), (25, 25)  # Статические начальные позиции для тестирования

# Позиция кнопок управления
search_button_rect = pygame.Rect(width - (button_size[0] * 2.2), button_size[1] * 6, *button_size)
restart_button_rect = pygame.Rect(width - (button_size[0] * 2), button_size[1] * 9, *button_size)
obstacle_button_rect = pygame.Rect(width - (button_size[0] * 2.2), button_size[1] * 4.5, *button_size)

# Позиции полей ввода для управления пользователем
obstacle_input_rect = pygame.Rect(width - (button_size[0] * 1.2), button_size[1] * 4.5, 60, button_size[1])
delay_input_rect = pygame.Rect(width - (button_size[0] * 1.2), button_size[1] * 6, 60, button_size[1])

# Функция для отрисовки сетки
def draw_grid():
    for x in range(0, grid_width, grid_size):  # Проход по всем горизонтальным координатам
        for y in range(0, grid_height, grid_size):  # Проход по всем вертикальным координатам
            rect = pygame.Rect(x, y, grid_size, grid_size)  # Создание прямоугольника для клетки
            grid_pos = (x // grid_size, y // grid_size)  # Определение позиции клетки в сетке

            # Определение цвета клетки в зависимости от её состояния
            if grid_pos in path:
                pygame.draw.rect(screen, GREEN, rect)  # Путь
            elif all_cells[grid_pos] == 1:
                pygame.draw.rect(screen, YELLOW, rect)  # Выделенная клетка
            elif grid_pos in visited_cells:
                pygame.draw.rect(screen, BLUE, rect)  # Посещенная клетка
            elif all_cells[grid_pos] == 2:
                pygame.draw.rect(screen, OBSTACLE_COLOR, rect)  # Объект-препятствие

            pygame.draw.rect(screen, GRAY, rect, 1)  # Рисуем границы клеток

# Функция для отрисовки черной и красной точек
def draw_points():
    pygame.draw.circle(screen, BLACK, (black_point[0] * grid_size + grid_size // 2, black_point[1] * grid_size + grid_size // 2), grid_size // 3)
    pygame.draw.circle(screen, RED, (red_point[0] * grid_size + grid_size // 2, red_point[1] * grid_size + grid_size // 2), grid_size // 3)

# Функция для отрисовки кнопок
def draw_button(button, text, color, path, active, text_color=WHITE):
    if text == 'Restart':
        button_color = color if not active else GRAY  # Меняем цвет кнопки, если она активна
    else:
        button_color = color if (not active and not path) else GRAY  # Меняем цвет кнопки в зависимости от состояния

    pygame.draw.rect(screen, button_color, button)  # Отрисовка кнопки
    font = pygame.font.Font(None, 30)  # Создание шрифта для текста
    text_surf = font.render(text, True, text_color)  # Отрисовка текста
    text_rect = text_surf.get_rect(center=button.center)  # Центрирование текста по кнопке
    screen.blit(text_surf, text_rect)  # Отрисовка текста на экране

# Функция для отрисовки поля ввода
def draw_input_box(rect, text, active):
    color = GREEN if active else GRAY  # Цвет поля ввода зависит от активности
    pygame.draw.rect(screen, color, rect, 2)  # Отрисовка поля
    font = pygame.font.Font(None, 30)  # Шрифт текста
    text_surf = font.render(text, True, BLACK)  # Отрисовка текста
    screen.blit(text_surf, (rect.x + 5, rect.y + 5))  # Отрисовка текста внутри поля

# Функция для перезапуска игры
def restarting_game():
    global black_point, red_point, path, searching_started, visited_cells, search_text_color
    black_point, red_point = point_genetration()  # Генерация новых точек
    all_cells_0()  # Сброс состояния клеток
    path = []  # Очистка пути
    searching_started = False  # Сброс состояния поиска
    visited_cells = []  # Очистка посещенных клеток
    search_text_color = WHITE  # Сброс цвета текста

# Функция для добавления препятствий на поле
def add_obstacle():
    global obstacle_count
    for _ in range(obstacle_count):  # Добавляем заданное количество препятствий
        while True:
            obstacle = (random.randint(0, 39), random.randint(0, 29))  # Генерация случайной позиции для препятствия
            # Проверка, что препятствие не совпадает с точками и не находится в уже занятой клетке
            if obstacle != black_point and obstacle != red_point and all_cells[obstacle] == 0:
                all_cells[obstacle] = 2  # Устанавливаем клетку как препятствие
                break

# Функция для поиска пути с использованием алгоритма BFS
def bfs_search(black_point, red_point):
    global search_delay
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Направления для перемещения по сетке
    queue = deque([(black_point, [black_point])])  # Очередь для BFS с начальной точкой

    visited = set()  # Множество для хранения посещенных клеток
    visited.add(black_point)  # Добавление начальной точки в посещенные

    while queue:  # Пока очередь не пуста
        current_point, path = queue.popleft()  # Извлечение текущей точки и пути
        visited_cells.append(current_point)  # Добавление текущей точки в список посещенных

        draw_grid()  # Отрисовка сетки
        draw_points()  # Отрисовка точек
        pygame.display.flip()  # Обновление экрана
        pygame.time.delay(search_delay)  # Задержка между шагами поиска

        if current_point == red_point:  # Проверка, достигли ли мы целевой точки
            return path  # Возвращаем найденный путь

        # Перебор соседних клеток
        for direction in directions:
            neighbor = (current_point[0] + direction[0], current_point[1] + direction[1])  # Получение соседней клетки
            # Проверка границ и условий проходимости
            if 0 <= neighbor[0] < 40 and 0 <= neighbor[1] < 30:
                if all_cells[neighbor] != 1 and all_cells[neighbor] != 2 and neighbor not in visited:
                    visited.add(neighbor)  # Добавление соседней клетки в посещенные
                    queue.append((neighbor, path + [neighbor]))  # Добавление в очередь для дальнейшего поиска

    return None  # Если путь не найден

# Функция для начала поиска
def start_search():
    global path, visited_cells, search_text_color, searching_started
    
    visited_cells = []  # Очистка списка посещенных клеток
    path = bfs_search(black_point, red_point) or []  # Запуск поиска пути

    # Обновление состояния поиска в зависимости от результата
    if path:
        search_text_color = GREEN  # Путь найден, устанавливаем зеленый цвет
    else:
        search_text_color = RED  # Путь не найден, устанавливаем красный цвет
        path.append('x')  # Добавляем маркер о неудаче
    
    searching_started = False  # Завершение состояния поиска

# Инициализация состояния клеток
all_cells_0()

# Основной цикл приложения
running = True
while running:
    screen.fill(WHITE)  # Заполнение экрана белым цветом

    # Блокировка кнопок поиска и препятствий, если поиск начался
    draw_grid()  # Отрисовка сетки
    draw_points()  # Отрисовка точек
    draw_button(obstacle_button_rect, 'Add Obstacle', BUTTON_COLOR, path, searching_started)
    draw_button(search_button_rect, 'Search', BUTTON_COLOR, path, searching_started, search_text_color)
    draw_button(restart_button_rect, 'Restart', BUTTON_COLOR, path, searching_started)

    draw_input_box(obstacle_input_rect, input_fields['obstacle'], active_input == 'obstacle')  # Поле ввода для количества препятствий
    draw_input_box(delay_input_rect, input_fields['delay'], active_input == 'delay')  # Поле ввода для задержки

    # Обработка событий Pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Проверка на выход из приложения
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:  # Проверка на нажатие кнопки мыши
            # Обработка нажатия на поля ввода
            if obstacle_input_rect.collidepoint(event.pos):
                active_input = 'obstacle'  # Активируем поле для ввода количества препятствий
            elif delay_input_rect.collidepoint(event.pos):
                active_input = 'delay'  # Активируем поле для ввода задержки
            elif search_button_rect.collidepoint(event.pos) and not searching_started:  # Нажатие на кнопку поиска
                searching_started = True  # Устанавливаем флаг начала поиска
                draw_button(obstacle_button_rect, 'Add Obstacle', BUTTON_COLOR, path, searching_started)
                draw_button(search_button_rect, 'Search', BUTTON_COLOR, path, searching_started, search_text_color)
                draw_button(restart_button_rect, 'Restart', BUTTON_COLOR, path, searching_started)
                search_delay = int(input_fields['delay'])  # Получение задержки из поля ввода
                start_search()  # Запуск поиска пути
            elif restart_button_rect.collidepoint(event.pos):  # Нажатие на кнопку перезапуска
                restarting_game()  # Перезапуск игры
            elif obstacle_button_rect.collidepoint(event.pos) and not searching_started:  # Нажатие на кнопку добавления препятствий
                obstacle_count = int(input_fields['obstacle'])  # Получение количества препятствий из поля ввода
                add_obstacle()  # Добавление препятствий на поле
            else:  # Обработка нажатий на сетку
                if not searching_started:
                    mouse_x, mouse_y = event.pos
                    if mouse_x < grid_width and mouse_y < grid_height:  # Проверка, что клик был в пределах сетки
                        grid_x = mouse_x // grid_size
                        grid_y = mouse_y // grid_size
                        cell = (grid_x, grid_y)

                        # Переключение состояния клетки (выделена/не выделена)
                        if cell != black_point and cell != red_point:
                            all_cells[cell] = 1 if all_cells[cell] == 0 else 0

        # Обработка событий клавиатуры
        elif event.type == pygame.KEYDOWN and active_input:
            if event.key == pygame.K_RETURN:  # Проверка нажатия Enter
                if active_input == 'obstacle':
                    obstacle_count = int(input_fields['obstacle'])  # Сохранение количества препятствий
                elif active_input == 'delay':
                    search_delay = int(input_fields['delay'])  # Сохранение задержки
                active_input = None  # Сброс активного поля ввода
            elif event.key == pygame.K_BACKSPACE:  # Обработка нажатия Backspace
                input_fields[active_input] = input_fields[active_input][:-1]  # Удаление последнего символа
            else:
                if event.unicode.isdigit():  # Проверка, является ли вводимое значение числом
                    input_fields[active_input] += event.unicode  # Добавление символа в текущее поле

    pygame.display.flip()  # Обновление экрана после всех отрисовок

pygame.quit()  # Завершение работы Pygame
