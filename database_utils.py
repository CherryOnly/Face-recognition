import mysql.connector
import os

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