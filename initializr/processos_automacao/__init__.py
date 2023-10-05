import sys
from datetime import datetime as dt

# Shell constants for Windows and POSIX
CMD_PROMPT = "cmd.exe"
TERMINAL = "xterm"
CURR_SHELL = ""
KILLSHELL = ""
KILLCHROME = ""
# Check SO and build the shell command accordingly
SO = sys.platform
BASE_CMD: list = []

if "win" in SO:
    BASE_CMD = [CMD_PROMPT, "/K python"]
    CURR_SHELL = CMD_PROMPT
    KILLSHELL= "TASKKILL /IM conhost.exe /F"
    KILLCHROME = "TASKKILL /IM chrome.exe /F"

elif "linux" in SO:
    BASE_CMD = [TERMINAL, "-e", "python3"]
    CURR_SHELL = CMD_PROMPT
    KILLSHELL= f"killall {TERMINAL}"
    KILLCHROME = f"killall chrome"

STDWAIT = 10

# REBOOT_SCHED: bool = (int(dt.now().hour) % 6 == 0 and not int(dt.now().minute))

