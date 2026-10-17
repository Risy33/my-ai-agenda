import sqlite3

DB_FILE = "agenda.db"


def connect(db_file=DB_FILE):
    connection = sqlite3.connect(db_file) # opens the file and creates the table if it doesn't exist yet.
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


def display_tasks(connection):
    tasks = get_tasks(connection)
    if not tasks:
        print("Your agenda is empty.")
        return

    for number, task in enumerate(tasks, start=1):
        status = "x" if task["completed"] else " "
        print(f"{number}. [{status}] {task['title']}")


def add_task(connection):
    title = input("What do you need to do? ").strip()
    if not title:
        print("A task cannot be empty.")
        return

    connection.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
    connection.commit()
    print("Task added.")


def complete_task(connection):
    if not get_tasks(connection):
        print("There are no tasks to complete.")
        return

    display_tasks(connection)
    try:
        task_number = int(input("Enter the task number to complete: "))
    except ValueError:
        print("Please enter a number.")
        return

    tasks = get_tasks(connection)
    if task_number < 1 or task_number > len(tasks):
        print("That task number does not exist.")
        return

    task_id = tasks[task_number - 1]["id"]
    connection.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
    connection.commit()
    print("Task completed.")

def delete_task(connection):
    if not get_tasks(connection):
        print("There are no tasks to delete.")
        return

    display_tasks(connection)
    try:
        task_number = int(input("Enter the task number to delete: "))
    except ValueError:
        print("Please enter a number.")
        return

    tasks = get_tasks(connection)
    if task_number < 1 or task_number > len(tasks):
        print("That task number does not exist.")
        return

    task_id = tasks[task_number - 1]["id"]
    connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    connection.commit()

    print("Task deleted.")

def main():
    connection = connect()

    while True:
        print("\nMy AI Agenda")
        print("1. Add a task")
        print("2. Show tasks")
        print("3. Complete a task")
        print("4. Delete a task")
        print("5. Quit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_task(connection)
        elif choice == "2":
            display_tasks(connection)
        elif choice == "3":
            complete_task(connection)
        elif choice == "4":
            delete_task(connection)
        elif choice == "5":
            connection.close()
            print("Goodbye!")
            break
        else:
            print("Choose 1, 2, 3, 4, or 5.")


if __name__ == "__main__":
    main()