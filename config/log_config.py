import logging
import os
import sys


# Duplicate to avoid circular imports

def resource_path_log(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    filename=resource_path_log('./logs/app.logs'),
    filemode='w'
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(log_format))
logging.getLogger().addHandler(console_handler)

logger = logging.getLogger()
