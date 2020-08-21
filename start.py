import time
import pygame as pg

# Основные параметры работы
W, H = 1200, 850
TOTAL_PIXEL_COUNT = W * H
DELTA_X = DELTA_Y = 0.0030
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


def mandelbrot():
    count_limit = 0
    current_pixel_count = 0
    result_surface = pg.Surface((W, H))
    text_surface = pg.Surface((W, H))

    for a in range(W):
        for b in range(H):
            c = complex((a - W // 3 * 2) * DELTA_X, (b - H // 2) * DELTA_Y)
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


def julia():
    count_limit = 0
    current_pixel_count = 0
    surface = pg.Surface((W, H))
    text_surface = pg.Surface((W, H))

    c = complex(0.36, 0.36)
    for a in range(W):
        for b in range(H):
            z = complex((a - W // 2) * DELTA_X, (b - H // 2) * DELTA_Y)
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


class Menu:

    TRANSPARENT_COLOR = (255, 0, 0)
    ITEMS_DATA = [
        {
            'action': mandelbrot,
            'text': 'Фрактал Мандельброта'
        },
        {
            'action': julia,
            'text': 'Фрактал Жюлиа'
        }
    ]

    def __init__(self):
        self.surface = pg.Surface((W, H))
        self.surface.set_colorkey(self.TRANSPARENT_COLOR)
        self.surface.fill(self.TRANSPARENT_COLOR)
        self.menu_rect = None
        self.items = None
        self.show_flag = False

    def draw_menu(self, pos):
        # Если меню еще не отрисовывалось, то готовим данные для отрисовки
        if not self.show_flag:
            self.items = []
            menu_width = menu_height = 0
            for item_data in self.ITEMS_DATA:
                text_surface = FONT.render(item_data['text'], 0, (255, 255, 255))
                text_surface_rect = text_surface.get_rect()
                self.items.append(
                    {
                        'text_surface': text_surface,
                        'action': item_data['action']
                    }
                )
                menu_width = max(menu_width, text_surface_rect.width + 30)
                menu_height += text_surface_rect.height + 10

            menu_x, menu_y = pos
            if (menu_x + menu_width) > W:
                menu_x -= menu_width
            if (menu_y + menu_height) > H:
                menu_y -= menu_height
            self.menu_rect = pg.Rect(menu_x, menu_y, menu_width, menu_height)

            self.show_flag = True

        item_x, item_y = self.menu_rect.x, self.menu_rect.y
        for item in self.items:
            text_surface = item['text_surface']
            text_surface_rect = text_surface.get_rect()

            item_rect = item.setdefault(
                'item_rect',
                pg.Rect(item_x, item_y, self.menu_rect.width, text_surface_rect.height + 10)
            )

            if item_rect.collidepoint(pos):
                color = (95, 95, 110)
            else:
                color = (50, 50, 50)

            pg.draw.rect(self.surface, color, item_rect)
            self.surface.blit(text_surface, (item_x + 15, item_y + 5))

            item_y += (text_surface_rect.height + 10)

    def clear_menu(self):
        self.surface.fill(self.TRANSPARENT_COLOR)
        self.menu_rect = None
        self.items = None
        self.show_flag = False

    def click(self, pos, button):
        if not self.show_flag:
            if button == pg.BUTTON_RIGHT:
                self.draw_menu(pos)
            return None
        else:
            selected_action = None
            if self.menu_rect.collidepoint(pos):
                for item in self.items:
                    item_rect = item['item_rect']
                    if item_rect.collidepoint(pos):
                        selected_action = item['action']()

            self.clear_menu()
            if button == pg.BUTTON_RIGHT:
                self.draw_menu(pos)
            return selected_action

    def move(self, pos):
        if not self.show_flag:
            return
        self.draw_menu(pos)


def main():
    fractal_func = mandelbrot()
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
                fractal_func = menu.click(event.pos, event.button)

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
