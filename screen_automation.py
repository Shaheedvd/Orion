import pyautogui
from backend.utils.logger import get_logger

logger = get_logger('screen')

def click(x, y):
    pyautogui.click(x, y)
    return {'ok': True}

def type_text(text):
    pyautogui.write(text)
    return {'ok': True}

def run_macro(actions):
    # actions: [{"type":"click","x":10,"y":20},{"type":"type","text":"hello"}]
    for a in actions:
        if a.get('type') == 'click':
            pyautogui.click(a['x'], a['y'])
        elif a.get('type') == 'type':
            pyautogui.write(a['text'])
    return {'ok': True}
