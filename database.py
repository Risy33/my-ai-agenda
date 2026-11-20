import sqlite3

DB_FILE = "agenda.db"

# Bump this number whenever the table structure changes, and add a step to migrate().
SCHEMA_VERSION = 1

TASK_COLUMNS = "id, title, completed, due_date, priority, category"

# The current table structure. The CHECK constraints are a last line of defence:
# even if a bug (or an AI response) slips past tasks.py, SQLite refuses invalid data.
CREATE_TASKS_TABLE = """
    CREATE TABLE {name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL CHECK (trim(title) != ''),
        completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1)),
        due_date TEXT CHECK (due_date IS NULL OR date(due_date) IS due_date),
        priority TEXT NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
        category TEXT CHECK (category IS NULL OR trim(category) != '')
    )
"""

# Columns that very old databases (from before these features) may be missing.
LEGACY_COLUMNS = {
    "due_date": "TEXT",
    "priority": "TEXT NOT NULL DEFAULT 'medium'",
    "category": "TEXT",
}


def connect(db_file=DB_FILE):
    connection = sqlite3.connect(db_file)  # opens the file, creating it if needed
    connection.row_factory = sqlite3.Row  # lets us read columns by name
    version = connection.execute("PRAGMA user_version").fetchone()[0]
    if version < SCHEMA_VERSION:
        migrate(connection)
    return connection


def migrate(connection):
    """Bring the database up to SCHEMA_VERSION in one transaction (all or nothing)."""
    connection.execute("BEGIN")
    with connection:  # commits if every step succeeds, rolls back if any step fails
        table_exists = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'tasks'"
        ).fetchone()

        if not table_exists:
            connection.execute(CREATE_TASKS_TABLE.format(name="tasks"))
        else:
            # Add any missing columns, then copy everything into a table with constraints.
            # (SQLite cannot add CHECK constraints to an existing table, so we rebuild it.)
            columns = [row["name"] for row in connection.execute("PRAGMA table_info(tasks)")]
            for name, definition in LEGACY_COLUMNS.items():
                if name not in columns:
                    connection.execute(f"ALTER TABLE tasks ADD COLUMN {name} {definition}")
            connection.execute(CREATE_TASKS_TABLE.format(name="tasks_new"))
            connection.execute(
                f"INSERT INTO tasks_new ({TASK_COLUMNS}) SELECT {TASK_COLUMNS} FROM tasks"
            )
            connection.execute("DROP TABLE tasks")
            connection.execute("ALTER TABLE tasks_new RENAME TO tasks")

        connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")


def get_tasks(connection):
    # Earliest due date first; tasks without a date (NULL) go last. id keeps ties stable.
    return connection.execute(
        f"SELECT {TASK_COLUMNS} FROM tasks ORDER BY due_date IS NULL, due_date, id"
    ).fetchall()


def get_overdue_tasks(connection, today):
    """Unfinished tasks whose due date is before `today` ('YYYY-MM-DD')."""
    return connection.execute(
        f"SELECT {TASK_COLUMNS} FROM tasks "
        "WHERE completed = 0 AND due_date < ? ORDER BY due_date, id",
        (today,),
    ).fetchall()


def get_tasks_due_between(connection, start, end):
    """Unfinished tasks due from `start` to `end`, both included ('YYYY-MM-DD')."""
    return connection.execute(
        f"SELECT {TASK_COLUMNS} FROM tasks "
        "WHERE completed = 0 AND due_date BETWEEN ? AND ? ORDER BY due_date, id",
        (start, end),
    ).fetchall()


def get_categories(connection):
    return [
        row["category"]
        for row in connection.execute(
            "SELECT DISTINCT category FROM tasks "
            "WHERE category IS NOT NULL ORDER BY category COLLATE NOCASE"
        )
    ]


def get_filtered_tasks(connection, status="all", start_date=None, end_date=None, category=None):
    """Return tasks matching optional status, inclusive date bounds, and category (any case)."""
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
        conditions.append("category = ? COLLATE NOCASE")  # "work" also matches "Work"
        parameters.append(category)

    where_clause = f" WHERE {' AND '.join(conditions)}" if conditions else ""
    return connection.execute(
        f"SELECT {TASK_COLUMNS} FROM tasks"
        f"{where_clause} ORDER BY due_date IS NULL, due_date, id",
        parameters,
    ).fetchall()


def insert_task(connection, title, due_date=None, priority="medium", category=None):
    connection.execute(
        "INSERT INTO tasks (title, due_date, priority, category) VALUES (?, ?, ?, ?)",
        (title, due_date, priority, category),
    )
    connection.commit()


def mark_completed(connection, task_id):
    connection.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
    connection.commit()


def mark_not_completed(connection, task_id):
    connection.execute("UPDATE tasks SET completed = 0 WHERE id = ?", (task_id,))
    connection.commit()


def update_title(connection, task_id, title):
    connection.execute("UPDATE tasks SET title = ? WHERE id = ?", (title, task_id))
    connection.commit()


def update_due_date(connection, task_id, due_date):
    connection.execute("UPDATE tasks SET due_date = ? WHERE id = ?", (due_date, task_id))
    connection.commit()


def update_priority(connection, task_id, priority):
    connection.execute("UPDATE tasks SET priority = ? WHERE id = ?", (priority, task_id))
    connection.commit()


def update_category(connection, task_id, category):
    connection.execute("UPDATE tasks SET category = ? WHERE id = ?", (category, task_id))
    connection.commit()


def remove_task(connection, task_id):
    connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    connection.commit()
