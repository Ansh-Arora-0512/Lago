import pygame
import pygame.gfxdraw
from collections import deque
from bot import Board, Infinity
from time import time


def update_board(is_player=True):
    global current

    pygame.draw.rect(board, "#008450", board_surface, border_radius=15)
    for line in lines:
        pygame.draw.line(board, "#000000", line[0], line[1])
        pygame.draw.line(board, "#000000", line[2], line[3])

    for y, x in current.our:
        pygame.gfxdraw.filled_circle(board,
                                     board_w * x // 8 + board_w // 16 + 1,
                                     board_w * y // 8 + board_w // 16 + 1,
                                     board_w // 16 - 5,
                                     (0, 0, 0) if current.player else (255, 255, 255))
        pygame.gfxdraw.aacircle(board,
                                board_w * x // 8 + board_w // 16 + 1,
                                board_w * y // 8 + board_w // 16 + 1,
                                board_w // 16 - 5,
                                (0, 0, 0) if current.player else (255, 255, 255))

    for y, x in current.their:
        pygame.gfxdraw.filled_circle(board,
                                     board_w * x // 8 + board_w // 16 + 1,
                                     board_w * y // 8 + board_w // 16 + 1,
                                     board_w // 16 - 5,
                                     (255, 255, 255) if current.player else (0, 0, 0))
        pygame.gfxdraw.aacircle(board,
                                board_w * x // 8 + board_w // 16 + 1,
                                board_w * y // 8 + board_w // 16 + 1,
                                board_w // 16 - 5,
                                (255, 255, 255) if current.player else (0, 0, 0))

    for y, x in current.children:
        pygame.gfxdraw.aacircle(board,
                                board_w * x // 8 + board_w // 16 + 1,
                                board_w * y // 8 + board_w // 16 + 1,
                                board_w // 16 - 5,
                                (30, 30, 30) if current.player else (200, 200, 200))

    if current.player:
        pygame.draw.rect(screen, "#fffdd0", b_rect, border_radius=15)
        pygame.draw.rect(screen, "#000000", w_rect)
        grid_font.render_to(screen, (b_rect.left + 7, b_rect.top + 7), "BLACK", "#000000")
        grid_font.render_to(screen, (w_rect.left + 7, w_rect.top + 7), "WHITE", "#ffffff")
        count_font.render_to(screen, (b_rect.left + 7, b_rect.top + 25), str(len(current.our)), "#000000")
        count_font.render_to(screen, (w_rect.left + 7, w_rect.top + 25), str(len(current.their)), "#ffffff")
        timer_font.render_to(screen, w_timer_rect.topleft, f"{w_mins:02}:{w_secs:02}", "#ffffff")
    else:
        pygame.draw.rect(screen, "#fffdd0", w_rect, border_radius=15)
        pygame.draw.rect(screen, "#000000", b_rect)
        grid_font.render_to(screen, (b_rect.left + 7, b_rect.top + 7), "BLACK", "#ffffff")
        grid_font.render_to(screen, (w_rect.left + 7, w_rect.top + 7), "WHITE", "#000000")
        count_font.render_to(screen, (b_rect.left + 7, b_rect.top + 25), str(len(current.their)), "#ffffff")
        count_font.render_to(screen, (w_rect.left + 7, w_rect.top + 25), str(len(current.our)), "#000000")
        timer_font.render_to(screen, b_timer_rect.topleft, f"{b_mins:02}:{b_secs:02}", "#ffffff")

    screen.blit(board, (margin, margin))
    pygame.display.update((board_rect, timer_rect))

    if is_player:
        current = current.search()
        update_board(False)


if __name__ == "__main__":
    pygame.init()
    w = 560
    h = 660
    margin = 25
    out_margin = 15
    screen = pygame.display.set_mode((w, h))
    clock = pygame.time.Clock()
    running = True
    dt = 0
    turn = 0

    screen.fill("#000000")
    othello_font = pygame.freetype.SysFont("Sans", 50)
    grid_font = pygame.freetype.SysFont("Sans", 15)
    count_font = pygame.freetype.SysFont("Sans", 21)
    timer_font = pygame.freetype.SysFont("Sans", 48)
    board_w = w - 2 * margin
    board_surface = pygame.Rect(0, 0, board_w, board_w)
    board_rect = pygame.Rect(margin, margin, board_w, board_w)
    board = pygame.Surface((board_w, board_w))
    lines = []
    for i in range(1, 9):
        temp = board_w * i // 8
        lines.append(((temp, 0), (temp, board_w), (0, temp), (board_w, temp)))
        temp = temp - board_w // 16 + margin - 5
        grid_font.render_to(screen, (temp, w - margin + 5), chr(64 + i), "#ffffff")
        grid_font.render_to(screen, (margin - 12, temp), str(i), "#ffffff")

    undo = pygame.Rect(w - 2 * margin - 105, board_w + 2 * margin + 10, 60, h - board_w - 4 * margin)
    redo = pygame.Rect(w - margin - 60, board_w + 2 * margin + 10, 60, h - board_w - 4 * margin)
    pygame.draw.rect(screen, "#fffdd0", undo, border_radius=15)
    pygame.draw.rect(screen, "#fffdd0", redo, border_radius=15)
    othello_font.render_to(screen, ((undo.left + undo.right)//2 - 11, (undo.bottom + undo.top)//2 - 13), "<", "#000000")
    othello_font.render_to(screen, ((redo.left + redo.right)//2 - 8, (redo.bottom + redo.top)//2 - 13), ">", "#000000")
    b_millis, b_secs, b_mins, w_millis, w_secs, w_mins = (0,) * 6
    b_rect = pygame.Rect(margin, board_w + 2 * margin + 10, 165, h - board_w - 4 * margin)
    w_rect = pygame.Rect(margin + 172, board_w + 2 * margin + 10, 165, h - board_w - 4 * margin)
    timer_rect = pygame.Rect(margin, board_w + 2 * margin + 10, 342, h - board_w - 4 * margin)
    b_timer_rect = pygame.Rect(margin + 60, board_w + 2 * margin + 16, 100, 35)
    w_timer_rect = pygame.Rect(margin + 232, board_w + 2 * margin + 16, 100, 35)
    pygame.display.flip()

    x, y = pygame.mouse.get_pos()
    undo_stack = deque()
    end = False
    current = Board()
    current.peek()
    update_board()

    while running:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and not end:
                coords = ([i for i in range(8) if y > board_w * i // 8 + margin],
                          [i for i in range(8) if x > board_w * i // 8 + margin])
                if coords[0] and coords[1]:
                    coords = (coords[0][-1], coords[1][-1])
                    if coords in current.children:
                        current = current.move(coords)
                        end = current.peek()
                        update_board()
                        if end:
                            pass

                if undo.top < y < undo.bottom:
                    if undo.left < x < undo.right and current.parent is not None:
                        undo_stack.append(current)
                        current = current.parent
                        update_board()
                    if redo.left < x < redo.right and undo_stack:
                        current = undo_stack.pop()
                        update_board()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and current.parent is not None:
                    undo_stack.append(current)
                    current = current.parent
                    update_board()
                elif event.key == pygame.K_RIGHT and undo_stack:
                    current = undo_stack.pop()
                    update_board()

        clock.tick(30)
        if current.player:
            b_millis += clock.get_time()
            if b_millis >= 1000:
                b_millis = 0
                b_secs += 1
            if b_secs == 60:
                b_mins += 1
                b_secs = 0
            pygame.draw.rect(screen, "#fffdd0", b_timer_rect)
            timer_font.render_to(screen, b_timer_rect.topleft, f"{b_mins:02}:{b_secs:02}", "#000000")
            pygame.display.update(b_timer_rect)
        else:
            w_millis += clock.get_time()
            if w_millis >= 1000:
                w_millis = 0
                w_secs += 1
            if w_secs == 60:
                w_mins += 1
                w_secs = 0
            pygame.draw.rect(screen, "#fffdd0", w_timer_rect)
            timer_font.render_to(screen, w_timer_rect.topleft, f"{w_mins:02}:{w_secs:02}", "#000000")
            pygame.display.update(w_timer_rect)
        x, y = pygame.mouse.get_pos()

    pygame.quit()
