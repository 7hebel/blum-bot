from win32gui import FindWindow, GetWindowRect
from PIL import ImageEnhance, ImageOps, Image
from dataclasses import dataclass
import pyautogui as pag
import tkinter as tk
import keyboard
import mouse
import time
import sys


"""
FLAGS:
-t: Test mode (no clicks, only moves mouse)
-r: Repeat after game ended.
-o: No overlay mode.
"""

POINT_COLOR = (0, 255, 0)
WHITE_COLOR = (255, 255, 255)
RED_COLOR = (255, 0, 0)

WIN_SIZE = (384, 420)
REPLAY_BTN = (200, 410)
GAME_END = "end"
JUMPS = 20
NO_OVERLAY_MODE = "-o" in sys.argv

window_handle = FindWindow(None, "TelegramDesktop")
window_rect = GetWindowRect(window_handle)

x_offset = window_rect[0] + 10
y_offset = window_rect[1] + 180
ss_region = (x_offset, y_offset, WIN_SIZE[0], WIN_SIZE[1])

if not NO_OVERLAY_MODE:
    overlay_root = tk.Tk()
    overlay_root.title("BlumBot - Autoclicker")
    overlay_root.geometry(f"{WIN_SIZE[0]+4}x{WIN_SIZE[1] + 234}+{x_offset - 10}+{y_offset - 200}")
    overlay_root.resizable(False, False)
    overlay_root.wm_attributes("-topmost", True)
    overlay_root.wm_attributes('-transparentcolor','#AAA')
    overlay_root.config(bg='#AAA')
    overlay_root.lift()

    def start_btn_callback():
        start_btn.destroy()
        
        stop_info_text = tk.Label(overlay_root, text="Press ESC to stop.", bg="white", fg="black", font=("Aerial", 16, "bold"))
        stop_info_text.pack(pady=10)
        
        overlay_root.update()
    
        start_bot()

    start_btn = tk.Button(overlay_root, text="Start Bot", background="#2dba42", font=("Aerial", 16, 'bold'), fg="white", borderwidth=2, pady=0, padx=12, relief="ridge", command=start_btn_callback)
    start_btn.pack(pady=10)


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
    time.sleep(1.5)


def collect_at(x: int, y: int) -> None:
    x += x_offset
    y += y_offset
    
    if "-t" in sys.argv:
        mouse.move(x, y)
        
    else:
        mouse.move(x, y)
        mouse.click()
        
      
@dataclass
class BombArea:
    x: int
    y: int
    
    def __hash__(self) -> int:
        return hash(f"{self.x}.{self.y}")
    
    def __post_init__(self) -> None:
        self.x += 10
        self.y -= 10
        
        self.x_end = self.x - 28
        self.y_end = self.y + 40
        
        self.xrange = range(self.x_end, self.x)
        self.yrange = range(self.y, self.y_end)
        
    def contains_pos(self, x: int, y: int) -> bool:
        return x in self.xrange and y in self.yrange
    
    def intersects(self, bomb_area: "BombArea") -> bool:
        if self.x == bomb_area.x and self.y == bomb_area.y:
            return True
        
        for bx in bomb_area.xrange:
            for by in bomb_area.yrange:
                if self.contains_pos(bx, by):
                    return True
        
        return False
    

class BombsContainer:
    def __init__(self) -> None:
        self.bombs_pos: set[BombArea] = set()
        
    def add_bomb(self, new_bomb: BombArea) -> None:
        if not self.bombs_pos:
            self.bombs_pos.add(new_bomb)
            return
        
        intersection = None
        for bomb in self.bombs_pos:
            if bomb.intersects(new_bomb):
                intersection = bomb
                break
            
        if intersection is None:
            self.bombs_pos.add(new_bomb)
            return
        
        # Pick right-top-most bomb area.
        x_win, x_lost = (bomb, new_bomb) if bomb.x >= new_bomb.x else (new_bomb, bomb)
        x_diff = x_win.x - x_lost.x
        
        y_win, y_lost = (bomb, new_bomb) if bomb.y <= new_bomb.y else (new_bomb, bomb)
        y_diff = y_lost.y - y_win.y
        
        conflict_winner = x_win if x_diff >= y_diff else y_win
        
        if conflict_winner == new_bomb:
            self.bombs_pos.remove(bomb)
            self.bombs_pos.add(new_bomb)
            
    def is_pos_safe(self, xy: list[int, int]) -> bool:
        x, y = xy
        
        for bomb in self.bombs_pos:
            if bomb.contains_pos(x, y):
                return False
        return True
           
           
def detect_bombs(raw_ss: Image.Image) -> BombsContainer:
    image = ImageOps.posterize(raw_ss, 2)
    c = ImageEnhance.Contrast(image)
    image = c.enhance(5)
    W, H = image.size
    
    bombs = BombsContainer()
    
    for y in range(0, H-1, 2):
        for x in range(0, W-1, 2):
            pos = [x, y]
            px_color = image.getpixel(pos)
            
            if px_color == RED_COLOR:
                bombs.add_bomb(BombArea(x, y))
            
    return bombs
           
def get_locations(n=2) -> list | str:
    locs = []
    image = pag.screenshot(region=ss_region)

    # bombs = detect_bombs(image)

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
                    # locs = list(filter(bombs.is_pos_safe, locs))
                    return locs
    
    return None


def start_bot():
    games_count = 1
    print("Started, press [ESC] to stop.")
    print(f"Playing game: {games_count}")
    
    while not keyboard.is_pressed("esc"):
        locs = get_locations()
        if locs is None:
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

    if not NO_OVERLAY_MODE:
        overlay_root.destroy()


if not NO_OVERLAY_MODE:
    overlay_root.mainloop()

if NO_OVERLAY_MODE:
    print("Start Blum drop game and press [space].")
    print("Waiting for [space] press...")
    while not keyboard.is_pressed("space"):
        pass
    
    start_bot()
    
