import tkinter as tk
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
from PIL import ImageGrab, Image, ImageTk
import time
import mysql.connector
import shutil
from tkinter import filedialog
import pandas as pd
from tkinter import ttk
from fpdf import FPDF


class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.images = []
        canvas = tk.Canvas(self)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


def upload_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        new_path = os.path.join('Original', os.path.basename(file_path))
        shutil.copy(file_path, new_path)
        images.append(cv2.imread(new_path))
        classNames.append(os.path.splitext(os.path.basename(new_path))[0])
        image_paths.append(new_path)
        insert_image_paths([new_path])
        print(f"Image {os.path.basename(new_path)} has been uploaded.")
        view_faces()  # Refresh the face view




def create_database():
    mydb = mysql.connector.connect(
        host="localhost",
        user="user_without_password",
        database="faces"
    )
    mycursor = mydb.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS faces (id INT AUTO_INCREMENT PRIMARY KEY, image_path VARCHAR(255))")
    mycursor.execute("CREATE TABLE IF NOT EXISTS attendance (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), time VARCHAR(255))")

def insert_image_paths(image_paths):
    mydb = mysql.connector.connect(
        host="localhost",
        user="user_without_password",
        database="faces"
    )
    mycursor = mydb.cursor()

    for path in image_paths:
        mycursor.execute("SELECT image_path FROM faces WHERE image_path = %s", (path,))
        result = mycursor.fetchone()
        if result is None:
            sql = "INSERT INTO faces (image_path) VALUES (%s)"
            val = (path,)
            mycursor.execute(sql, val)

    mydb.commit()


def delete_image_from_db(image_path):
    mydb = mysql.connector.connect(
        host="localhost",
        user="user_without_password",
        database="faces"
    )
    mycursor = mydb.cursor()

    mycursor.execute("DELETE FROM faces WHERE image_path = %s", (image_path,))
    mydb.commit()


def delete_image_from_folder(image_path):
    if os.path.exists(image_path):
        os.remove(image_path)


def add_image_to_db(image_path):
    mydb = mysql.connector.connect(
        host="localhost",
        user="user_without_password",
        database="faces"
    )
    mycursor = mydb.cursor()

    mycursor.execute("SELECT image_path FROM faces WHERE image_path = %s", (image_path,))
    result = mycursor.fetchone()
    if result is None:
        sql = "INSERT INTO faces (image_path) VALUES (%s)"
        val = (image_path,)
        mycursor.execute(sql, val)

    mydb.commit()


def view_faces():
    # Check if the face view window already exists
    if hasattr(view_faces, 'image_window') and view_faces.image_window.winfo_exists():
        # Close the previous face view window
        view_faces.image_window.destroy()

    image_window = tk.Toplevel(root)
    image_window.title("Faces")

    scrollable_frame = ScrollableFrame(image_window)
    scrollable_frame.pack(fill="both", expand=True)

    standard_size = (200, 200)
    processed_paths = set()

    mydb = mysql.connector.connect(
        host="localhost",
        user="user_without_password",
        database="faces"
    )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT image_path FROM faces")
    image_paths = mycursor.fetchall()

    for i, path in enumerate(image_paths):
        if i > 50 or path[0] in processed_paths:
            continue

        if not os.path.isfile(path[0]):  # Check if file exists
            print(f"File {path[0]} does not exist")
            continue

        img = cv2.imread(path[0])

        if img is None:  # Check if image loading was successful
            print(f"Unable to load image {path[0]}")
            continue

        processed_paths.add(path[0])

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = img.resize(standard_size, Image.ANTIALIAS)
        imgtk = ImageTk.PhotoImage(image=img)
        scrollable_frame.images.append(imgtk)

        frame = tk.Frame(scrollable_frame.scrollable_frame)
        frame.pack()

        label = tk.Label(frame, image=imgtk)
        label.pack(side='left')

        delete_button = tk.Button(frame, text="Delete", command=lambda p=path[0]: delete_image_from_db_and_folder(p))
        delete_button.pack(side='right')

    upload_button = tk.Button(image_window, text="Upload Image", command=upload_image)
    upload_button.pack(side='top', anchor='ne')

    # Store the reference to the new face view window
    view_faces.image_window = image_window


def delete_image_from_db_and_folder(image_path):
    delete_image_from_db(image_path)
    delete_image_from_folder(image_path)
    view_faces()


create_database()

path = 'Original'
images = []
classNames = []
image_paths = []
myList = os.listdir(path)
for cl in myList:
    image_path = f'{path}/{cl}'
    curImg = cv2.imread(image_path)
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
    image_paths.append(image_path)
print(classNames)

insert_image_paths(image_paths)

root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


def markAttendance(name):
    now = datetime.now()
    dtString = now.strftime('%Y-%m-%d %H:%M:%S')

    mydb = mysql.connector.connect(
        host="localhost",
        user="user_without_password",
        database="faces"
    )
    mycursor = mydb.cursor()

    # Check the last timestamp that the name was logged
    mycursor.execute("SELECT time FROM attendance WHERE name = %s ORDER BY time DESC LIMIT 1", (name,))
    result = mycursor.fetchone()

    if result is not None:
        last_logged_time = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
        if (now - last_logged_time).total_seconds() < 10:
            print(f"Already logged attendance for {name} in the last 10 seconds")
            return

    sqlFormula = "INSERT INTO attendance (name, time) VALUES (%s, %s)"
    mycursor.execute(sqlFormula, (name, dtString))
    mydb.commit()
    print('Attendance marked for ' + name)



def captureScreen(bbox=(0, 0, screen_width, screen_height)):
    capScr = np.array(ImageGrab.grab(bbox))
    capScr = cv2.cvtColor(capScr, cv2.COLOR_RGB2BGR)
    return capScr


def view_stats_button_click():
    # Create a new window for displaying statistics
    stats_window = tk.Toplevel(root)
    stats_window.title("Recognition Statistics")

    mydb = mysql.connector.connect(
        host="localhost",
        user="user_without_password",
        database="faces"
    )
    mycursor = mydb.cursor()

    # Query the attendance data
    mycursor.execute("SELECT name, time FROM attendance ORDER BY time DESC")
    result = mycursor.fetchall()

    # Create a list to store the statistics
    stats = []

    # Format the statistics
    for row in result:
        stats.append(f"Name: {row[0]}, Time: {row[1]}")

    # Create a scrollable frame to display the statistics
    scrollable_frame = ScrollableFrame(stats_window)
    scrollable_frame.pack(fill="both", expand=True)

    # Display each statistic in a new label
    for stat in stats:
        label = tk.Label(scrollable_frame.scrollable_frame, text=stat)
        label.pack(pady=10)
        
    export_stats_button = tk.Button(stats_window, text="Export Statistics", command=export_stats_button_click)
    export_stats_button.pack(pady=10)


def export_stats_button_click():
    # Open the file dialog to select the save location
    filetypes = [('CSV Files', '*.csv'), ('Excel Files', '*.xls'), ('Text Files', '*.txt'), ('PDF Files', '*.pdf'), ('All Files', '*.*')]
    save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=filetypes)
    
    if save_path:
        # Export the data to a file
        export_file(save_path)


def export_file(save_path):
    extension = os.path.splitext(save_path)[-1].lower()

    mydb = mysql.connector.connect(
        host="localhost",
        user="user_without_password",
        database="faces"
    )
    mycursor = mydb.cursor()

    # Query the attendance data
    mycursor.execute("SELECT name, time FROM attendance ORDER BY time DESC")
    result = mycursor.fetchall()

    # Convert the data into a pandas DataFrame
    data = pd.DataFrame(result, columns=['name', 'time'])

    if extension == '.csv':
        # Save the data to the selected file path as a CSV file
        data.to_csv(save_path, index=False)
    elif extension == '.xls':
        # Save the data to the selected file path as an Excel file
        data.to_excel(save_path, index=False)
    elif extension == '.txt':
        # Save the data to the selected file path as a text file
        data.to_csv(save_path, sep='\t', index=False)
    elif extension == '.pdf':
        export_to_pdf(data, save_path)

    print("Data exported successfully.")


def export_to_pdf(data, save_path):
    pdf = FPDF()

    # Column widths
    w = [40, 60]

    # Add a page
    pdf.add_page()

    # Set font
    pdf.set_font("Arial", size=12)

    # Add a cell
    pdf.cell(200, 10, txt="Name and Time", ln=True, align='C')

    # Header
    for i, column in enumerate(data.columns):
        pdf.cell(w[i], 10, txt=column, border=1, ln=False)

    pdf.ln(10)

    # Data
    for row in data.itertuples():
        pdf.cell(w[0], 10, txt=row[1], border=1, ln=False)
        pdf.cell(w[1], 10, txt=str(row[2]), border=1, ln=True)

    # Save the pdf with name .pdf
    pdf.output(save_path)


def main(use_screen):
    encodeListKnown = findEncodings(images)
    print('Encoding Complete')

    if not use_screen:
        cap = cv2.VideoCapture(0)

    prev_frame_time = 0
    skipped_frames = 15

    while True:
        time_elapsed = time.time() - prev_frame_time
        if time_elapsed > 1. / skipped_frames:
            if use_screen:
                img = captureScreen()
            else:
                success, img = cap.read()

            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            facesCurFrame = face_recognition.face_locations(imgS, model='cnnq')
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    name = classNames[matchIndex].upper()
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    markAttendance(name)

            cv2.imshow('Webcam', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            prev_frame_time = time.time()

    if not use_screen:
        cap.release()
    cv2.destroyAllWindows()



def on_screen_button_click():
    root.destroy()
    main(use_screen=True)


def on_webcam_button_click():
    root.destroy()
    main(use_screen=False)


root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set the style
style = ttk.Style()
style.theme_use("clam")

# Set consistent padding
style.configure(".", padding=6)

root.title("Face Recognition")
root.geometry("300x400")

# Configure the grid
root.columnconfigure(0, weight=1)
root.rowconfigure([0, 1, 2, 3], weight=1)

# Create and grid the buttons
screen_button = ttk.Button(root, text="Use Screen", command=on_screen_button_click)
screen_button.grid(row=0, sticky='ew', padx=20, pady=20)

webcam_button = ttk.Button(root, text="Use Webcam", command=on_webcam_button_click)
webcam_button.grid(row=1, sticky='ew', padx=20, pady=20)

view_faces_button = ttk.Button(root, text="View Faces", command=view_faces)
view_faces_button.grid(row=2, sticky='ew', padx=20, pady=20)

view_stats_button = ttk.Button(root, text="View Recognition Statistics", command=view_stats_button_click)
view_stats_button.grid(row=3, sticky='ew', padx=20, pady=20)

root.mainloop()

