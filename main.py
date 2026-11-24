import time

import pyautogui as pg
import pyperclip

#pg.moveTo(200,315) first in discord
time.sleep(2)
def write_unicode(text):
    """
    Writes Unicode text (e.g., Ukrainian) using clipboard paste.
    Works across platforms.
    """
    try:
        # Copy text to clipboard
        pyperclip.copy(text)

        # Small delay to ensure clipboard is ready
        time.sleep(0.1)

        # Paste using Ctrl+V (Windows/Linux) or Command+V (macOS)
        if pg.platform.system() == "Darwin":  # macOS
            pg.hotkey('command', 'v')
        else:  # Windows/Linux
            pg.hotkey('ctrl', 'v')
    except Exception as e:
        print(f"Error writing text: {e}")
"""pg.moveTo(1510,30)
pg.leftClick()
print("gey")
pg.moveTo(950,565)
pg.leftClick()
pg.moveTo(1510,30)
pg.leftClick()"""

pg.moveTo(500,930)#тут координати дс на робочем столе
pg.leftClick()
pg.leftClick()

time.sleep(6)#время чтоб дс открился при старте
pg.moveTo(200,315)
time.sleep(0.5)
pg.leftClick()
pg.moveTo(800,900)
time.sleep(0.2)
write_unicode("Сука") #тут любой текст
pg.press(keys="enter")
