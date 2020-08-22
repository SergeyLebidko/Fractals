import time
import random
import pygame as pg

# Основные параметры работы
W, H = 1200, 850
TOTAL_PIXEL_COUNT = W * H
DEFAULT_SCOPE = 0, 0, 0.003
ITER_LIMIT = 40
DELTA_COLOR = 255 // ITER_LIMIT


# Инициализируем окно
pg.init()
SC = pg.display.set_mode((W, H))
pg.display.set_caption('Fractals')

CLOCK = pg.time.Clock()
FONT = pg.font.SysFont('Arial', 28)


def point(surface, pos, color):
    pg.draw.rect(surface, color, (pos[0], pos[1], 1, 1))


def get_iter_count(z, c):
    for k in range(ITER_LIMIT):
        z = z * z + c
        if abs(z) > 2:
            break
    return k


def render_msg(msg, surface):
    surface.fill((0, 0, 0))
    msg_surface = FONT.render(msg, 0, (255, 255, 255))
    msg_surface_rect = msg_surface.get_rect()
    surface.blit(msg_surface, (W // 2 - msg_surface_rect.width // 2, H // 2 - msg_surface_rect.height // 2))
    return surface


def mandelbrot(x0, y0, delta_pixel):
    count_limit = 0
    current_pixel_count = 0
    result_surface = pg.Surface((W, H))
    text_surface = pg.Surface((W, H))

    for a in range(W):
        for b in range(H):
            c = complex(x0 + (a - W // 3 * 2) * delta_pixel, y0 - (b - H // 2) * delta_pixel)
            z = complex(0, 0)
            k = get_iter_count(z, c)
            color = tuple([255 - DELTA_COLOR * k for _ in range(3)])
            point(result_surface, (a, b), color)

            current_pixel_count += 1
            count_limit += 1
            if count_limit == 10000:
                count_limit = 0
                yield render_msg(
                    'Фрактал Мандельброта: {:.1%} выполнено...'.format(current_pixel_count / TOTAL_PIXEL_COUNT),
                    text_surface
                )

    yield result_surface


def julia(x0, y0, delta_pixel):
    count_limit = 0
    current_pixel_count = 0
    surface = pg.Surface((W, H))
    text_surface = pg.Surface((W, H))

    c = complex(0.36, 0.36)
    for a in range(W):
        for b in range(H):
            z = complex(x0 + (a - W // 2) * delta_pixel, y0 - (b - H // 2) * delta_pixel)
            k = get_iter_count(z, c)
            color = tuple([255 - DELTA_COLOR * k for _ in range(3)])
            point(surface, (a, b), color)

            current_pixel_count += 1
            count_limit += 1
            if count_limit == 10000:
                count_limit = 0
                yield render_msg(
                    'Фрактал Жюлиа: {:.1%} выполнено...'.format(current_pixel_count / TOTAL_PIXEL_COUNT),
                    text_surface
                )

    yield surface


FRACTAL_DESCRIPTIONS = [
    {
        'action': mandelbrot,
        'text': 'Фрактал Мандельброта',
    },
    {
        'action': julia,
        'text': 'Фрактал Жюлиа',
    }
]


class Menu:
    TRANSPARENT_COLOR = (255, 0, 0)

    def __init__(self):
        self.surface = pg.Surface((W, H))
        self.surface.set_colorkey(self.TRANSPARENT_COLOR)
        self.surface.fill(self.TRANSPARENT_COLOR)

        self.menu_rect = None
        self.show_flag = False

        self.items = []
        self.menu_width = self.menu_height = 0
        for description in FRACTAL_DESCRIPTIONS:
            text_surface = FONT.render(description['text'], 0, (255, 255, 255))
            self.items.append(
                {
                    'text_surface': text_surface,
                    'description': description
                }
            )
            text_surface_rect = text_surface.get_rect()
            self.menu_width = max(self.menu_width, text_surface_rect.width + 30)
            self.menu_height += text_surface_rect.height + 10

    def draw_menu(self, pos):
        # Если меню еще не отрисовывалось, то готовим данные для отрисовки его на новой позиции
        if not self.show_flag:
            menu_x, menu_y = pos
            if (menu_x + self.menu_width) > W:
                menu_x -= self.menu_width
            if (menu_y + self.menu_height) > H:
                menu_y -= self.menu_height
            self.menu_rect = pg.Rect(menu_x, menu_y, self.menu_width, self.menu_height)

            item_x, item_y = menu_x, menu_y
            for item in self.items:
                text_surface = item['text_surface']
                text_surface_rect = text_surface.get_rect()
                item['item_rect'] = pg.Rect(item_x, item_y, self.menu_width, text_surface_rect.height + 10)
                item_y += (text_surface_rect.height + 10)

            self.show_flag = True

        for item in self.items:
            item_rect = item['item_rect']
            text_surface = item['text_surface']
            if item_rect.collidepoint(pos):
                color = (95, 95, 105)
            else:
                color = (50, 50, 50)
            pg.draw.rect(self.surface, color, item_rect)
            self.surface.blit(text_surface, (item_rect.x + 15, item_rect.y + 5))

    def click(self, pos, button):
        selected_item = None

        if self.show_flag:
            for item in self.items:
                item_rect = item['item_rect']
                if item_rect.collidepoint(pos):
                    selected_item = item['description']

        self.surface.fill(self.TRANSPARENT_COLOR)
        self.show_flag = False

        if button == pg.BUTTON_RIGHT:
            self.draw_menu(pos)

        return selected_item

    def move(self, pos):
        if not self.show_flag:
            return
        self.draw_menu(pos)


def main():
    selected_fractal = random.choice(FRACTAL_DESCRIPTIONS)
    fractal_func = selected_fractal['action'](*DEFAULT_SCOPE)
    scopes = [DEFAULT_SCOPE]
    fractal_surface = pg.Surface((W, H))
    menu = Menu()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()

            # Во время отрисовки фрактала блокируем все действия пользоователя кроме закрытия окна
            if fractal_func:
                continue

            if event.type == pg.MOUSEMOTION:
                menu.move(event.pos)

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button in [pg.BUTTON_LEFT, pg.BUTTON_RIGHT, pg.BUTTON_MIDDLE]:
                    selected_fractal = menu.click(event.pos, event.button)
                    if selected_fractal:
                        fractal_func = selected_fractal['action'](*DEFAULT_SCOPE)

                elif event.button == pg.BUTTON_WHEELUP:
                    x0, y0, delta_pixel = scopes[-1]
                    pos_x, pos_y = event.pos
                    x0, y0 = x0 + (pos_x - (W // 2)) * delta_pixel, y0 - (pos_y - (H // 2)) * delta_pixel
                    delta_pixel /= 2
                    scopes.append((x0, y0, delta_pixel))
                    fractal_func = selected_fractal['action'](*scopes[-1])

                elif event.button == pg.BUTTON_WHEELDOWN:
                    if len(scopes) == 1:
                        continue
                    scopes.pop()
                    fractal_func = selected_fractal['action'](*scopes[-1])

        if fractal_func:
            try:
                value = next(fractal_func)
            except StopIteration:
                fractal_func = None
            else:
                fractal_surface = value

        SC.blit(fractal_surface, (0, 0))
        SC.blit(menu.surface, (0, 0))
        pg.display.update()

        CLOCK.tick(25)


if __name__ == '__main__':
    main()
