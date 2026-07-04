import curses
import time
import random

# تعریف قطعات (تترومینوها) به صورت ماتریس‌های 2 بعدی
SHAPES = [
    # I (Cyan)
    ([[1, 1, 1, 1]], 4),
    # J (Blue)
    ([[1, 0, 0], 
      [1, 1, 1]], 7),
    # L (White/Orange)
    ([[0, 0, 1], 
      [1, 1, 1]], 6),
    # O (Yellow)
    ([[1, 1], 
      [1, 1]], 2),
    # S (Green)
    ([[0, 1, 1], 
      [1, 1, 0]], 3),
    # T (Magenta)
    ([[0, 1, 0], 
      [1, 1, 1]], 5),
    # Z (Red)
    ([[1, 1, 0], 
      [0, 1, 1]], 1)
]

def rotate_shape(shape):
    """چرخش 90 درجه‌ای قطعه در جهت عقربه‌های ساعت"""
    return [list(row) for row in zip(*shape[::-1])]

def check_collision(board, shape, offset_y, offset_x):
    """بررسی برخورد قطعه با دیواره‌ها یا بلوک‌های قرار گرفته"""
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                board_y = offset_y + y
                board_x = offset_x + x
                # برخورد با کف یا دیواره‌ها
                if board_y >= 20 or board_x < 0 or board_x >= 10:
                    return True
                # برخورد با سایر بلوک‌ها (فقط اگر داخل صفحه باشد)
                if board_y >= 0 and board[board_y][board_x] != 0:
                    return True
    return False

def main(stdscr):
    # تنظیمات اولیه
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.keypad(1)
    
    # تعریف رنگ‌ها
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)     # Z
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # O
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)   # S
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)    # I
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # T
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)   # L
    curses.init_pair(7, curses.COLOR_BLUE, curses.COLOR_BLACK)    # J
    curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLACK)   # حاشیه‌ها

    sh, sw = stdscr.getmaxyx()
    
    # عرض برد 10 و ارتفاع 20 است (اما عرض رندر شده 20 است چون هر بلوک 2 کاراکتر است '██')
    board_w = 10
    board_h = 20
    offset_x = (sw - (board_w * 2)) // 2
    offset_y = (sh - board_h) // 2

    if sh < board_h + 2 or sw < board_w * 2 + 20:
        stdscr.addstr(0, 0, "Terminal too small! Please resize.")
        stdscr.refresh()
        time.sleep(3)
        return

    while True:
        stdscr.nodelay(1)
        
        # برد بازی: ماتریس 20 در 10 پر از صفر
        board = [[0] * board_w for _ in range(board_h)]
        
        score = 0
        lines_cleared = 0
        level = 1
        
        game_over = False
        
        # گرفتن اولین قطعه
        current_shape, current_color = random.choice(SHAPES)
        current_x = board_w // 2 - len(current_shape[0]) // 2
        current_y = 0
        
        next_shape, next_color = random.choice(SHAPES)
        
        # کنترل سرعت سقوط
        fall_speed = 0.5
        last_fall_time = time.time()
        
        stdscr.timeout(20) # فریم‌ریت بالا برای دریافت سریع کلیدها
        
        while not game_over:
            # 1. دریافت ورودی
            keys = set()
            while True:
                k = stdscr.getch()
                if k == -1: break
                keys.add(k)
                
            if ord('q') in keys or ord('Q') in keys:
                return
                
            # حرکت به چپ
            if curses.KEY_LEFT in keys or ord('a') in keys:
                if not check_collision(board, current_shape, current_y, current_x - 1):
                    current_x -= 1
                    
            # حرکت به راست
            if curses.KEY_RIGHT in keys or ord('d') in keys:
                if not check_collision(board, current_shape, current_y, current_x + 1):
                    current_x += 1
                    
            # چرخش قطعه
            if curses.KEY_UP in keys or ord('w') in keys:
                rotated = rotate_shape(current_shape)
                if not check_collision(board, rotated, current_y, current_x):
                    current_shape = rotated
                    try: curses.beep()
                    except: pass
                    
            # سقوط سریع (Soft Drop)
            if curses.KEY_DOWN in keys or ord('s') in keys:
                if not check_collision(board, current_shape, current_y + 1, current_x):
                    current_y += 1
                    
            # سقوط لحظه‌ای (Hard Drop)
            if ord(' ') in keys:
                while not check_collision(board, current_shape, current_y + 1, current_x):
                    current_y += 1
                last_fall_time = 0 # فوراً قطعه را قفل کن
                
            # 2. منطق سقوط و جاذبه
            current_time = time.time()
            if current_time - last_fall_time > fall_speed:
                if not check_collision(board, current_shape, current_y + 1, current_x):
                    current_y += 1
                else:
                    # قطعه به زمین یا قطعه دیگر خورده است، آن را در برد ذخیره کن
                    for y, row in enumerate(current_shape):
                        for x, cell in enumerate(row):
                            if cell:
                                if current_y + y < 0: # بیرون از صفحه مانده است
                                    game_over = True
                                else:
                                    board[current_y + y][current_x + x] = current_color
                    
                    if game_over: break
                    
                    # بررسی و حذف خطوط پر شده
                    lines_to_clear = []
                    for i in range(board_h):
                        if all(board[i]):
                            lines_to_clear.append(i)
                            
                    if lines_to_clear:
                        # افکت چشمک زدن خطوط پر شده
                        try: curses.flash()
                        except: pass
                        
                        # حذف خطوط و اضافه کردن خطوط خالی به بالا
                        for i in lines_to_clear:
                            del board[i]
                            board.insert(0, [0] * board_w)
                            
                        # محاسبه امتیاز کلاسیک
                        cleared = len(lines_to_clear)
                        lines_cleared += cleared
                        if cleared == 1: score += 100 * level
                        elif cleared == 2: score += 300 * level
                        elif cleared == 3: score += 500 * level
                        elif cleared == 4: score += 800 * level # تترایس!
                        
                        # افزایش سطح و سرعت
                        level = (lines_cleared // 10) + 1
                        fall_speed = max(0.05, 0.5 - (level - 1) * 0.05)
                        
                    # آوردن قطعه بعدی
                    current_shape, current_color = next_shape, next_color
                    next_shape, next_color = random.choice(SHAPES)
                    current_x = board_w // 2 - len(current_shape[0]) // 2
                    current_y = 0
                    
                    # اگر قطعه جدید بلافاصله برخورد کند، بازی تمام است
                    if check_collision(board, current_shape, current_y, current_x):
                        game_over = True
                        
                last_fall_time = current_time

            # 3. رسم صفحه
            stdscr.erase()
            
            # رسم UI (امتیاز و سطح)
            stdscr.addstr(offset_y - 2, offset_x, f" SCORE: {score} ", curses.color_pair(4) | curses.A_BOLD)
            stdscr.addstr(offset_y - 2, offset_x + 12, f" LEVEL: {level} ", curses.color_pair(2) | curses.A_BOLD)
            
            # رسم قطعه بعدی (پیش‌نمایش)
            stdscr.addstr(offset_y + 2, offset_x + 24, "NEXT:", curses.color_pair(8) | curses.A_BOLD)
            for y, row in enumerate(next_shape):
                for x, cell in enumerate(row):
                    if cell:
                        try: stdscr.addstr(offset_y + 4 + y, offset_x + 24 + (x * 2), "██", curses.color_pair(next_color))
                        except: pass
            
            # رسم حاشیه زمین بازی
            for i in range(board_h):
                stdscr.addstr(offset_y + i, offset_x - 2, "<!", curses.color_pair(8))
                stdscr.addstr(offset_y + i, offset_x + board_w * 2, "!>", curses.color_pair(8))
            stdscr.addstr(offset_y + board_h, offset_x - 2, "<!" + "=" * (board_w * 2) + "!>", curses.color_pair(8))
            
            # رسم بلوک‌های ذخیره شده در زمین
            for y in range(board_h):
                for x in range(board_w):
                    if board[y][x] != 0:
                        try: stdscr.addstr(offset_y + y, offset_x + (x * 2), "██", curses.color_pair(board[y][x]))
                        except: pass
                        
            # رسم سایه (محل فرود قطعه فعلی) - Ghost Piece
            ghost_y = current_y
            while not check_collision(board, current_shape, ghost_y + 1, current_x):
                ghost_y += 1
            for y, row in enumerate(current_shape):
                for x, cell in enumerate(row):
                    if cell:
                        try: stdscr.addstr(offset_y + ghost_y + y, offset_x + ((current_x + x) * 2), "▒▒", curses.color_pair(current_color))
                        except: pass
                        
            # رسم قطعه در حال سقوط
            for y, row in enumerate(current_shape):
                for x, cell in enumerate(row):
                    if cell and offset_y + current_y + y >= 0:
                        try: stdscr.addstr(offset_y + current_y + y, offset_x + ((current_x + x) * 2), "██", curses.color_pair(current_color))
                        except: pass
                        
            stdscr.refresh()

        # --- پایان بازی ---
        stdscr.nodelay(0)
        stdscr.timeout(-1)
        
        # منوی باخت
        for i in range(-3, 4):
            stdscr.addstr(sh // 2 + i, (sw - 30) // 2, " " * 30)
            
        msg = " GAME OVER! "
        stdscr.addstr(sh // 2 - 2, (sw - len(msg)) // 2, msg, curses.color_pair(1) | curses.A_BOLD | curses.A_BLINK)
        stdscr.addstr(sh // 2, (sw - 16) // 2, f" FINAL SCORE: {score} ", curses.color_pair(2) | curses.A_BOLD)
        stdscr.addstr(sh // 2 + 1, (sw - 11) // 2, "[R] Restart", curses.color_pair(6) | curses.A_BOLD)
        stdscr.addstr(sh // 2 + 2, (sw - 8) // 2, "[Q] Exit", curses.color_pair(1) | curses.A_BOLD)
        stdscr.refresh()
        
        action = -1
        while action not in [ord('r'), ord('R'), ord('q'), ord('Q')]:
            action = stdscr.getch()
            
        if action in [ord('q'), ord('Q')]:
            break

if __name__ == "__main__":
    curses.wrapper(main)
