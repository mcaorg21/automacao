import pyautogui
import time

def find_elements_on_screen(files, region=False, click=False, search=False, search_wait=0, limit=10):
    for file in files:
        try:
            element = pyautogui.locateOnScreen(
                image=file, 
                region=region, 
                grayscale=True, 
                confidence=0.95
            )
            element = pyautogui.center(element)

            if (click):
                pyautogui.click(element.x, element.y)

            return element
        except Exception as e:
            print("Erro: %s, Arquivo: %s" % (e, file))

    if (search == True and limit > 0):
        limit -= 1
        time.sleep(search_wait)
        return find_elements_on_screen(files, region, click, search, search_wait, limit)

    return False
