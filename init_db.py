# sqlite3 is a library that connects our application to a database
import sqlite3
# Connect to the database (this creates quiz.db if it doesn't already exist)
conn = sqlite3.connect("quiz.db")
# A cursor lets us execute SQL commands
cursor = conn.cursor()
# Create the users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
# Create the results table
cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    score_percentage REAL,
    score INTEGER,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS score (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    score INTEGER,
    user_id  INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")
# Save the changes
conn.commit() 
# Close the database connection
conn.close()
print("Database created!")