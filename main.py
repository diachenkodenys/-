import os
import time
import json
import glob
import subprocess

import pyautogui as pg
import pyperclip


# =========================
# CONFIG
# =========================

CONFIG_PATH = "config.json"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


# =========================
# FIND DISCORD
# =========================

def find_discord():

    local_appdata = os.getenv("LOCALAPPDATA")

    if not local_appdata:
        raise RuntimeError("LOCALAPPDATA not found")

    # Direct executable paths
    paths = [
        os.path.join(local_appdata, "Discord", "Discord.exe"),
        os.path.join(local_appdata, "DiscordCanary", "Discord.exe"),
        os.path.join(local_appdata, "DiscordPTB", "Discord.exe"),
    ]

    # Search version folders
    paths.extend(
        glob.glob(
            os.path.join(local_appdata, "Discord", "app-*", "Discord.exe")
        )
    )

    paths.extend(
        glob.glob(
            os.path.join(local_appdata, "DiscordPTB", "app-*", "Discord.exe")
        )
    )

    paths.extend(
        glob.glob(
            os.path.join(local_appdata, "DiscordCanary", "app-*", "Discord.exe")
        )
    )

    for path in paths:
        if os.path.isfile(path):
            return path

    return None


# =========================
# START DISCORD
# =========================

def start_discord():

    discord_path = find_discord()

    if discord_path:

        print(f"Found Discord: {discord_path}")

        subprocess.Popen(
            [discord_path],
            shell=False
        )

        return True

    # Fallback: Discord updater
    updater = os.path.join(
        os.getenv("LOCALAPPDATA"),
        "Discord",
        "Update.exe"
    )

    if os.path.isfile(updater):

        subprocess.Popen(
            [updater, "--processStart", "Discord.exe"],
            shell=False
        )

        return True

    print("Discord executable not found!")
    return False


# =========================
# WRITE UNICODE
# =========================

def write_unicode(text):

    try:

        pyperclip.copy(text)
        time.sleep(0.2)

        if pg.platform.system() == "Darwin":
            pg.hotkey("command", "v")
        else:
            pg.hotkey("ctrl", "v")

    except Exception as e:
        print(f"Error writing text: {e}")


# =========================
# MAIN
# =========================

def main():

    config = load_config()

    username = config["username"]
    message = config["message"]
    send_automatically = config.get("send_automatically", False)

    print("Starting Discord...")

    if not start_discord():
        return

    # Wait for Discord to load
    time.sleep(12)

    print("Opening Discord Quick Switcher...")

    # Ctrl+K opens Discord Quick Switcher
    pg.hotkey("ctrl", "k")
    time.sleep(1)

    # Search for user
    write_unicode(username)
    time.sleep(2)

    # Select search result
    pg.press("enter")
    time.sleep(3)

    # Paste message
    write_unicode(message)

    if send_automatically:

        pg.press("enter")
        print("Message sent.")

    else:

        print("Message pasted. Check the recipient and text.")

        input("Press Enter to send the message...")

        pg.press("enter")
        print("Message sent.")


if __name__ == "__main__":
    main()