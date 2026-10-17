import database


def display_tasks(connection):
    tasks = database.get_tasks(connection)
    if not tasks:
        print("Your agenda is empty.")
        return

    for number, task in enumerate(tasks, start=1):
        status = "x" if task["completed"] else " "
        print(f"{number}. [{status}] {task['title']}")


def ask_for_task_id(connection, action):
    """Show the tasks, ask for a number, and return that task's database id (or None)."""
    tasks = database.get_tasks(connection)
    if not tasks:
        print(f"There are no tasks to {action}.")
        return None

    display_tasks(connection)
    try:
        number = int(input(f"Enter the task number to {action}: "))
    except ValueError:
        print("Please enter a number.")
        return None

    if number < 1 or number > len(tasks):
        print("That task number does not exist.")
        return None

    return tasks[number - 1]["id"]


def add_task(connection):
    title = input("What do you need to do? ").strip()
    if not title:
        print("A task cannot be empty.")
        return

    database.insert_task(connection, title)
    print("Task added.")


def complete_task(connection):
    task_id = ask_for_task_id(connection, "complete")
    if task_id is None:
        return

    database.mark_completed(connection, task_id)
    print("Task completed.")


def delete_task(connection):
    task_id = ask_for_task_id(connection, "delete")
    if task_id is None:
        return

    database.remove_task(connection, task_id)
    print("Task deleted.")


def main():
    connection = database.connect()

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
