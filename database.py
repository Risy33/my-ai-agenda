import sqlite3

DB_FILE = "agenda.db"


def connect(db_file=DB_FILE):
    connection = sqlite3.connect(db_file)  # opens the file, creating it if needed
    connection.row_factory = sqlite3.Row  # lets us read columns by name
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    connection.commit()
    return connection


def get_tasks(connection):
    return connection.execute("SELECT id, title, completed FROM tasks ORDER BY id").fetchall()


def insert_task(connection, title):
    connection.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
    connection.commit()


def mark_completed(connection, task_id):
    connection.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
    connection.commit()


def remove_task(connection, task_id):
    connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    connection.commit()
