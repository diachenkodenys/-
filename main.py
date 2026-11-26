
import os
import time
import json
import glob
import subprocess

import pyautogui as pg
import pyperclip
import psutil
import winocr

import win32gui
import win32con
import win32process


CONFIG_PATH = "config.json"


# =========================
# CONFIG
# =========================

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# DISCORD PATH
# =========================

def find_discord():

    local = os.getenv("LOCALAPPDATA")

    paths = [
        os.path.join(local, "Discord", "Discord.exe"),
        os.path.join(local, "DiscordPTB", "Discord.exe"),
        os.path.join(local, "DiscordCanary", "Discord.exe"),
    ]

    for folder in ["Discord", "DiscordPTB", "DiscordCanary"]:
        paths += glob.glob(
            os.path.join(local, folder, "app-*", "Discord.exe")
        )

    for path in paths:
        if os.path.isfile(path):
            return path

    return None


def find_updater():

    path = os.path.join(
        os.getenv("LOCALAPPDATA"),
        "Discord",
        "Update.exe"
    )

    if os.path.isfile(path):
        return path

    return None


# =========================
# PROCESS CHECK
# =========================

def get_discord_processes():

    processes = []

    for p in psutil.process_iter(["name", "exe", "pid"]):

        try:
            if p.info["name"] and p.info["name"].lower() == "discord.exe":
                processes.append(p)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return processes


# =========================
# WINDOW SEARCH
# =========================

def find_discord_windows():

    windows = []

    def callback(hwnd, _):

        if not win32gui.IsWindow(hwnd):
            return

        if not win32gui.IsWindowVisible(hwnd):
            return

        if win32gui.GetWindow(hwnd, win32con.GW_OWNER):
            return

        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        try:
            p = psutil.Process(pid)

            if p.name().lower() != "discord.exe":
                return

            windows.append(hwnd)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    win32gui.EnumWindows(callback, None)

    return windows


# =========================
# FOCUS WINDOW
# =========================

def force_focus(hwnd):

    if not hwnd:
        return False

    try:

        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        foreground = win32gui.GetForegroundWindow()

        current_thread = win32process.GetWindowThreadProcessId(foreground)[0]
        target_thread = win32process.GetWindowThreadProcessId(hwnd)[0]

        attached = False

        if current_thread != target_thread:

            try:
                win32process.AttachThreadInput(
                    current_thread,
                    target_thread,
                    True
                )
                attached = True

            except Exception:
                pass

        win32gui.BringWindowToTop(hwnd)
        win32gui.SetActiveWindow(hwnd)
        win32gui.SetForegroundWindow(hwnd)

        if attached:

            try:
                win32process.AttachThreadInput(
                    current_thread,
                    target_thread,
                    False
                )

            except Exception:
                pass

        time.sleep(0.15)

        return win32gui.GetForegroundWindow() == hwnd

    except Exception as e:

        print("Focus error:", e)
        return False


def activate_discord():

    windows = find_discord_windows()

    if not windows:
        return False

    for hwnd in windows:

        if force_focus(hwnd):
            print("Discord focused.")
            return True

    return False


# =========================
# START / RESTORE
# =========================

def open_discord():

    discord_path = find_discord()
    updater = find_updater()

    if activate_discord():
        return True, "already_open"

    processes = get_discord_processes()

    if processes:

        print("Discord process exists. Attempting to restore...")

        if discord_path:
            subprocess.Popen([discord_path], shell=False)

        elif updater:
            subprocess.Popen(
                [updater, "--processStart", "Discord.exe"],
                shell=False
            )

        status = "restored"

    else:

        print("Discord is not running. Starting...")

        if discord_path:
            subprocess.Popen([discord_path], shell=False)

        elif updater:
            subprocess.Popen(
                [updater, "--processStart", "Discord.exe"],
                shell=False
            )

        else:
            print("Discord installation not found.")
            return False, "failed"

        status = "fresh_start"

    print("Waiting for Discord window...")

    timeout = 45
    start = time.time()

    while time.time() - start < timeout:

        windows = find_discord_windows()

        if windows:

            for hwnd in windows:

                if force_focus(hwnd):
                    print("Discord window activated.")
                    return True, status

        time.sleep(0.25)

    print("Discord window could not be activated.")
    return False, "failed"


# =========================
# WINDOWS OCR
# =========================

def wait_for_discord_ready(timeout=60):

    print("Waiting for Discord interface using Windows OCR...")

    start = time.time()
    ready_hits = 0

    markers = [
        # English
        "direct messages",
        "friends",
        "nitro",
        "shop",
        "message",

        # German
        "direktnachrichten",
        "freunde",
        "nachrichten",

        # Russian
        "личные сообщения",
        "друзья",

        # Ukrainian
        "особисті повідомлення",
        "друзі",
    ]

    while time.time() - start < timeout:

        windows = find_discord_windows()

        if not windows:
            ready_hits = 0
            time.sleep(0.5)
            continue

        hwnd = windows[0]

        try:

            left, top, right, bottom = win32gui.GetWindowRect(hwnd)

            width = right - left
            height = bottom - top

            if width < 400 or height < 300:
                ready_hits = 0
                time.sleep(0.5)
                continue

            screenshot = pg.screenshot(
                region=(left, top, width, height)
            )

            # Windows built-in OCR
            result = winocr.recognize_pil_sync(screenshot, "en")

            recognized_text = result["text"].lower()

            found = [
                marker for marker in markers
                if marker in recognized_text
            ]

            if found:

                ready_hits += 1
                print("OCR recognized:", found)

            else:

                ready_hits = 0

            # Require two successful checks
            if ready_hits >= 2:

                print("Discord interface is ready!")
                return True

        except Exception as e:

            ready_hits = 0
            print("OCR error:", e)

        time.sleep(0.5)

    print("Discord loading timeout!")
    return False


# =========================
# TEXT
# =========================

def write_unicode(text):

    pyperclip.copy(text)
    time.sleep(0.1)
    pg.hotkey("ctrl", "v")


# =========================
# MAIN
# =========================

def main():

    config = load_config()

    username = config["username"]
    message = config["message"]
    send_automatically = config.get("send_automatically", False)

    success, status = open_discord()

    if not success:
        print("Stopping: Discord was not activated.")
        return

    # OCR ONLY when Discord starts completely from zero
    if status == "fresh_start":

        if not wait_for_discord_ready(timeout=60):
            print("Stopping: Discord interface was not detected.")
            return
        time.sleep(1.3)
    elif status == "restored":

        time.sleep(1)

    else:

        time.sleep(0.3)

    # Focus Discord again
    if not activate_discord():
        print("Could not focus Discord.")
        return

    # Open Quick Switcher
    pg.hotkey("ctrl", "k")
    time.sleep(0.25)

    # Search user
    write_unicode(username)
    time.sleep(0.7)

    # Select result
    pg.press("enter")
    time.sleep(0.4)

    # Paste message
    write_unicode(message)

    if send_automatically:

        pg.press("enter")
        print("Message sent.")

    else:

        print("Message is ready.")

        input("Press Enter to send...")

        pg.press("enter")
        print("Message sent.")


if __name__ == "__main__":
    main()
