import cv2
import numpy as np
from PIL import ImageGrab


def captureScreen(bbox=(0, 0, screen_width, screen_height)):
    capScr = np.array(ImageGrab.grab(bbox))
    capScr = cv2.cvtColor(capScr, cv2.COLOR_RGB2BGR)
    return capScr

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