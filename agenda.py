def display_tasks(tasks):
    if not tasks:
        print("Your agenda is empty.")
        return

    for number, task in enumerate(tasks, start=1):
        status = "x" if task["completed"] else " "
        print(f"{number}. [{status}] {task['title']}")


def add_task(tasks):
    title = input("What do you need to do? ").strip()
    if not title:
        print("A task cannot be empty.")
        return

    tasks.append({"title": title, "completed": False})
    print("Task added.")


def complete_task(tasks):
    if not tasks:
        print("There are no tasks to complete.")
        return

    display_tasks(tasks)
    try:
        number = int(input("Enter the task number to complete: "))
    except ValueError:
        print("Please enter a number.")
        return

    if number < 1 or number > len(tasks):
        print("That task number does not exist.")
        return

    tasks[number - 1]["completed"] = True
    print("Task completed.")


def main():
    tasks = []

    while True:
        print("\nMy AI Agenda")
        print("1. Add a task")
        print("2. Show tasks")
        print("3. Complete a task")
        print("4. Quit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            display_tasks(tasks)
        elif choice == "3":
            complete_task(tasks)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Choose 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()