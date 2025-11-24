import mysql.connector

# these are just placeholders
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Edidiong@06",
        database="result copy"
    )
