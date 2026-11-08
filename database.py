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
    # Databases created before due dates existed need the new column added.
    columns = [row["name"] for row in connection.execute("PRAGMA table_info(tasks)")]
    if "due_date" not in columns:
        connection.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT")  # "YYYY-MM-DD" or NULL
    connection.commit()
    return connection


def get_tasks(connection):
    return connection.execute(
        "SELECT id, title, completed, due_date FROM tasks ORDER BY id"
    ).fetchall()


def insert_task(connection, title, due_date=None):
    connection.execute("INSERT INTO tasks (title, due_date) VALUES (?, ?)", (title, due_date))
    connection.commit()


def mark_completed(connection, task_id):
    connection.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
    connection.commit()


def update_due_date(connection, task_id, due_date):
    connection.execute("UPDATE tasks SET due_date = ? WHERE id = ?", (due_date, task_id))
    connection.commit()


def remove_task(connection, task_id):
    connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    connection.commit()

def update_due_date(connection, task_id, due_date):
    connection.execute("UPDATE tasks SET due_date = ? WHERE id = ?", (due_date, task_id))
    connection.commit()