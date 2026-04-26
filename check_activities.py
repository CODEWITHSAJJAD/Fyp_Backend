import pyodbc
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-2GIJV0P\\SUQOON;DATABASE=fyp_ORM1;UID=sa;PWD=123456')
cursor = conn.cursor()
cursor.execute("SELECT activity_id, activity_name FROM Activity")
print('ID | Activity Name')
print('-' * 30)
for row in cursor.fetchall():
    print(f'{row[0]} | {row[1]}')
conn.close()