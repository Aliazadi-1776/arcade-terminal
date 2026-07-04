import curses
import time
import random

def main(stdscr):
    # تنظیمات اولیه
    curses.curs_set(0)
    stdscr.nodelay(1)
    
    # تعریف رنگ‌ها
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # بازیکن
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # دشمنان و جان‌ها
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # تیرها و امتیاز
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)   # حاشیه
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)# رنگ مخصوص باس

    sh, sw = stdscr.getmaxyx()

    # طراحی‌های جدید پیکسلی (ASCII Art پیشرفته)
    player_art = [
        "  ▲  ",
        " ▄█▄ ",
        " ▀▀▀ "
    ]
    
    enemy_art = [
        "▄██▄",
        " ▀▀ "
    ]
    
    boss_art = [
        "  ▄██████████▄  ",
        " ██████████████ ",
        " ██▀▀▀▀▀▀▀▀▀▀██ ",
        " ▀            ▀ "
    ]

    while True:
        # متغیرهای بازی
        player_x = sw // 2
        player_y = sh - 4
        lives = 3
        score = 0
        wave = 1
        
        player_bullets = []
        enemy_bullets = []
        
        enemies = []
        enemy_dir = 1
        enemy_speed = 15 
        frame_count = 0
        
        # متغیرهای مربوط به باس
        boss_active = False
        bosses_defeated = 0
        boss = {"x": 0, "y": 2, "hp": 0, "max_hp": 0, "dir": 1, "width": 16}
        
        def spawn_wave():
            enemies.clear()
            # 4 ردیف در 8 ستون دشمن ایجاد می‌کنیم تا در صفحه جا بشوند
            for row in range(4):
                for col in range(8):
                    enemies.append([2 + row * 3, 5 + col * 6])
                    
        def spawn_boss(level):
            nonlocal boss_active
            boss_active = True
            boss["x"] = sw // 2 - boss["width"] // 2
            boss["y"] = 2
            boss["dir"] = 1
            if level == 1:
                boss["hp"] = 50
                boss["max_hp"] = 50
            elif level == 2:
                boss["hp"] = 150
                boss["max_hp"] = 150
            elif level == 3:
                boss["hp"] = 300
                boss["max_hp"] = 300
            enemies.clear() # وقتی باس می‌آید، دشمنان عادی ناپدید می‌شوند
            try: curses.flash(); curses.beep() # افکت ورود باس
            except: pass

        spawn_wave() # ایجاد اولین موج دشمنان
        
        game_over = False
        win = False
        msg = ""

        # تنظیم سرعت فریم بازی - این تنظیم نقش اساسی در رفع لگ دارد
        stdscr.timeout(30) 
        
        # --- حلقه گیم‌پلی ---
        while not game_over and not win:
            
            # --- 1. دریافت ورودی کاربر (اول دریافت کلیدها برای جلوگیری از پرش تصویر) ---
            keys_pressed = set()
            while True:
                k = stdscr.getch()
                if k == -1: break
                keys_pressed.add(k)
                
            if ord('q') in keys_pressed or ord('Q') in keys_pressed:
                return # خروج از بازی به هاب

            # حرکت بازیکن
            if curses.KEY_LEFT in keys_pressed or ord('a') in keys_pressed or ord('A') in keys_pressed:
                player_x = max(2, player_x - 3)
            if curses.KEY_RIGHT in keys_pressed or ord('d') in keys_pressed or ord('D') in keys_pressed:
                player_x = min(sw - 7, player_x + 3)
                
            # شلیک بازیکن (محدودیت 5 تیر همزمان)
            if ord(' ') in keys_pressed:
                if len(player_bullets) < 5:
                    player_bullets.append([player_y - 1, player_x + 2])
                    try: curses.beep() # صدای تیراندازی
                    except: pass

            # --- 2. بروزرسانی منطق بازی ---
            frame_count += 1
            
            # سیستم بررسی و اسپاون باس
            if score >= 1500 and bosses_defeated == 0 and not boss_active: spawn_boss(1)
            elif score >= 10000 and bosses_defeated == 1 and not boss_active: spawn_boss(2)
            elif score >= 15000 and bosses_defeated == 2 and not boss_active: spawn_boss(3)
            elif len(enemies) == 0 and not boss_active:
                wave += 1
                lives += 1 # هر موج جدید یک جان اضافه می‌شود
                spawn_wave()
                
            # منطق حرکت دشمنان عادی
            if not boss_active and frame_count % enemy_speed == 0:
                hit_edge = False
                for ey, ex in enemies:
                    if (enemy_dir == 1 and ex >= sw - 6) or (enemy_dir == -1 and ex <= 3):
                        hit_edge = True
                        break
                
                if hit_edge:
                    enemy_dir *= -1
                    for e in enemies:
                        e[0] += 1
                        if e[0] >= player_y: 
                            game_over = True
                else:
                    for e in enemies:
                        e[1] += enemy_dir

                if enemies and random.random() < 0.3:
                    shooter = random.choice(enemies)
                    enemy_bullets.append([shooter[0] + 2, shooter[1] + 2])
                    
                if len(enemies) < 5: enemy_speed = 3
                elif len(enemies) < 15: enemy_speed = 6
                elif len(enemies) < 30: enemy_speed = 9
                else: enemy_speed = 12

            # منطق حرکت باس
            if boss_active:
                if frame_count % 3 == 0: # سرعت باس
                    boss["x"] += boss["dir"]
                    if boss["x"] <= 2 or boss["x"] >= sw - boss["width"] - 2:
                        boss["dir"] *= -1
                
                # شلیک رگباری باس
                if random.random() < 0.15:
                    enemy_bullets.append([boss["y"] + 4, boss["x"] + 2])
                    enemy_bullets.append([boss["y"] + 4, boss["x"] + boss["width"] - 3])
                    if boss["hp"] < boss["max_hp"] // 2: # فاز خشم باس
                        enemy_bullets.append([boss["y"] + 4, boss["x"] + boss["width"] // 2])

            # حرکت و برخورد تیرهای بازیکن
            for pb in player_bullets[:]:
                pb[0] -= 1
                if pb[0] <= 0:
                    player_bullets.remove(pb)
                    continue
                
                hit = False
                if boss_active:
                    # برخورد با باس
                    if boss["y"] <= pb[0] <= boss["y"] + 3 and boss["x"] <= pb[1] <= boss["x"] + boss["width"]:
                        boss["hp"] -= 1
                        score += 5
                        player_bullets.remove(pb)
                        hit = True
                        if boss["hp"] <= 0:
                            boss_active = False
                            bosses_defeated += 1
                            score += boss["max_hp"] * 10 # جایزه کشتن باس
                            lives += 2 # اضافه شدن 2 جان با کشتن باس
                            try: curses.flash()
                            except: pass
                            if bosses_defeated >= 3:
                                win = True
                else:
                    # برخورد با دشمن عادی
                    for e in enemies[:]:
                        if e[0] <= pb[0] <= e[0] + 1 and e[1] <= pb[1] <= e[1] + 3:
                            enemies.remove(e)
                            player_bullets.remove(pb)
                            score += 10
                            hit = True
                            break
                if hit: continue
            
            # حرکت و برخورد تیرهای دشمنان
            for eb in enemy_bullets[:]:
                eb[0] += 1
                if eb[0] >= sh - 1:
                    enemy_bullets.remove(eb)
                    continue
                    
                # برخورد با بازیکن
                if player_y <= eb[0] <= player_y + 2 and player_x <= eb[1] <= player_x + 4:
                    enemy_bullets.remove(eb)
                    lives -= 1
                    try: curses.flash(); curses.beep() # فلش و بوق هنگام تیر خوردن
                    except: pass
                    if lives <= 0:
                        game_over = True

            # --- 3. رسم صفحه (Erase و Draw در یک فریم باعث از بین رفتن پرش می‌شود) ---
            stdscr.erase()
            
            # رسم حاشیه و UI
            stdscr.attron(curses.color_pair(4))
            stdscr.border(0)
            stdscr.attroff(curses.color_pair(4))
            
            stdscr.addstr(0, 2, f" SCORE: {score} | WAVE: {wave} ", curses.color_pair(3) | curses.A_BOLD)
            stdscr.addstr(0, sw - 15, f" LIVES: {'♥' * lives} ", curses.color_pair(2) | curses.A_BOLD)

            if boss_active:
                hp_bar = f" BOSS HP: {boss['hp']}/{boss['max_hp']} "
                stdscr.addstr(0, (sw - len(hp_bar)) // 2, hp_bar, curses.color_pair(5) | curses.A_REVERSE | curses.A_BOLD)

            # رسم بازیکن (آرت 3 خطی)
            for i, line in enumerate(player_art):
                try: stdscr.addstr(player_y + i, player_x, line, curses.color_pair(1) | curses.A_BOLD)
                except: pass
            
            # رسم دشمنان (آرت 2 خطی)
            for ey, ex in enemies:
                for i, line in enumerate(enemy_art):
                    try: stdscr.addstr(ey + i, ex, line, curses.color_pair(2) | curses.A_BOLD)
                    except: pass
                    
            # رسم باس (آرت 4 خطی)
            if boss_active:
                for i, line in enumerate(boss_art):
                    try: stdscr.addstr(boss["y"] + i, boss["x"], line, curses.color_pair(5) | curses.A_BOLD)
                    except: pass
                
            # رسم تیرهای بازیکن
            for py, px in player_bullets:
                try: stdscr.addstr(py, px, "┃", curses.color_pair(3) | curses.A_BOLD)
                except: pass
                
            # رسم تیرهای دشمنان
            for ey, ex in enemy_bullets:
                try: stdscr.addstr(ey, ex, "▼", curses.color_pair(2) | curses.A_BOLD)
                except: pass

            # نمایش تغییرات به صورت یکپارچه
            stdscr.refresh()

        # --- فاز پایان بازی ---
        stdscr.nodelay(0)
        stdscr.timeout(-1)
        
        try: curses.flash(); curses.beep(); time.sleep(0.1); curses.beep() # صدای پایان بازی
        except: pass
        
        for i in range(-4, 5):
            stdscr.addstr(sh // 2 + i, (sw - 34) // 2, " " * 34)
            
        if win:
            msg = " YOU SAVED THE GALAXY! "
            color = curses.color_pair(1)
        else:
            msg = " GAME OVER! EARTH IS DOOMED! "
            color = curses.color_pair(2)
            
        stdscr.addstr(sh // 2 - 2, (sw - len(msg)) // 2, msg, color | curses.A_BOLD | curses.A_BLINK)
        stdscr.addstr(sh // 2, (sw - 16) // 2, f" FINAL SCORE: {score} ", curses.color_pair(3) | curses.A_BOLD)
        stdscr.addstr(sh // 2 + 2, (sw - 11) // 2, "[R] Restart", curses.color_pair(4) | curses.A_BOLD)
        stdscr.addstr(sh // 2 + 3, (sw - 8) // 2, "[Q] Exit", curses.color_pair(4) | curses.A_BOLD)
        stdscr.refresh()
        
        action = -1
        while action not in [ord('r'), ord('R'), ord('q'), ord('Q')]:
            action = stdscr.getch()
            
        if action in [ord('q'), ord('Q')]:
            break

if __name__ == "__main__":
    curses.wrapper(main)
