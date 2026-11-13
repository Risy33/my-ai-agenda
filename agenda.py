from datetime import date, timedelta

import database


def is_overdue(task, today):
    """A task is overdue when it is unfinished and its due date is before today."""
    return not task["completed"] and task["due_date"] is not None and task["due_date"] < today.isoformat()


def format_task(task, today):
    status = "x" if task["completed"] else " "
    due = f" (due {task['due_date']})" if task["due_date"] else ""
    overdue = " OVERDUE" if is_overdue(task, today) else ""
    return f"[{status}] {task['title']}{due} (priority {task['priority']}){overdue}"


def display_tasks(connection):
    tasks = database.get_tasks(connection)
    if not tasks:
        print("Your agenda is empty.")
        return

    today = date.today()
    for number, task in enumerate(tasks, start=1):
        print(f"{number}. {format_task(task, today)}")


def parse_due_date(text):
    """Turn text into 'YYYY-MM-DD'. Blank means no date (None). Raise ValueError if invalid."""
    text = text.strip()
    if not text:
        return None
    return date.fromisoformat(text).isoformat()


def parse_priority(text):
    """Turn text into 'low', 'medium', or 'high'. Blank means 'medium'. Raise ValueError if invalid."""
    text = text.strip().lower()
    if not text:
        return "medium"
    if text in ("low", "medium", "high"):
        return text
    raise ValueError("Priority must be 'low', 'medium', or 'high'.")


def ask_for_due_date(prompt="Due date (YYYY-MM-DD, or press Enter for none): "):
    """Ask for an optional due date. Return 'YYYY-MM-DD', None (no date), or False (invalid)."""
    try:
        return parse_due_date(input(prompt))
    except ValueError:
        print("That is not a valid date. Use the format YYYY-MM-DD, for example 2026-12-31.")
        return False


def ask_for_priority(prompt="Priority (low, medium, high, default is medium): "):
    """Ask for a priority. Return 'low', 'medium', or 'high', or False if invalid."""
    try:
        return parse_priority(input(prompt))
    except ValueError as e:
        print(e)
        return False


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

    due_date = ask_for_due_date()
    if due_date is False:
        return

    priority = ask_for_priority()
    if priority is False:
        return
    database.insert_task(connection, title, due_date, priority)
    print("Task added.")

def edit_priority(connection):
    task_id = ask_for_task_id(connection, "edit")
    if task_id is None:
        return

    text = input("New priority (low, medium, high, or Enter to keep it): ").strip()
    if not text:
        print("Keeping the current priority.")
        return

    try:
        priority = parse_priority(text)
    except ValueError as e:
        print(e)
        return

    database.update_priority(connection, task_id, priority)
    print("Priority updated.")


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


def edit_due_date(connection):
    task_id = ask_for_task_id(connection, "edit")
    if task_id is None:
        return

    text = input("New due date (YYYY-MM-DD, 'clear' to remove it, or Enter to keep it): ").strip()
    if not text:
        print("Keeping the current due date.")
        return

    if text.lower() == "clear":
        database.update_due_date(connection, task_id, None)
        print("Due date removed.")
        return

    try:
        due_date = parse_due_date(text)
    except ValueError:
        print("That is not a valid date. Use the format YYYY-MM-DD, for example 2026-12-31.")
        return

    database.update_due_date(connection, task_id, due_date)
    print("Due date updated.")


def show_today(connection, today=None):
    today = today or date.today()
    overdue = database.get_overdue_tasks(connection, today.isoformat())
    due_today = database.get_tasks_due_between(connection, today.isoformat(), today.isoformat())

    print(f"Today's agenda ({today.isoformat()})")
    if not overdue and not due_today:
        print("Nothing is due today and nothing is overdue.")
        return

    if overdue:
        print("Overdue:")
        for task in overdue:
            print(f"  - {task['title']} (due {task['due_date']}, priority {task['priority']})")
    if due_today:
        print("Due today:")
        for task in due_today:
            print(f"  - {task['title']} (priority {task['priority']})")


def show_next_seven_days(connection, today=None):
    today = today or date.today()
    end = today + timedelta(days=6)  # today plus the six days after it = seven days
    tasks = database.get_tasks_due_between(connection, today.isoformat(), end.isoformat())

    print(f"Next seven days ({today.isoformat()} to {end.isoformat()})")
    if not tasks:
        print("Nothing is due in the next seven days.")
        return

    current_day = None
    for task in tasks:
        if task["due_date"] != current_day:
            current_day = task["due_date"]
            weekday = date.fromisoformat(current_day).strftime("%A")
            print(f"{weekday} {current_day}:")
        print(f"  - {task['title']} (priority {task['priority']})")


def main():
    connection = database.connect()

    while True:
        print("\nMy AI Agenda")
        print("1. Add a task")
        print("2. Show tasks")
        print("3. Complete a task")
        print("4. Delete a task")
        print("5. Edit a task's due date")
        print("6. Edit a task's priority")
        print("7. Today's agenda")
        print("8. Next seven days")
        print("9. Quit")

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
            edit_due_date(connection)
        elif choice == "6":
            edit_priority(connection)
        elif choice == "7":
            show_today(connection)
        elif choice == "8":
            show_next_seven_days(connection)
        elif choice == "9":
            unfinished = [task for task in database.get_tasks(connection) if not task["completed"]]
            print(f"There are still {len(unfinished)} tasks not completed.")
            connection.close()
            print("Goodbye!")
            break
        else:
            print("Choose a number from 1 to 9.")


if __name__ == "__main__":
    main()