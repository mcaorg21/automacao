from psutil import process_iter
import sys
import os


def count_process(proc_name: str, stop_limit: int=0):
    cnt = 0
    for process in process_iter():
        try:
            if proc_name in process.name():
                cnt += 1
                print(f"\rProcessos Chrome:{cnt}", end="")
                if stop_limit and cnt > stop_limit:
                    return cnt
        except:
            pass
    return cnt


def killall_by_name(proc_name: str, max_processes_allowed=0):
    if count_process(proc_name, max_processes_allowed) > max_processes_allowed:
        if "linux" in sys.platform:
            os.system(f"killall chrome")
        elif "win" in sys.platform:
            os.system("TASKKILL /IM chrome.exe /F")
