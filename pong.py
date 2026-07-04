import curses
import time

def main(stdscr):
    # تنظیمات اولیه
    curses.curs_set(0)
    stdscr.nodelay(1)
    
    # تعریف رنگ‌ها
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)    # بازیکن 1 (چپ)
    curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # بازیکن 2 / هوش مصنوعی (راست)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # توپ و متون منو
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)   # حاشیه و تور
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)   # امتیازها
    
    sh, sw = stdscr.getmaxyx()
    
    # حلقه اصلی برای ری‌استارت کردن بازی
    while True:
        w = curses.newwin(sh, sw, 0, 0)
        w.keypad(1)
        
        mode = 1
        target_score = 5
        
        # --- فاز منوی تنظیمات قبل از بازی ---
        w.timeout(-1) 
        menu_step = 0
        current_selection = 0
        
        options_mode = ["1 Player (vs AI)", "2 Players (Local)"]
        options_score = [5, 10, 15]
        
        while menu_step < 2:
            w.erase()
            w.attron(curses.color_pair(4))
            w.border(0)
            w.attroff(curses.color_pair(4))
            
            if menu_step == 0:
                title = " SELECT GAME MODE "
                opts = options_mode
                footer = "P1: W/S   |   P2: Up/Down"
            else:
                title = " SELECT TARGET SCORE "
                opts = [f"{s} Goals" for s in options_score]
                footer = ""
                
            w.addstr(sh // 2 - 4, (sw - len(title)) // 2, title, curses.color_pair(3) | curses.A_BOLD)
            
            for idx, opt in enumerate(opts):
                color = curses.color_pair(1) | curses.A_REVERSE if idx == current_selection else curses.color_pair(4)
                w.addstr(sh // 2 - 1 + idx * 2, (sw - len(opt)) // 2, opt, color)
                
            if footer:
                w.addstr(sh - 3, (sw - len(footer)) // 2, footer, curses.color_pair(5))
                
            w.refresh()
            
            key = w.getch()
            if key in [ord('q'), ord('Q')]:
                return 
            elif key == curses.KEY_UP and current_selection > 0:
                current_selection -= 1
            elif key == curses.KEY_DOWN and current_selection < len(opts) - 1:
                current_selection += 1
            elif key in [10, 13]: 
                if menu_step == 0:
                    mode = 1 if current_selection == 0 else 2
                    menu_step += 1
                    current_selection = 0 
                elif menu_step == 1:
                    target_score = options_score[current_selection]
                    menu_step += 1

        w.nodelay(1) 
        
        pad_h = 5
        p1_y = sh // 2 - pad_h // 2
        p1_x = 4
        p2_y = sh // 2 - pad_h // 2
        p2_x = sw - 5
        
        ball_y = sh // 2
        ball_x = sw // 2
        ball_dy = 1
        ball_dx = 1
        
        score1 = 0
        score2 = 0
        
        game_over = False
        winner_msg = ""
        
        # --- حلقه اصلی مسابقه ---
        while not game_over:
            w.erase()
            
            w.attron(curses.color_pair(4))
            w.border(0)
            for i in range(1, sh - 1):
                if i % 2 == 1:
                    w.addch(i, sw // 2, '|')
            w.attroff(curses.color_pair(4))
            
            w.addstr(1, sw // 4, f" {score1} ", curses.color_pair(5) | curses.A_BOLD)
            w.addstr(1, sw * 3 // 4, f" {score2} ", curses.color_pair(5) | curses.A_BOLD)
            
            for i in range(pad_h):
                try: w.addstr(int(p1_y) + i, p1_x, "█", curses.color_pair(1))
                except curses.error: pass
            
            for i in range(pad_h):
                try: w.addstr(int(p2_y) + i, p2_x, "█", curses.color_pair(2))
                except curses.error: pass
                
            try: w.addstr(int(ball_y), int(ball_x), "●", curses.color_pair(3) | curses.A_BOLD)
            except curses.error: pass
                
            keys_pressed = set()
            while True:
                k = w.getch()
                if k == -1: break
                keys_pressed.add(k)
            
            if ord('q') in keys_pressed or ord('Q') in keys_pressed:
                return 
                
            # حرکت بازیکن 1 - اصلاح شده برای پشتیبانی از حالت‌های مختلف
            up_keys = {ord('w'), ord('W'), curses.KEY_UP}
            down_keys = {ord('s'), ord('S'), curses.KEY_DOWN}
            
            # در حالت 1 نفره، هم جهت‌نما و هم W/S برای بازیکن 1 کار می‌کنند
            # در حالت 2 نفره، بازیکن 1 فقط با W/S و بازیکن 2 با جهت‌نما کار می‌کند
            if mode == 1:
                if any(k in keys_pressed for k in up_keys): p1_y = max(1, p1_y - 3)
                if any(k in keys_pressed for k in down_keys): p1_y = min(sh - pad_h - 1, p1_y + 3)
            else:
                if ord('w') in keys_pressed or ord('W') in keys_pressed: p1_y = max(1, p1_y - 3)
                if ord('s') in keys_pressed or ord('S') in keys_pressed: p1_y = min(sh - pad_h - 1, p1_y + 3)
                if curses.KEY_UP in keys_pressed: p2_y = max(1, p2_y - 3)
                if curses.KEY_DOWN in keys_pressed: p2_y = min(sh - pad_h - 1, p2_y + 3)
            
            if mode == 1:
                if ball_dx > 0: 
                    center_p2 = p2_y + pad_h // 2
                    if center_p2 < ball_y and p2_y < sh - pad_h - 1: p2_y += 1
                    elif center_p2 > ball_y and p2_y > 1: p2_y -= 1
            
            ball_y += ball_dy
            ball_x += ball_dx
            
            if ball_y <= 1: ball_y = 1; ball_dy *= -1
            elif ball_y >= sh - 2: ball_y = sh - 2; ball_dy *= -1
                
            if ball_dx < 0 and p1_x <= ball_x <= p1_x + 1:
                if p1_y <= ball_y <= p1_y + pad_h - 1:
                    ball_dx *= -1; ball_x = p1_x + 2 
            
            if ball_dx > 0 and p2_x - 1 <= ball_x <= p2_x:
                if p2_y <= ball_y <= p2_y + pad_h - 1:
                    ball_dx *= -1; ball_x = p2_x - 2 
            
            if ball_x <= 0: 
                score2 += 1; ball_y, ball_x = sh // 2, sw // 2; ball_dx = 1; time.sleep(0.5) 
            elif ball_x >= sw - 1: 
                score1 += 1; ball_y, ball_x = sh // 2, sw // 2; ball_dx = -1; time.sleep(0.5)
                
            if score1 >= target_score: winner_msg = " PLAYER 1 WINS! " if mode == 2 else " YOU WIN! "; game_over = True
            elif score2 >= target_score: winner_msg = " PLAYER 2 WINS! " if mode == 2 else " AI WINS! "; game_over = True
                
            time.sleep(0.055)
            
        w.nodelay(0) 
        
        for i in range(-3, 4): w.addstr(sh // 2 + i, (sw - 20) // 2, " " * 20)
            
        w.addstr(sh // 2 - 2, (sw - len(winner_msg)) // 2, winner_msg, curses.color_pair(3) | curses.A_BOLD | curses.A_BLINK)
        w.addstr(sh // 2, (sw - 11) // 2, "[R] Restart", curses.color_pair(1) | curses.A_BOLD)
        w.addstr(sh // 2 + 1, (sw - 8) // 2, "[Q] Exit", curses.color_pair(2) | curses.A_BOLD)
        w.refresh()
        
        action = -1
        while action not in [ord('r'), ord('R'), ord('q'), ord('Q')]: action = w.getch()
            
        if action in [ord('q'), ord('Q')]: break 

if __name__ == "__main__":
    curses.wrapper(main)
