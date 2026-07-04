import curses
import time
import random

def main(stdscr):
    # تنظیمات اولیه
    curses.curs_set(0)
    stdscr.keypad(1) # رفع مشکل گیر کردن کلیدهای جهت‌نما!
    
    # تعریف رنگ‌ها برای آجرهای مختلف
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)    
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK) 
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)   
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)  # توپ و حاشیه
    curses.init_pair(7, curses.COLOR_BLUE, curses.COLOR_BLACK)   # راکت (Paddle)

    sh, sw = stdscr.getmaxyx()
    
    # ابعاد راکت و آجرها
    paddle_w = 15
    paddle_h = 1
    brick_w = 8
    brick_h = 2
    
    # محاسبه تعداد ستون‌های آجری که در صفحه جا می‌شوند
    cols = (sw - 4) // brick_w
    start_x = (sw - (cols * brick_w)) // 2

    while True:
        stdscr.nodelay(1) # بسیار مهم: رفع باگ فریز شدن بازی بعد از ری‌استارت!
        
        # متغیرهای بازی
        paddle_x = sw // 2 - paddle_w // 2
        paddle_y = sh - 3
        
        ball_x = sw // 2
        ball_y = sh - 5
        ball_dx = 1
        ball_dy = -1
        
        lives = 3
        score = 0
        game_over = False
        win = False
        frame_count = 0
        
        bricks = []
        
        # تابع ساخت ردیف آجرهای رندوم
        def spawn_row(y_pos):
            for c in range(cols):
                if random.random() > 0.25: # ۷۵ درصد شانس برای ساخته شدن آجر در هر خانه
                    bricks.append({
                        'y': y_pos, 
                        'x': start_x + c * brick_w, 
                        'w': brick_w - 1, 
                        'color': random.randint(1, 5) # رنگ کاملا تصادفی
                    })
                    
        # ساخت موج اولیه آجرها (4 ردیف)
        for r in range(4):
            spawn_row(4 + r * brick_h)
            
        while not game_over and not win:
            frame_count += 1
            
            # 1. دریافت ورودی (بدون توقف)
            keys = set()
            while True:
                k = stdscr.getch()
                if k == -1: break
                keys.add(k)
                
            if ord('q') in keys or ord('Q') in keys: return
            
            # حرکت راکت به چپ و راست (بسیار روان‌تر از قبل و سریع‌تر)
            if curses.KEY_LEFT in keys or ord('a') in keys or ord('A') in keys:
                paddle_x = max(2, paddle_x - 6) # سرعت حرکت راکت افزایش یافت به 6
            if curses.KEY_RIGHT in keys or ord('d') in keys or ord('D') in keys:
                paddle_x = min(sw - paddle_w - 2, paddle_x + 6)
                
            # 2. منطق سقوط آجرها و تولید از بالا
            # هر 120 فریم آجرها یک پله پایین می‌آیند و ردیف جدید ساخته می‌شود
            if frame_count % 120 == 0:
                for b in bricks:
                    b['y'] += brick_h
                    # اگر آجرها به راکت برسند، بازی تمام است
                    if b['y'] >= paddle_y - 1:
                        game_over = True 
                spawn_row(4) # ساخت ردیف جدید در بالای صفحه
                
            # اگر بازیکن تمام آجرهای صفحه را پاک کرد، فورا موج جدید بده
            if not bricks:
                for r in range(3):
                    spawn_row(4 + r * brick_h)
                
            # 3. حرکت توپ
            ball_x += ball_dx
            ball_y += ball_dy
            
            # برخورد با دیوارهای چپ و راست
            if ball_x <= 1:
                ball_x = 2
                ball_dx *= -1
                try: curses.beep()
                except: pass
            elif ball_x >= sw - 2:
                ball_x = sw - 3
                ball_dx *= -1
                try: curses.beep()
                except: pass
                
            # برخورد با سقف
            if ball_y <= 1:
                ball_y = 2
                ball_dy *= -1
                try: curses.beep()
                except: pass
                
            # افتادن توپ به پایین صفحه (از دست دادن جان)
            elif ball_y >= sh - 1:
                lives -= 1
                try: curses.flash(); curses.beep(); time.sleep(0.1); curses.beep()
                except: pass
                
                if lives <= 0:
                    game_over = True
                else:
                    # ریست کردن جایگاه توپ و راکت
                    ball_x = sw // 2
                    ball_y = paddle_y - 1
                    ball_dy = -1
                    ball_dx = 1 if ball_dx > 0 else -1
                    paddle_x = sw // 2 - paddle_w // 2
                    time.sleep(1) 
                    continue
                    
            # 4. فیزیک برخورد توپ با راکت
            if ball_dy > 0 and int(ball_y) == paddle_y and paddle_x <= ball_x <= paddle_x + paddle_w:
                ball_dy *= -1
                ball_y = paddle_y - 1
                try: curses.beep()
                except: pass
                
                # کنترل زاویه: اگر به گوشه‌ها بخورد زاویه تندتر می‌شود (dx تغییر می‌کند)
                center = paddle_x + paddle_w // 2
                if ball_x < center - 3: ball_dx = -2     # گوشه چپ تند
                elif ball_x < center: ball_dx = -1       # مرکز مایل به چپ
                elif ball_x > center + 3: ball_dx = 2    # گوشه راست تند
                elif ball_x >= center: ball_dx = 1       # مرکز مایل به راست
                
            # 5. برخورد با آجرها
            hit_brick = None
            for b in bricks:
                if b['y'] <= ball_y <= b['y'] + 1 and b['x'] <= ball_x <= b['x'] + b['w']:
                    hit_brick = b
                    break
                    
            if hit_brick:
                bricks.remove(hit_brick)
                score += (6 - hit_brick['color']) * 10 # آجرهای بالاتر امتیاز بیشتر دارند
                ball_dy *= -1 # بازتاب ساده توپ
                try: curses.beep()
                except: pass
                
            # تنظیم دینامیک سرعت بازی: سرعت پایه کمی کمتر شد تا توپ کنترل‌پذیرتر شود
            current_speed = max(0.02, 0.05 - (score // 300) * 0.005)
            time.sleep(current_speed)

            # 6. رسم صفحه
            stdscr.erase()
            
            # رسم حاشیه
            stdscr.attron(curses.color_pair(6))
            stdscr.border(0)
            stdscr.attroff(curses.color_pair(6))
            
            # رسم رابط کاربری
            stdscr.addstr(0, 2, f" SCORE: {score} ", curses.color_pair(3) | curses.A_BOLD)
            stdscr.addstr(0, sw - 15, f" LIVES: {'♥' * lives} ", curses.color_pair(1) | curses.A_BOLD)
            
            # رسم آجرها
            for b in bricks:
                brick_str = "█" * b['w']
                try: stdscr.addstr(b['y'], b['x'], brick_str, curses.color_pair(b['color']))
                except: pass
                
            # رسم راکت
            paddle_str = "▀" * paddle_w
            try: stdscr.addstr(paddle_y, paddle_x, paddle_str, curses.color_pair(7) | curses.A_BOLD)
            except: pass
            
            # رسم توپ
            try: stdscr.addstr(int(ball_y), int(ball_x), "●", curses.color_pair(6) | curses.A_BOLD)
            except: pass
            
            stdscr.refresh()

        # --- پایان بازی ---
        stdscr.nodelay(0)
        stdscr.timeout(-1)
        
        # پاک کردن کادر وسط برای منو
        for i in range(-3, 4):
            stdscr.addstr(sh // 2 + i, (sw - 30) // 2, " " * 30)
            
        msg = " GAME OVER! "
        color = curses.color_pair(1)
            
        stdscr.addstr(sh // 2 - 2, (sw - len(msg)) // 2, msg, color | curses.A_BOLD | curses.A_BLINK)
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
