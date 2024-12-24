from win32gui import FindWindow, GetWindowRect
import pyautogui as pag
import threading
import keyboard
import mouse
import time
import sys

"""
FLAGS:
-t: Test mode (no clicks, only moves mouse)
-r: Repeat after game ended.
"""

def calc_win_size(rect: list[int, int, int, int]) -> list[int, int]:
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    return [int(w / 1.04), int(h / 1.06)]

try:
    window_handle = FindWindow(None, "TelegramDesktop")
    window_rect = GetWindowRect(window_handle)
except:
    print("Telegram window not found.")
    exit()

WHITE_COLOR = (255, 255, 255)
WAIT = 0

WIN_SIZE = calc_win_size(window_rect)
GAME_END = "end"
JUMPS = 20
TEST_MODE = "-t" in sys.argv

x_start = int(window_rect[0] * 1.02)
x_end = int((x_start + (window_rect[2] - window_rect[0])) * 0.97)
Y_LEVEL = window_rect[3] // 1.5

y_offset = int(window_rect[1] * 1.7)
end_ss_region = (x_start, window_rect[3] - 130, int(WIN_SIZE[0] / 1.1), 10)


SUPRESS_CLICK = False


def is_end() -> bool:
    image = pag.screenshot(region=end_ss_region)
    
    W, H = image.size
    y = H - 1
    w_count = 0
    
    for x in range(0, W, 50):
        pos = [x, y]
        px_color = image.getpixel(pos)
        if px_color == WHITE_COLOR:
            w_count += 1
            if w_count > 3:
                return True
            
    return False

def end_checker():
    global SUPRESS_CLICK

    while True:
        time.sleep(0.1)
        if is_end():
            # print("end")
            SUPRESS_CLICK = True


def press_replay():
    time.sleep(0.5)
    mouse.move(250 + x_start, window_rect[3] - 130)

    if not TEST_MODE:
        mouse.click()

    time.sleep(0.5)


def start_bot():
    global SUPRESS_CLICK
    
    games_count = 1
    print("Started, hold [ESC] to stop.")
    print(f"Playing game: {games_count}")
    
    while not keyboard.is_pressed("esc"):
        for x in range(x_start, x_end, JUMPS):
            if not SUPRESS_CLICK:
                time.sleep(WAIT)
                mouse.move(x, Y_LEVEL)
                mouse.click()

        if SUPRESS_CLICK:
            SUPRESS_CLICK = False

            if "-r" in sys.argv:
                games_count += 1
                # print(f"Playing game: {games_count}")
                press_replay()
                
            else:
                print("(Game end) Repeat mode off (no -r flag) exiting...")
                exit()
                
            
    print("\n\nManual exit...")


print("Start Blum drop game and press [space].")
print("Waiting for [space] press...")
checker_th = threading.Thread(target=end_checker, daemon=True)

while not keyboard.is_pressed("space"):
    pass

checker_th.start()
start_bot()
    
