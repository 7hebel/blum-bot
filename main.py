from win32gui import FindWindow, GetWindowRect
from PIL import ImageEnhance, ImageOps
from collections import deque
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

POINT_COLORS = ((255, 0, 0), (255, 255, 255))
WHITE_COLOR = (255, 255, 255)

WIN_SIZE = calc_win_size(window_rect)
GAME_END = "end"
JUMPS = 30
TEST_MODE = "-t" in sys.argv

x_offset = int(window_rect[0] * 1.02)
y_offset = int(window_rect[1] * 1.7)
ss_region = (x_offset, y_offset, int(WIN_SIZE[0] / 1.1), int(WIN_SIZE[1] / 1.4))

def is_end(image) -> bool:
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

def press_replay():
    time.sleep(0.5)
    mouse.move(200 + x_offset, ss_region[3] - 1 + y_offset)

    if not TEST_MODE:
        mouse.click()

    time.sleep(1)

def collect_at(x: int, y: int) -> None:
    x += x_offset
    y += y_offset
    
    mouse.move(x, y)
        
    if not TEST_MODE:
        mouse.click()

def get_locations(n=2) -> list | str:
    locs = []
    image = pag.screenshot(region=ss_region)

    image = ImageOps.posterize(image, 1)
    c = ImageEnhance.Contrast(image)
    image = c.enhance(5)
    
    if is_end(image):
        return GAME_END
    
    W, H = image.size
    
    for y in range(0, H, JUMPS):
        for x in range(0, W, JUMPS):
            px_color = image.getpixel([x, y])

            if px_color in POINT_COLORS:
                locs.append((x, y))
                
                if len(locs) >= n:
                    return locs
    
    return locs


def start_bot():
    games_count = 1
    print("Started, hold [ESC] to stop.")
    print(f"Playing game: {games_count}")
    
    while not keyboard.is_pressed("esc"):
        locs = get_locations()
        if not locs:
            continue
        
        if locs == GAME_END:
            if "-r" in sys.argv:
                games_count += 1
                print(f"Playing game: {games_count}")
                press_replay()
                continue
                
            else:
                print("(Game end) Repeat mode off (no -r flag) exiting...")
                exit()
        
        for location in locs:
            x, y = location
            collect_at(x, y)
            
    print("\n\nManual exit...")

print("Start Blum drop game and press [space].")
print("Waiting for [space] press...")
while not keyboard.is_pressed("space"):
    pass

start_bot()
    
