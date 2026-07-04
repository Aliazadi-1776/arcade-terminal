import curses
import time

# لیست بازی‌ها به همراه نام و آیکن‌های پیشرفته (ASCII Art)
GAMES = [
    {
        "id": "snake",
        "name": "Snake",
        "icon": [
            "    ____      ",
            "   / . .\\     ",
            "   \\  ---<    ",
            "    \\  /      ",
            "  __/ /       ",
            "  \\__/        "
        ]
    },
    {
        "id": "pong",
        "name": "Pong",
        "icon": [
            "  |    :    ",
            "  |    :  | ",
            "  | O  :  | ",
            "       :  | ",
            "       :    ",
            "       :    "
        ]
    },
    {
        "id": "invaders",
        "name": "Space Invaders",
        "icon": [
            "   .    .   ",
            "    \\  /    ",
            "  .------.  ",
            "  |o_  _o|  ",
            "  +_ /\\ _+  ",
            "   /    \\   "
        ]
    },
    {
        "id": "tetris",
        "name": "Tetris",
        "icon": [
            "    [][]    ",
            "  [][][]    ",
            "            ",
            "    [][]    ",
            "    [][]    ",
            "            "
        ]
    },
    {
        "id": "pacman",
        "name": "Pac-Man",
        "icon": [
            "   .-'''-.  ",
            "  /   o   \\ ",
            " |      < o ",
            "  \\       / ",
            "   '-...-'  ",
            "            "
        ]
    },
    {
        "id": "breakout",
        "name": "Breakout",
        "icon": [
            " [#][#][#]  ",
            " [#][#][#]  ",
            "            ",
            "       O    ",
            "            ",
            "   ======   "
        ]
    }
]

def draw_card(stdscr, y, x, h, w, game, is_selected):
    """رسم یک کارت بازی در مختصات و ابعاد مشخص شده"""
    color = curses.color_pair(2) if is_selected else curses.color_pair(1)
    
    for i in range(h):
        for j in range(w):
            if i == 0 or i == h - 1:
                stdscr.addstr(y + i, x + j, "-", color)
            elif j == 0 or j == w - 1:
                stdscr.addstr(y + i, x + j, "|", color)
            else:
                stdscr.addstr(y + i, x + j, " ", color)
    
    stdscr.addstr(y, x, "+", color)
    stdscr.addstr(y, x + w - 1, "+", color)
    stdscr.addstr(y + h - 1, x, "+", color)
    stdscr.addstr(y + h - 1, x + w - 1, "+", color)

    title_x = x + (w - len(game["name"])) // 2
    if title_x > x and title_x + len(game["name"]) < x + w:
        stdscr.addstr(y + 2, title_x, game["name"], color | curses.A_BOLD)

    icon = game["icon"]
    icon_start_y = y + (h - len(icon)) // 2 + 1
    for i, line in enumerate(icon):
        line_x = x + (w - len(line)) // 2
        if line_x > x and line_x + len(line) < x + w:
            stdscr.addstr(icon_start_y + i, line_x, line, color)

def main(stdscr):
    curses.curs_set(0)
    stdscr.timeout(100) 
    curses.start_color()
    
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK) 
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)  
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) 

    selected_index = 0

    while True:
        stdscr.clear()
        term_h, term_w = stdscr.getmaxyx()

        if term_h < 22 or term_w < 65:
            msg = "Terminal is too small! Please enlarge your window."
            stdscr.addstr(term_h // 2, (term_w - len(msg)) // 2, msg, curses.color_pair(1) | curses.A_BLINK)
            stdscr.refresh()
            stdscr.getch()
            continue

        title = "=== TERMINAL ARCADE HUB ==="
        stdscr.addstr(1, (term_w - len(title)) // 2, title, curses.color_pair(3) | curses.A_BOLD)
        subtitle = "Use Arrow Keys to navigate, ENTER to select, 'q' to quit."
        stdscr.addstr(2, (term_w - len(subtitle)) // 2, subtitle, curses.color_pair(1))

        margin_y = 4
        margin_x = 4
        available_h = term_h - margin_y - 2
        available_w = term_w - (margin_x * 2)

        card_h = available_h // 2
        card_w = available_w // 3

        for i, game in enumerate(GAMES):
            row = i // 3
            col = i % 3
            y = margin_y + (row * card_h)
            x = margin_x + (col * card_w)
            draw_card(stdscr, y, x, card_h - 1, card_w - 1, game, selected_index == i)

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_RIGHT:
            if selected_index % 3 < 2: selected_index += 1
        elif key == curses.KEY_LEFT:
            if selected_index % 3 > 0: selected_index -= 1
        elif key == curses.KEY_DOWN:
            if selected_index + 3 < 6: selected_index += 3
        elif key == curses.KEY_UP:
            if selected_index - 3 >= 0: selected_index -= 3
        elif key in [10, 13]: 
            stdscr.clear()
            selected_game = GAMES[selected_index]
            msg = f"Starting {selected_game['name']}..."
            stdscr.addstr(term_h // 2, (term_w - len(msg)) // 2, msg, curses.color_pair(3) | curses.A_BOLD)
            stdscr.refresh()
            time.sleep(1)
            return selected_game['id'] 
        elif key == ord('q') or key == ord('Q'):
            return None 

if __name__ == "__main__":
    while True:
        try:
            selected_game_id = curses.wrapper(main)
        except KeyboardInterrupt:
            break
            
        if selected_game_id is None:
            print("\nThanks for playing! See you next time. 👾\n")
            break
            
        try:
            if selected_game_id == "snake":
                import snake
                curses.wrapper(snake.main)
            elif selected_game_id == "pong":
                import pong
                curses.wrapper(pong.main)
            elif selected_game_id == "invaders":
                import invaders # مطابق با فایل جدید شما
                curses.wrapper(invaders.main)
            elif selected_game_id == "tetris":
                import tetris
                curses.wrapper(tetris.main)
            elif selected_game_id == "pacman":
                import pacman
                curses.wrapper(pacman.main)
            elif selected_game_id == "breakout":
                import breakout
                curses.wrapper(breakout.main)
        except ImportError as e:
            print(f"\n[!] Error: Game file '{selected_game_id}.py' not found! Make sure it's in the same directory.\n")
            time.sleep(2)
        except Exception as e:
            print(f"\n[!] An error occurred: {e}\n")
            time.sleep(2)
