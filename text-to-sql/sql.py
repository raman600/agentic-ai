import sqlite3

#Connect to the SQLite database
connection = sqlite3.connect('student.db')

#Create a cursor object using the connection
cursor = connection.cursor()

#Create a table
table_info ="""
Create table student(Name Varchar(20), class varchar(20), section varchar(20), marks int);
"""

cursor.execute(table_info)

#Insert data into the table
cursor.execute("Insert into student values('John', 'Data Science', 'A', 85);")
cursor.execute("Insert into student values('Jane', 'Machine Learning', 'B', 90);")
cursor.execute("Insert into student values('Rob', 'Artificial Intelligence', 'B', 79);")
cursor.execute("Insert into student values('Matt', 'Business Intelligence', 'B', 95);")

data = cursor.execute('''Select * from student''')

for row in data:
    print(row)

#Close the connection
connection.commit()
connection.close()