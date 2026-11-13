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
    columns = [row["name"] for row in connection.execute("PRAGMA table_info(tasks)")]
    if "priority" not in columns:
        connection.execute("ALTER TABLE tasks ADD COLUMN priority TEXT NOT NULL DEFAULT 'medium'")  # "low", "medium" or "high"
    connection.commit()
    columns = [row["name"] for row in connection.execute("PRAGMA table_info(tasks)")]
    if "category" not in columns:
        connection.execute("ALTER TABLE tasks ADD COLUMN category TEXT")
    connection.commit()
    return connection


def get_tasks(connection):
    # Earliest due date first; tasks without a date (NULL) go last. id keeps ties stable.
    return connection.execute(
        "SELECT id, title, completed, due_date, priority, category "
        "FROM tasks ORDER BY due_date IS NULL, due_date, id"
    ).fetchall()


def get_overdue_tasks(connection, today):
    """Unfinished tasks whose due date is before `today` ('YYYY-MM-DD')."""
    return connection.execute(
        "SELECT id, title, completed, due_date, priority, category FROM tasks "
        "WHERE completed = 0 AND due_date < ? ORDER BY due_date, id",
        (today,),
    ).fetchall()


def get_tasks_due_between(connection, start, end):
    """Unfinished tasks due from `start` to `end`, both included ('YYYY-MM-DD')."""
    return connection.execute(
        "SELECT id, title, completed, due_date, priority, category FROM tasks "
        "WHERE completed = 0 AND due_date BETWEEN ? AND ? ORDER BY due_date, id",
        (start, end),
    ).fetchall()


def get_categories(connection):
    return [
        row["category"]
        for row in connection.execute(
            "SELECT DISTINCT category FROM tasks "
            "WHERE category IS NOT NULL AND category != '' ORDER BY category COLLATE NOCASE"
        )
    ]


def get_filtered_tasks(connection, status="all", start_date=None, end_date=None, category=None):
    """Return tasks matching optional status, inclusive date bounds, and exact category."""
    if status not in ("all", "open", "completed"):
        raise ValueError("Status must be 'all', 'open', or 'completed'.")

    conditions = []
    parameters = []
    if status == "open":
        conditions.append("completed = 0")
    elif status == "completed":
        conditions.append("completed = 1")
    if start_date is not None:
        conditions.append("due_date >= ?")
        parameters.append(start_date)
    if end_date is not None:
        conditions.append("due_date <= ?")
        parameters.append(end_date)
    if category is not None:
        conditions.append("category = ?")
        parameters.append(category)

    where_clause = f" WHERE {' AND '.join(conditions)}" if conditions else ""
    return connection.execute(
        "SELECT id, title, completed, due_date, priority, category FROM tasks"
        f"{where_clause} ORDER BY due_date IS NULL, due_date, id",
        parameters,
    ).fetchall()


def insert_task(connection, title, due_date=None, priority='medium', category=None):
    connection.execute(
        "INSERT INTO tasks (title, due_date, priority, category) VALUES (?, ?, ?, ?)",
        (title, due_date, priority, category),
    )
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

def update_priority(connection, task_id, priority):
    connection.execute("UPDATE tasks SET priority = ? WHERE id = ?", (priority, task_id))
    connection.commit()


def update_category(connection, task_id, category):
    connection.execute("UPDATE tasks SET category = ? WHERE id = ?", (category, task_id))
    connection.commit()