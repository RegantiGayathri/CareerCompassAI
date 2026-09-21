import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="G@y@3123",
            database="CareerCompassDB"
        )

        if connection.is_connected():
            print("MySQL database connected successfully!")
            return connection

    except Error as e:
        print("Database connection error:", e)
        return None
if __name__ == "__main__":
    connection = get_connection()

    if connection:
        print("✅ Connection test successful!")
        connection.close()
    else:
        print("❌ Connection test failed!")