**PyInstaller command to create .exe file**

pyinstaller --noconfirm --onefile --windowed --name "ImageCheck" --add-data "config;config/" --add-data "logs;logs/" --add-data "images;images/" --add-data "model;model/" --add-data "qss;qss/" --add-data ".venv/Lib/site-packages/ultralytics/cfg/default.yaml;ultralytics/cfg/" main.py
