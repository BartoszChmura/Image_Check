import os
import shutil
import tkinter as tk
from PIL import Image, ImageTk


class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Przeglądarka zdjęć")

        self.folder_path = './zdjecia/nowe'
        self.checked_folder_path = './zdjecia/sprawdzone'

        self.image_list = [f for f in os.listdir(self.folder_path) if f.endswith(('png', 'jpg', 'jpeg', 'bmp'))]
        self.current_index = 0

        self.image_label = tk.Label(root)
        self.image_label.pack()

        self.delete_button = tk.Button(root, text="Odrzuć", command=self.delete_image)
        self.delete_button.pack(side=tk.RIGHT)

        self.keep_button = tk.Button(root, text="Zachowaj", command=self.keep_image)
        self.keep_button.pack(side=tk.RIGHT)

        self.prev_button = tk.Button(root, text="Poprzednie", command=self.prev_image)
        self.prev_button.pack(side=tk.LEFT)

        self.next_button = tk.Button(root, text="Następne", command=self.next_image)
        self.next_button.pack(side=tk.LEFT)

        self.root.bind("<Left>", self.prev_image)
        self.root.bind("<Right>", self.next_image)
        self.root.bind("<Escape>", self.close_app)

        self.show_image()

    def show_image(self):
        if self.image_list:
            image_path = os.path.join(self.folder_path, self.image_list[self.current_index])
            image = Image.open(image_path)
            image.thumbnail((1000, 1000))
            self.photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=self.photo)
            self.root.title(f"Przeglądarka zdjęć - {self.image_list[self.current_index]}")
        else:
            self.image_label.config(text="Brak zdjęć w folderze")

    def keep_image(self):
        if self.image_list:
            image_path = os.path.join(self.folder_path, self.image_list[self.current_index])
            new_path = os.path.join(self.checked_folder_path, self.image_list[self.current_index])
            shutil.move(image_path, new_path)
            del self.image_list[self.current_index]
            if self.current_index >= len(self.image_list):
                self.current_index = len(self.image_list) - 1
            self.show_image()

    def delete_image(self):
        if self.image_list:
            image_path = os.path.join(self.folder_path, self.image_list[self.current_index])
            os.remove(image_path)
            del self.image_list[self.current_index]
            if self.current_index >= len(self.image_list):
                self.current_index = len(self.image_list) - 1
            self.show_image()

    def next_image(self, event=None):
        if self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.show_image()
        elif self.image_list:
            self.current_index = 0
            self.show_image()

    def prev_image(self, event=None):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_image()
        elif self.image_list:
            self.current_index = len(self.image_list) - 1
            self.show_image()

    def close_app(self, event=None):
        self.root.quit()
