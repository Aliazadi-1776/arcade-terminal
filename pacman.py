import curses
import time
import random

# طراحی مپ کلاسیک پک‌من (39 عرض در 20 ارتفاع)
# # = دیوار، . = نقطه، o = قرص قدرت، فاصله خالی = مسیر بدون امتیاز
RAW_MAZE = [
    "#######################################",
    "#..................#..................#",
    "#.####.######.####.#.####.######.####.#",
    "#o####.######.####.#.####.######.####o#",
    "#.....................................#",
    "#.####.#.#####################.#.####.#",
    "#......#...........#...........#......#",
    "######.####### ### # ### #######.######",
    "     #.#       #       #       #.#     ",
    "######.# ##### #### #### ##### #.######", # درِ خانه روح‌ها در وسط این خط است
    ".......  #                   #  .......", # تونل‌های کناری و خانه روح‌ها
    "######.# ##### ######### ##### #.######",
    "     #.#       #       #       #.#     ",
    "######.# ##################### #.######",
    "#..................#..................#",
    "#.####.######.####.#.####.######.####.#",
    "#o...#............. .............#...o#",
    "####.#.#.#####################.#.#.####",
    "#......#...........#...........#......#",
    "#######################################"
]

def main(stdscr):
    # تنظیمات اولیه
    curses.curs_set(0)
    stdscr.nodelay(1)
    
    # تعریف رنگ‌ها
    curses.start_color()
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK) # پک‌من
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # روح 1 (Blinky)
    curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)# روح 2 (Pinky)
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)   # روح 3 (Inky)
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)  # روح 4 (Clyde)
    curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)   # دیوارها
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)  # نقطه‌ها و فریم‌های چشمک‌زن
    curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLUE)   # روح‌های ترسیده

    sh, sw = stdscr.getmaxyx()
    
    maze_h = len(RAW_MAZE)
    maze_w = len(RAW_MAZE[0])
    
    # بررسی اندازه ترمینال (با توجه به ۲ برابر شدن عرض مپ)
    if sh < maze_h + 2 or sw < maze_w * 2 + 2:
        stdscr.addstr(0, 0, "Terminal too small! Please resize (min 80x24).")
        stdscr.refresh()
        time.sleep(3)
        return

    while True:
        # پردازش مپ
        walls = set()
        dots = set()
        pellets = set()
        
        for r, row in enumerate(RAW_MAZE):
            for c, char in enumerate(row):
                if char == '#': walls.add((r, c))
                elif char == '.': dots.add((r, c))
                elif char == 'o': pellets.add((r, c))
                
        # تنظیمات کاراکترها
        pac = {'y': 16, 'x': 19, 'dy': 0, 'dx': 0, 'ndy': 0, 'ndx': 0}
        ghosts = [
            {'y': 10, 'x': 18, 'dy': -1, 'dx': 0, 'color': 2},
            {'y': 10, 'x': 19, 'dy': -1, 'dx': 0, 'color': 3},
            {'y': 10, 'x': 20, 'dy': -1, 'dx': 0, 'color': 4},
            {'y': 9,  'x': 19, 'dy': -1, 'dx': 0, 'color': 5},
        ]
        
        lives = 3
        score = 0
        frightened = 0
        frame_count = 0
        ready_timer = 20 # زمان انتظار در شروع هر جان
        
        game_over = False
        win = False
        
        stdscr.timeout(120) # کاهش سرعت بازی برای کنترل بهتر و واقعی‌تر شدن
        
        while not game_over and not win:
            # 1. دریافت ورودی
            keys = set()
            while True:
                k = stdscr.getch()
                if k == -1: break
                keys.add(k)
                
            if ord('q') in keys or ord('Q') in keys: return
                
            if curses.KEY_UP in keys or ord('w') in keys: pac['ndy'], pac['ndx'] = -1, 0
            if curses.KEY_DOWN in keys or ord('s') in keys: pac['ndy'], pac['ndx'] = 1, 0
            if curses.KEY_LEFT in keys or ord('a') in keys: pac['ndy'], pac['ndx'] = 0, -1
            if curses.KEY_RIGHT in keys or ord('d') in keys: pac['ndy'], pac['ndx'] = 0, 1
            
            frame_count += 1
            if frightened > 0: frightened -= 1

            if ready_timer > 0:
                ready_timer -= 1
            else:
                # 2. حرکت پک‌من
                ny, nx = pac['y'] + pac['ndy'], pac['x'] + pac['ndx']
                # تونل‌های کناری
                if nx < 0: nx = maze_w - 1
                elif nx >= maze_w: nx = 0
                
                # تغییر جهت اگر مانعی نباشد
                if (ny, nx) not in walls:
                    pac['dy'], pac['dx'] = pac['ndy'], pac['ndx']
                    
                ny, nx = pac['y'] + pac['dy'], pac['x'] + pac['dx']
                if nx < 0: nx = maze_w - 1
                elif nx >= maze_w: nx = 0
                
                if (ny, nx) not in walls:
                    pac['y'], pac['x'] = ny, nx
                    
                # بررسی برخورد پیش از حرکت روح‌ها
                dead = False
                for g in ghosts:
                    if g['y'] == pac['y'] and g['x'] == pac['x']:
                        if frightened > 0:
                            score += 200
                            g['y'], g['x'] = 10, 19 # فرستادن روح به خانه
                            try: curses.beep()
                            except: pass
                        else:
                            dead = True
                
                # خوردن نقطه‌ها و قرص‌ها
                pos = (pac['y'], pac['x'])
                if pos in dots:
                    dots.remove(pos)
                    score += 10
                elif pos in pellets:
                    pellets.remove(pos)
                    score += 50
                    frightened = 45 # مدت زمان ترس روح‌ها
                    try: curses.flash()
                    except: pass
                    
                if not dots and not pellets:
                    win = True
                    
                # 3. حرکت روح‌ها
                for g in ghosts:
                    # اگر ترسیده باشند، سرعتشان نصف می‌شود
                    if frightened > 0 and frame_count % 2 == 0:
                        continue
                        
                    valid_moves = []
                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ny, nx = g['y'] + dy, g['x'] + dx
                        if nx < 0: nx = maze_w - 1
                        elif nx >= maze_w: nx = 0
                        
                        if (ny, nx) not in walls:
                            # جلوگیری از برگشت به عقب مگر اینکه بن‌بست باشد
                            if (dy, dx) != (-g['dy'], -g['dx']) or (g['dy'] == 0 and g['dx'] == 0):
                                valid_moves.append((dy, dx))
                    
                    if not valid_moves:
                        valid_moves.append((-g['dy'], -g['dx']))
                        
                    if frightened > 0:
                        best = random.choice(valid_moves)
                    else:
                        # 60 درصد مواقع سعی می‌کنند به سمت پک‌من بروند، 40 درصد رندوم
                        if random.random() < 0.6:
                            best = valid_moves[0]
                            min_dist = 9999
                            for dy, dx in valid_moves:
                                ny, nx = g['y'] + dy, g['x'] + dx
                                dist = abs(ny - pac['y']) + abs(nx - pac['x'])
                                if dist < min_dist:
                                    min_dist = dist
                                    best = (dy, dx)
                        else:
                            best = random.choice(valid_moves)
                            
                    g['dy'], g['dx'] = best
                    g['y'] += g['dy']
                    g['x'] += g['dx']
                    if g['x'] < 0: g['x'] = maze_w - 1
                    elif g['x'] >= maze_w: g['x'] = 0
                    
                # بررسی برخورد پس از حرکت روح‌ها
                for g in ghosts:
                    if g['y'] == pac['y'] and g['x'] == pac['x']:
                        if frightened > 0:
                            score += 200
                            g['y'], g['x'] = 10, 19
                            try: curses.beep()
                            except: pass
                        else:
                            dead = True
                            
                if dead:
                    lives -= 1
                    try: curses.flash(); curses.beep(); time.sleep(0.1); curses.beep()
                    except: pass
                    if lives <= 0:
                        game_over = True
                    else:
                        # ریست کردن جایگاه‌ها برای جان بعدی
                        pac.update({'y': 16, 'x': 19, 'dy': 0, 'dx': 0, 'ndy': 0, 'ndx': 0})
                        ghosts[0].update({'y': 10, 'x': 18, 'dy': -1, 'dx': 0})
                        ghosts[1].update({'y': 10, 'x': 19, 'dy': -1, 'dx': 0})
                        ghosts[2].update({'y': 10, 'x': 20, 'dy': -1, 'dx': 0})
                        ghosts[3].update({'y': 9,  'x': 19, 'dy': -1, 'dx': 0})
                        ready_timer = 20 # فعال کردن دوباره زمان انتظار
                        continue

            # 4. رسم صفحه
            stdscr.erase()
            offset_y = (sh - maze_h) // 2
            offset_x = (sw - (maze_w * 2)) // 2 # مپ با عرض 2 برابر رندر می‌شود
            
            # رسم رابط کاربری
            stdscr.addstr(offset_y - 2, offset_x, f" SCORE: {score} ", curses.color_pair(1) | curses.A_BOLD)
            stdscr.addstr(offset_y - 2, offset_x + 50, f" LIVES: {'♥' * lives} ", curses.color_pair(2) | curses.A_BOLD)
            
            # رسم دیوارها (بلوک‌های توپر و دوتایی)
            for r, c in walls:
                try: stdscr.addstr(offset_y + r, offset_x + (c * 2), "██", curses.color_pair(6))
                except: pass
            
            # رسم نقطه‌ها
            for r, c in dots:
                try: stdscr.addstr(offset_y + r, offset_x + (c * 2), " ·", curses.color_pair(7))
                except: pass
                
            # رسم قرص‌های قدرت
            for r, c in pellets:
                try: stdscr.addstr(offset_y + r, offset_x + (c * 2), " ●", curses.color_pair(7) | curses.A_BOLD | curses.A_BLINK)
                except: pass
                
            # رسم پک‌من (همراه با انیمیشن دهان)
            anim_open = (frame_count % 2 == 0)
            p_str = " O" # حالت دهان بسته
            if anim_open:
                if pac['dx'] == 1: p_str = " C"
                elif pac['dx'] == -1: p_str = " Ɔ" # استفاده از کاراکتر برعکس برای سمت چپ
                elif pac['dy'] == -1: p_str = " U"
                elif pac['dy'] == 1: p_str = " n"
            
            try: stdscr.addstr(offset_y + pac['y'], offset_x + (pac['x'] * 2), p_str, curses.color_pair(1) | curses.A_BOLD)
            except: pass
            
            # رسم روح‌ها (با انیمیشن پاها و اخطار چشمک‌زن وقتی زمان قرص رو به پایان است)
            for g in ghosts:
                if frightened > 0:
                    if frightened < 15 and frame_count % 4 < 2:
                        c = curses.color_pair(7) # فلاش سفید و آبی اخطار دهنده
                    else:
                        c = curses.color_pair(8) # آبی کامل
                    g_str = " W" if frame_count % 2 == 0 else " w"
                else:
                    c = curses.color_pair(g['color'])
                    g_str = " M" if frame_count % 2 == 0 else " m"
                    
                try: stdscr.addstr(offset_y + g['y'], offset_x + (g['x'] * 2), g_str, c | curses.A_BOLD)
                except: pass
                
            # نمایش کلمه READY در زمان انتظار
            if ready_timer > 0:
                try: stdscr.addstr(offset_y + 11, offset_x + 15 * 2, " READY! ", curses.color_pair(1) | curses.A_BOLD)
                except: pass
                
            stdscr.refresh()

        # --- پایان بازی ---
        stdscr.nodelay(0)
        stdscr.timeout(-1)
        
        # ساختن یک کادر منو در وسط صفحه
        for i in range(-3, 4):
            stdscr.addstr(sh // 2 + i, (sw - 30) // 2, " " * 30)
            
        if win:
            msg = " YOU CLEARED THE MAZE! "
            color = curses.color_pair(1)
        else:
            msg = " GAME OVER! "
            color = curses.color_pair(2)
            
        stdscr.addstr(sh // 2 - 2, (sw - len(msg)) // 2, msg, color | curses.A_BOLD | curses.A_BLINK)
        stdscr.addstr(sh // 2, (sw - 16) // 2, f" FINAL SCORE: {score} ", curses.color_pair(7) | curses.A_BOLD)
        stdscr.addstr(sh // 2 + 1, (sw - 11) // 2, "[R] Restart", curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(sh // 2 + 2, (sw - 8) // 2, "[Q] Exit", curses.color_pair(2) | curses.A_BOLD)
        stdscr.refresh()
        
        action = -1
        while action not in [ord('r'), ord('R'), ord('q'), ord('Q')]:
            action = stdscr.getch()
            
        if action in [ord('q'), ord('Q')]:
            break

if __name__ == "__main__":
    curses.wrapper(main)
