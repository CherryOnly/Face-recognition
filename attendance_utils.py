from datetime import datetime
import mysql.connector

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
