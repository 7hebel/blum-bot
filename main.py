from win32gui import FindWindow, GetWindowRect
from PIL import ImageEnhance, ImageOps, Image
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
MIN_NEIGHBOUR_COLORS = 4
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
        
     
def check_neighbours(x: int, y: int, image) -> bool:
    neighbour_pos = [
        [x-1, y-1],
        [x, y-1],
        [x+1, y-1],
        [x+1, y],
        [x+1, y+1],
        [x, y+1],
        [x-1, y+1],
        [x-1, y]
    ]
    
    correct = 0
    
    for pos in neighbour_pos:
        if image.getpixel(pos) == POINT_COLOR:
            correct += 1
            
    return correct >= MIN_NEIGHBOUR_COLORS
          
        
def get_locations(n=2) -> list | str:
    locs = []
    image = pag.screenshot(region=ss_region)

    image = ImageOps.posterize(image, 1)
    c = ImageEnhance.Contrast(image)
    image = c.enhance(5)
    
    # image.show()
    # exit()
    image.save("x.png")
    
    if is_end(image):
        return GAME_END
    
    W, H = image.size
    
    for y in range(0, H, JUMPS):
        for x in range(0, W, JUMPS):
            pos = [x, y]
            px_color = image.getpixel(pos)

            if px_color == POINT_COLOR:
                neighbours_status = check_neighbours(x, y, image)
                if not neighbours_status:
                    continue
                
                locs.append((x, y))
                
                if len(locs) >= n:
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
    
