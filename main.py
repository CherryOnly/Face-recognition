import tkinter as tk
import cv2
import numpy as np
import face_recognition
import os
from PIL import ImageGrab, Image, ImageTk
import time

from scrollable_frame import ScrollableFrame
from database_utils import create_database
from image_utils import load_images, view_faces, upload_image
from attendance_utils import markAttendance
from capture_utils import captureScreen, main
from export_utils import view_stats_button_click

root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

root.title("Face Recognition")
root.geometry("300x400")

screen_button = tk.Button(root, text="Use Screen", command=on_screen_button_click)
screen_button.pack(pady=10)

webcam_button = tk.Button(root, text="Use Webcam", command=on_webcam_button_click)
webcam_button.pack(pady=10)

view_faces_button = tk.Button(root, text="View Faces", command=view_faces)
view_faces_button.pack(pady=10)

view_stats_button = tk.Button(root, text="View Recognition Statistics", command=view_stats_button_click)
view_stats_button.pack(pady=10)

root.mainloop()
