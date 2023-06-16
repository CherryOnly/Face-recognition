import cv2
import face_recognition
import os
from tkinter import filedialog

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

def delete_image_from_folder(image_path):
    if os.path.exists(image_path):
        os.remove(image_path)

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
