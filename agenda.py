from datetime import date, timedelta

import database
import tasks


def format_task(task, today):
    status = "x" if task["completed"] else " "
    due = f" (due {task['due_date']})" if task["due_date"] else ""
    category = f" [{task['category']}]" if task["category"] else ""
    overdue = " OVERDUE" if tasks.is_overdue(task, today) else ""
    return f"[{status}] {task['title']}{due} (priority {task['priority']}){category}{overdue}"


def print_numbered(task_list, today):
    for number, task in enumerate(task_list, start=1):
        print(f"{number}. {format_task(task, today)}")


def display_tasks(connection):
    task_list = database.get_tasks(connection)
    if not task_list:
        print("Your agenda is empty.")
        return
    print_numbered(task_list, date.today())


def ask_until_valid(prompt, parse):
    """Keep asking until `parse` accepts the answer, then return the parsed value.

    `parse` is a function such as tasks.parse_due_date: it returns a value or raises ValueError.
    """
    while True:
        try:
            return parse(input(prompt))
        except ValueError as error:
            print(error)


def ask_yes_no(prompt):
    """Return True only if the user answers 'y' or 'yes'. Anything else means no."""
    return input(prompt).strip().lower() in ("y", "yes")


def ask_for_task(connection, action):
    """Show the tasks, ask for a number, and return that task (or None)."""
    task_list = database.get_tasks(connection)
    if not task_list:
        print(f"There are no tasks to {action}.")
        return None

    print_numbered(task_list, date.today())
    try:
        number = int(input(f"Enter the task number to {action}: "))
    except ValueError:
        print("Please enter a number.")
        return None

    if number < 1 or number > len(task_list):
        print("That task number does not exist.")
        return None

    return task_list[number - 1]


def add_task(connection):
    try:
        title = tasks.parse_title(input("What do you need to do? "))
    except ValueError as error:
        print(error)
        return

    due_date = ask_until_valid("Due date (YYYY-MM-DD, or press Enter for none): ", tasks.parse_due_date)
    priority = ask_until_valid("Priority (low, medium, high, default is medium): ", tasks.parse_priority)
    category = tasks.parse_category(input("Category (optional, press Enter for none): "))
    database.insert_task(connection, title, due_date, priority, category)
    print("Task added.")


def complete_task(connection):
    task = ask_for_task(connection, "complete")
    if task is None:
        return
    if task["completed"]:
        print("That task is already completed.")
        return

    database.mark_completed(connection, task["id"])
    print("Task completed.")


def reopen_task(connection):
    task = ask_for_task(connection, "mark as not completed")
    if task is None:
        return
    if not task["completed"]:
        print("That task is not completed yet.")
        return

    database.mark_not_completed(connection, task["id"])
    print("Task marked as not completed.")


def delete_task(connection):
    task = ask_for_task(connection, "delete")
    if task is None:
        return

    if not ask_yes_no(f"Delete '{task['title']}'? This cannot be undone (y/N): "):
        print("Nothing was deleted.")
        return

    database.remove_task(connection, task["id"])
    print("Task deleted.")


def edit_title(connection):
    task = ask_for_task(connection, "rename")
    if task is None:
        return

    text = input(f"New title (or Enter to keep '{task['title']}'): ")
    if not text.strip():
        print("Keeping the current title.")
        return

    database.update_title(connection, task["id"], tasks.parse_title(text))
    print("Title updated.")


def edit_due_date(connection):
    task = ask_for_task(connection, "edit")
    if task is None:
        return

    text = input("New due date (YYYY-MM-DD, 'clear' to remove it, or Enter to keep it): ").strip()
    if not text:
        print("Keeping the current due date.")
        return

    if text.lower() == "clear":
        database.update_due_date(connection, task["id"], None)
        print("Due date removed.")
        return

    try:
        due_date = tasks.parse_due_date(text)
    except ValueError as error:
        print(error)
        return

    database.update_due_date(connection, task["id"], due_date)
    print("Due date updated.")


def edit_priority(connection):
    task = ask_for_task(connection, "edit")
    if task is None:
        return

    text = input("New priority (low, medium, high, or Enter to keep it): ").strip()
    if not text:
        print("Keeping the current priority.")
        return

    try:
        priority = tasks.parse_priority(text)
    except ValueError as error:
        print(error)
        return

    database.update_priority(connection, task["id"], priority)
    print("Priority updated.")


def edit_category(connection):
    task = ask_for_task(connection, "edit")
    if task is None:
        return

    text = input("New category (or 'clear' to remove it, Enter to keep it): ").strip()
    if not text:
        print("Keeping the current category.")
        return

    if text.lower() == "clear":
        database.update_category(connection, task["id"], None)
        print("Category removed.")
        return

    database.update_category(connection, task["id"], tasks.parse_category(text))
    print("Category updated.")


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
            print(f"  - {format_task(task, today)}")
    if due_today:
        print("Due today:")
        for task in due_today:
            print(f"  - {format_task(task, today)}")


def show_next_seven_days(connection, today=None):
    today = today or date.today()
    end = today + timedelta(days=6)  # today plus the six days after it = seven days
    task_list = database.get_tasks_due_between(connection, today.isoformat(), end.isoformat())

    print(f"Next seven days ({today.isoformat()} to {end.isoformat()})")
    if not task_list:
        print("Nothing is due in the next seven days.")
        return

    current_day = None
    for task in task_list:
        if task["due_date"] != current_day:
            current_day = task["due_date"]
            weekday = date.fromisoformat(current_day).strftime("%A")
            print(f"{weekday} {current_day}:")
        print(f"  - {format_task(task, today)}")


def filter_tasks(connection):
    status = input("Status filter (all, open, completed; default all): ").strip().lower() or "all"
    if status not in tasks.STATUSES:
        print("Status must be 'all', 'open', or 'completed'.")
        return

    try:
        start_date = tasks.parse_due_date(input("Due on or after (YYYY-MM-DD, optional): "))
        end_date = tasks.parse_due_date(input("Due on or before (YYYY-MM-DD, optional): "))
    except ValueError as error:
        print(error)
        return
    if start_date and end_date and start_date > end_date:
        print("The start date must be on or before the end date.")
        return

    categories = database.get_categories(connection)
    if categories:
        print(f"Categories: {', '.join(categories)}")
    category = tasks.parse_category(input("Category (optional): "))

    task_list = database.get_filtered_tasks(connection, status, start_date, end_date, category)
    if not task_list:
        print("No tasks match those filters.")
        return
    print_numbered(task_list, date.today())


def show_weekly_overview(connection, today=None):
    today = today or date.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    task_list = database.get_filtered_tasks(
        connection,
        start_date=start.isoformat(),
        end_date=end.isoformat(),
    )
    tasks_by_date = {}
    for task in task_list:
        tasks_by_date.setdefault(task["due_date"], []).append(task)

    print(f"Calendar week ({start.isoformat()} to {end.isoformat()})")
    for day_offset in range(7):
        current_day = start + timedelta(days=day_offset)
        print(f"{current_day.strftime('%A')} {current_day.isoformat()}:")
        day_tasks = tasks_by_date.get(current_day.isoformat(), [])
        if not day_tasks:
            print("  No tasks.")
            continue
        for task in day_tasks:
            print(f"  - {format_task(task, today)}")


def say_goodbye(connection):
    unfinished = [task for task in database.get_tasks(connection) if not task["completed"]]
    count = len(unfinished)
    if count == 0:
        print("All tasks are completed.")
    elif count == 1:
        print("There is still 1 task not completed.")
    else:
        print(f"There are still {count} tasks not completed.")
    print("Goodbye!")


def main():
    connection = database.connect()
    try:
        while True:
            print("\nMy AI Agenda")
            print("1. Add a task")
            print("2. Show tasks")
            print("3. Complete a task")
            print("4. Mark a task as not completed")
            print("5. Delete a task")
            print("6. Edit a task's title")
            print("7. Edit a task's due date")
            print("8. Edit a task's priority")
            print("9. Edit a task's category")
            print("10. Today's agenda")
            print("11. Next seven days")
            print("12. Filter tasks")
            print("13. Calendar-week overview")
            print("14. Quit")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                add_task(connection)
            elif choice == "2":
                display_tasks(connection)
            elif choice == "3":
                complete_task(connection)
            elif choice == "4":
                reopen_task(connection)
            elif choice == "5":
                delete_task(connection)
            elif choice == "6":
                edit_title(connection)
            elif choice == "7":
                edit_due_date(connection)
            elif choice == "8":
                edit_priority(connection)
            elif choice == "9":
                edit_category(connection)
            elif choice == "10":
                show_today(connection)
            elif choice == "11":
                show_next_seven_days(connection)
            elif choice == "12":
                filter_tasks(connection)
            elif choice == "13":
                show_weekly_overview(connection)
            elif choice == "14":
                say_goodbye(connection)
                break
            else:
                print("Choose a number from 1 to 14.")
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C or Ctrl+D: leave quietly instead of showing a traceback.
        print("\nGoodbye!")
    finally:
        connection.close()  # runs however the loop ends, even after an error


if __name__ == "__main__":
    main()
