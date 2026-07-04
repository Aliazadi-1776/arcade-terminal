import curses
import random

def main(stdscr):
    # Initialize basic settings
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)
    
    # Initialize colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Snake color
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)     # Food & Game Over color
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Score text color
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Border color

    sh, sw = stdscr.getmaxyx()
    
    # Outer loop for handling Restart mechanism
    while True:
        stdscr.clear()
        
        # Create game window
        w = curses.newwin(sh, sw, 0, 0)
        w.keypad(1)
        w.timeout(100)
        
        # Draw Border
        w.attron(curses.color_pair(4))
        w.border(0)
        w.attroff(curses.color_pair(4))
        
        # Initial snake position and body
        snk_x = sw // 4
        snk_y = sh // 2
        snake = [
            [snk_y, snk_x],
            [snk_y, snk_x - 1],
            [snk_y, snk_x - 2]
        ]
        
        # Draw initial snake (using solid square '■')
        for part in snake:
            w.addstr(part[0], part[1], "■", curses.color_pair(1) | curses.A_BOLD)
        
        # Initial food position (using star '★')
        food = [sh // 2, sw // 2]
        w.addstr(food[0], food[1], "★", curses.color_pair(2) | curses.A_BOLD)
        
        current_dir = curses.KEY_RIGHT
        score = 0
        game_over = False
        
        # Initial Score display
        w.addstr(0, 2, f" Score: {score} ", curses.color_pair(3) | curses.A_BOLD)
        
        # Main game loop
        while not game_over:
            next_key = w.getch()
            
            # Handle Quit during gameplay
            if next_key == ord('q') or next_key == ord('Q'):
                return # Exit back to Atari Hub
            
            # Prevent snake from reversing into itself
            if next_key != -1:
                if next_key == curses.KEY_UP and current_dir != curses.KEY_DOWN:
                    current_dir = next_key
                elif next_key == curses.KEY_DOWN and current_dir != curses.KEY_UP:
                    current_dir = next_key
                elif next_key == curses.KEY_LEFT and current_dir != curses.KEY_RIGHT:
                    current_dir = next_key
                elif next_key == curses.KEY_RIGHT and current_dir != curses.KEY_LEFT:
                    current_dir = next_key
            
            # Calculate new head position
            new_head = [snake[0][0], snake[0][1]]
            
            if current_dir == curses.KEY_DOWN:
                new_head[0] += 1
            if current_dir == curses.KEY_UP:
                new_head[0] -= 1
            if current_dir == curses.KEY_LEFT:
                new_head[1] -= 1
            if current_dir == curses.KEY_RIGHT:
                new_head[1] += 1
                
            # Check for collision with walls (border) or self
            if (new_head[0] in [0, sh - 1] or 
                new_head[1] in [0, sw - 1] or 
                new_head in snake):
                game_over = True
                break
                
            snake.insert(0, new_head)
            
            # Check if food is eaten
            if snake[0] == food:
                score += 1
                food = None
                # Spawn new food inside the border
                while food is None:
                    nf = [
                        random.randint(1, sh - 2),
                        random.randint(1, sw - 2)
                    ]
                    food = nf if nf not in snake else None
                w.addstr(food[0], food[1], "★", curses.color_pair(2) | curses.A_BOLD)
                # Update Score
                w.addstr(0, 2, f" Score: {score} ", curses.color_pair(3) | curses.A_BOLD)
            else:
                # Move snake (erase tail)
                tail = snake.pop()
                w.addstr(tail[0], tail[1], ' ')
                
            # Draw new head (using solid square '■')
            try:
                w.addstr(snake[0][0], snake[0][1], "■", curses.color_pair(1) | curses.A_BOLD)
            except curses.error:
                pass
            
        # --- Game Over State ---
        w.nodelay(0) # Disable nodelay to wait for user input
        
        msg_over = " GAME OVER! "
        msg_score = f" Final Score: {score} "
        menu_restart = "[R] Restart"
        menu_exit = "[Q] Exit"
        
        # Clear a box in the middle for the menu so it doesn't overlap with the snake
        for i in range(-3, 4):
            w.addstr(sh // 2 + i, (sw - 20) // 2, " " * 20)
            
        # Draw Game Over Menu
        w.addstr(sh // 2 - 2, (sw - len(msg_over)) // 2, msg_over, curses.color_pair(2) | curses.A_BOLD | curses.A_BLINK)
        w.addstr(sh // 2 - 1, (sw - len(msg_score)) // 2, msg_score, curses.color_pair(3) | curses.A_BOLD)
        w.addstr(sh // 2 + 1, (sw - len(menu_restart)) // 2, menu_restart, curses.color_pair(1) | curses.A_BOLD)
        w.addstr(sh // 2 + 2, (sw - len(menu_exit)) // 2, menu_exit, curses.color_pair(4) | curses.A_BOLD)
        w.refresh()
        
        # Wait for valid user choice (Restart or Exit)
        action = -1
        while action not in [ord('r'), ord('R'), ord('q'), ord('Q')]:
            action = w.getch()
            
        if action in [ord('q'), ord('Q')]:
            break # Break the outer loop and return to Atari Hub

if __name__ == "__main__":
    curses.wrapper(main)
