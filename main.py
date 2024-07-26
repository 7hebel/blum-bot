from win32gui import FindWindow, GetWindowRect
from PIL import ImageEnhance, ImageOps
import pyautogui as pag
import keyboard
import mouse
import time
import sys

"""
FLAGS:
-t: Test mode (no clicks, only moves mouse)
-r: Repeat after game ended.
"""

POINT_COLOR = (0, 255, 0)
WHITE_COLOR = (255, 255, 255)
RED_COLOR = (255, 0, 0)

WIN_SIZE = (384, 420)
REPLAY_BTN = (200, 410)
GAME_END = "end"
JUMPS = 20

window_handle = FindWindow(None, "TelegramDesktop")
window_rect = GetWindowRect(window_handle)

x_offset = window_rect[0] + 10
y_offset = window_rect[1] + 180
ss_region = (x_offset, y_offset, WIN_SIZE[0], WIN_SIZE[1])


def is_end(image) -> bool:
    W, _ = image.size
    y = 410
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
    time.sleep(1)
    mouse.move(REPLAY_BTN[0] + x_offset, REPLAY_BTN[1] + y_offset)
    mouse.click()


def collect_at(x: int, y: int) -> None:
    x += x_offset
    y += y_offset
    
    if "-t" in sys.argv:
        mouse.move(x, y)
        
    else:
        mouse.move(x, y)
        mouse.click()
        
def color_difference(color1, color2) -> int:
    return sum([abs(component1-component2) for component1, component2 in zip(color1, color2)])
           
def get_locations(n=2) -> list | str:
    locs = []
    image = pag.screenshot(region=ss_region)

    image = ImageOps.posterize(image, 1)
    c = ImageEnhance.Contrast(image)
    image = c.enhance(5)
    
    # image.show()
    # exit()
    
    if is_end(image):
        return GAME_END
    
    W, H = image.size
    
    
    for y in range(0, H, JUMPS):
        for x in range(0, W, JUMPS):
            pos = [x, y]
            px_color = image.getpixel(pos)

            if px_color == POINT_COLOR:
                locs.append((x, y))
                
                if len(locs) >= n:
                    return locs
    
    return None

 
print("Waiting for [space] press...")
while not keyboard.is_pressed("space"):
    pass
 
print("Started...")
games_count = 1
while not keyboard.is_pressed("esc"):
    loc = get_locations()
    if loc is None:
        continue
    
    if loc == GAME_END:
        if "-r" in sys.argv:
            games_count += 1
            print(f"Playing game: {games_count}")
            press_replay()
            continue
            
        else:
            print("(Game end) Repeat mode off (no -r flag) exiting...")
            exit()
    
    for l in loc:
        x, y = l
        collect_at(x, y)
        
print("Manual exit...")
