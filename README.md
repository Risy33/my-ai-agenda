# My AI Agenda — Python & LLM Learning Project

## 1. Project vision

I want to build my own personal agenda application using Python. The application should help me organize tasks, plan my week, and eventually interact with an AI assistant using natural language.

This project is also my way of learning Python and understanding how Large Language Models (LLMs) work, from basic API usage to more advanced concepts such as embeddings, RAG, and AI agents.

The main goal is to build a genuinely useful application while understanding the code and AI concepts behind it.

I am a beginner, so the project must grow incrementally. Do not build the entire application at once. How Copilot should teach me is described in [`.github/copilot-instructions.md`](.github/copilot-instructions.md).

## Current milestone: terminal agenda with SQLite storage

A small Python program that can add tasks, show them, mark them complete (or not completed again), delete them, edit titles, due dates, priorities, and categories, and show planning views. Tasks are saved in a local SQLite file (`agenda.db`, created automatically and ignored by Git), so they survive restarts.

Run it with Python 3.9 or newer:

```bash
python agenda.py
```

Choose an option from the menu. Try adding a task, completing or deleting one by its number, and then quitting (option 14, or Ctrl+C). Restart the program to see that the tasks were saved. The numbers shown are positions in the list (1, 2, 3...); the program maps them to the real database IDs.

How it behaves:

- Tasks are listed by due date (earliest first, tasks without a date last). Unfinished tasks whose due date has passed are marked `OVERDUE`.
- When adding a task, an invalid date or priority is asked for again.
- Deleting a task asks for confirmation first.
- When editing a title, due date, or category, type a new value or press Enter to keep it. For due dates and categories, `clear` removes the value.
- **Today's agenda** shows overdue tasks plus tasks due today.
- **Next seven days** shows unfinished tasks due from today through the following six days, grouped by day.
- **Calendar-week overview** shows all tasks due Monday through Sunday, including completed tasks.
- **Filter tasks** combines task status, inclusive due-date bounds, and a category (upper/lower case is ignored).

To inspect the data: `sqlite3 agenda.db "SELECT * FROM tasks;"`

To run the tests (pytest):

```bash
pip install -r requirements-dev.txt
python -m pytest
```

### How the code is organized

| File | Responsibility |
| --- | --- |
| `agenda.py` | User interface: the terminal menu, `input()` and `print()`. |
| `tasks.py` | Application logic: validating titles, dates, priorities, and categories; deciding what is overdue. |
| `database.py` | Data storage: every SQL statement, plus creating and upgrading the database. |
| `test_agenda.py` | Automated tests. |
| `api.py` | Web API (FastAPI), a second interface next to the terminal menu. In progress, see below. |
| `requirements.txt` | Packages the app needs to run (`requirements-dev.txt` holds development-only tools such as pytest). |

### Concepts in this milestone

- The `sqlite3` module and a `tasks` table (`id`, `title`, `completed`, `due_date`, `priority`, `category`).
- Separating responsibilities: interface, logic, and storage each live in their own module.
- SQL `INSERT`, `SELECT`, `UPDATE`, and `DELETE`, with `?` placeholders for safe input.
- `CHECK` constraints, so the database itself refuses invalid data (blank titles, unknown priorities, impossible dates).
- Schema versions with `PRAGMA user_version`: `connect()` upgrades older databases automatically, inside one transaction so it either fully succeeds or changes nothing.
- `enumerate` numbers the displayed list; the chosen number is mapped back to the database ID.
- Error handling: functions in `tasks.py` raise `ValueError`, and the interface catches it and shows the message. `ask_until_valid()` keeps asking until the answer is valid (it receives the parsing function as an argument).
- `try` / `except` / `finally` in `main()`: Ctrl+C exits cleanly and the database connection is always closed.
- Due dates stored as text in `YYYY-MM-DD` format, validated with `datetime.date.fromisoformat`.
- Sorting in SQL with `ORDER BY`, querying date ranges with `BETWEEN` (ISO dates compare correctly as text), and case-insensitive matching with `COLLATE NOCASE`.
- `datetime.date` and `timedelta` for "today" and "seven days from now"; `date.weekday()` to find Monday for the calendar week.
- Testing: pytest with an in-memory SQLite database (`":memory:"`), so tests never touch `agenda.db`; `monkeypatch` replaces `input()` to test menu flows; `parametrize` runs one test with several inputs.

The personal-planning features are in place: due dates, priorities, categories, filters, today's agenda, the next seven days, and a calendar-week overview. The AI assistant comes after those foundations.

The AI assistant will propose structured tasks for you to review, and only confirmed tasks that pass the checks in `tasks.py` will be saved.

## Next milestone: web API with FastAPI (in progress)

**Goal:** add a web API with FastAPI as a second interface next to `agenda.py`, reusing `tasks.py` and `database.py` unchanged. This prepares the ground for the Nuxt web interface and the AI assistant (Version 3), and introduces Pydantic for data validation. The terminal app must keep working the whole time.

### Setup

Requires Python 3.10 or newer (FastAPI's documentation uses `str | None` syntax). The project uses Python 3.12 in a virtual environment:

```bash
python3.12 -m venv .venv          # only once
source .venv/bin/activate         # in every new terminal
pip install -r requirements.txt   # fastapi[standard], which includes the uvicorn server
fastapi dev api.py                # runs the API and restarts it when a file changes
```

Then open http://127.0.0.1:8000/health or the interactive docs page at http://127.0.0.1:8000/docs. Stop the server with Ctrl+C.

### Steps

| Step | What to build | New concepts | Status |
| --- | --- | --- | --- |
| 1 | Virtual environment, install FastAPI, `api.py` with `GET /health` | HTTP request/response, endpoints, JSON, status codes, decorators | ✅ Done |
| 2 | `GET /tasks` returns all tasks as JSON | Importing own modules, opening/closing a connection, `dict(row)`, list comprehensions | ⏭️ Next |
| 3 | One database connection per request with `Depends` | Dependency injection; SQLite connections and threads | |
| 4 | `POST /tasks` with a Pydantic `TaskCreate` model that reuses the checks in `tasks.py` | Pydantic models, request bodies, `ValueError` → HTTP 422 | |
| 5 | `PATCH /tasks/{id}` (complete, edit) and `DELETE /tasks/{id}`, 404 for unknown IDs | Path parameters, HTTP methods, status codes | |
| 6 | `GET /tasks/today`, `/tasks/week`, and `GET /tasks?status=open&category=work` | Query parameters | |
| 7 | Tests with FastAPI's `TestClient` and an in-memory database | Testing an API, overriding dependencies | |
| 8 | Update this README and commit | | |

After this milestone, Version 3 (AI assistant) becomes a `POST /assistant/propose` endpoint that returns proposed tasks without saving them, plus a confirm call that saves them through the same checks.

### What was learned in step 1

- An API lets other programs (browser, Nuxt app, AI assistant) use the agenda over HTTP: a client sends a request (method + path, e.g. `GET /health`) and the server returns a response (status code + body).
- Status codes: `2xx` worked, `4xx` client mistake (`404` Not Found, `400` Bad Request, `422` invalid data), `5xx` server bug.
- `@app.get("/health")` is a decorator: it connects the function below it to that endpoint.
- Endpoints `return` data instead of using `print()`: `print()` only reaches the server's terminal, never the client.
- FastAPI converts returned dictionaries and lists to JSON automatically (`True` → `true`, `None` → `null`). A tuple becomes a JSON array.
- `curl -i http://127.0.0.1:8000/health` shows the response headers, including `content-type: application/json`.

### Where to start next time

1. **Fix the open bug in `api.py`:** the `/health` line ends with a trailing comma (`return {...},`), so it returns a tuple and the JSON comes back wrapped in `[ ]`. Remove the comma and check the result.
2. **Commit step 1** (`api.py` and `requirements.txt` are not committed yet).
3. **Open question:** why is FastAPI in `requirements.txt` but pytest in `requirements-dev.txt`?
4. **Step 2 exercise:** add `GET /tasks` to `api.py`:
   - `import database` at the top.
   - Decorate a function such as `list_tasks()` with `@app.get("/tasks")`.
   - Open a connection with `database.connect()`, get the rows with `database.get_tasks(connection)`, convert each `sqlite3.Row` with `dict(row)` (try a list comprehension: `[something(x) for x in items]`), and return the list.
   - Close the connection in a `finally` block, like `main()` in `agenda.py`.
5. **Step 2 experiments:**
   - Return the rows *without* `dict()` and read the error in the browser and the server terminal. Then put `dict()` back.
   - Is `completed` shown as `true`/`false` or `0`/`1`? Why (see `CREATE TABLE` in `database.py`)? What would a JavaScript frontend prefer? (Step 4 fixes this with Pydantic.)
   - Add a task with `python agenda.py`, then reload `/tasks`: both interfaces share `agenda.db`.

## 2. Learning objectives

By the end of this project, I want to understand:

**Python**

- Variables, data types, lists, and dictionaries.
- Conditions, loops, and functions.
- Modules, packages, and virtual environments.
- Dates and times.
- Reading and writing files.
- Error handling and debugging.
- Classes and object-oriented programming when appropriate.
- Automated testing and clean code.

**Application development**

- Building a simple user interface.
- Separating the interface, business logic, and data storage.
- Persisting data in a database.
- Using Git and GitHub.
- Managing dependencies and configuration.
- Debugging and testing an application.

**LLMs and AI**

- What LLMs are and how they generate text.
- Tokens, context windows, and prompts.
- Calling an LLM through an API.
- Structured outputs and JSON.
- Embeddings and semantic similarity.
- Retrieval-Augmented Generation (RAG).
- Tool calling and AI agents.
- Evaluating AI responses, handling errors, and managing costs.
- Exploring transformers and attention mechanisms at a later stage.
- Experimenting with local models and model training if appropriate.

## 3. Technology stack

Use a simple, beginner-friendly stack.

- **Language:** Python.
- **Development environment:** GitHub Codespaces.
- **Coding assistant:** GitHub Copilot.
- **Interface:** a terminal menu now, plus a web API built with FastAPI (in progress); later a Nuxt (Vue) web interface connected to that API.
- **Database:** SQLite.
- **Data validation:** Python standard library initially; Pydantic arrives with FastAPI (step 4 of the web API milestone).
- **LLM integration:** a provider API, introduced after the basic agenda works.
- **Version control:** Git and GitHub.
- **Testing:** pytest, introduced gradually.

Prefer simple, established tools over unnecessary frameworks.

Do not introduce complex infrastructure, microservices, Docker, orchestration frameworks, or vector databases until there is a clear learning or product reason to do so.

## 4. Application features

### Version 1 — Basic agenda ✅

- Add a task.
- Display all tasks.
- Mark a task as completed.
- Edit and delete tasks.
- Assign a due date.
- Store tasks persistently.

### Version 2 — Personal planning ✅

- Display today's agenda.
- Display the next seven days.
- Add priorities and categories.
- Filter tasks by status, date, and category.
- Identify overdue tasks.
- Create a weekly overview.

### Version 2.5 — Web API with FastAPI (in progress)

- Expose the agenda as a web API next to the terminal menu.
- Validate request data with Pydantic, reusing the rules in `tasks.py`.
- Test the API with FastAPI's `TestClient`.

See [Next milestone: web API with FastAPI](#next-milestone-web-api-with-fastapi-in-progress) for the step-by-step plan.

### Version 3 — AI assistant

Allow the user to describe tasks in natural language.

Example:

> "I need to prepare a presentation by Friday, buy groceries tomorrow, and exercise twice this week."

The assistant should:

1. Interpret the request.
2. Identify proposed tasks and dates.
3. Return structured task data.
4. Validate the proposed data.
5. Ask the user to confirm.
6. Save the approved tasks through normal Python application logic.

The application must not save arbitrary AI-generated data without validation.

### Version 4 — Understanding LLMs

- Experiment with different prompts.
- Examine structured outputs.
- Compare model responses.
- Learn about tokens and context limits.
- Measure response time and API usage.
- Explore embeddings and semantic search.
- Build a small RAG feature using my own agenda data.

Example question:

> "What tasks have I postponed several times, and what should I prioritize this week?"

The application should retrieve relevant records before asking the LLM to generate an answer.

### Version 5 — AI planning assistant

- Suggest a realistic weekly schedule.
- Identify conflicts and overloaded days.
- Suggest priorities based on deadlines.
- Summarize the previous week.
- Allow the assistant to request specific application tools.
- Require user approval for consequential changes.

### Version 6 — Advanced learning

When the foundations are solid, explore:

- Transformer architecture.
- Self-attention and attention mechanisms.
- Tokenization and embeddings in more depth.
- Running a small local language model.
- Fine-tuning concepts and small experiments.
- Evaluating model quality and reliability.

These are optional advanced topics, not prerequisites for building the application.

## 5. Architecture principles

Keep the initial architecture simple.

Separate the application into three main responsibilities:

- **User interface:** the terminal menu now (`agenda.py`); later, Nuxt pages, forms, and displays.
- **Application logic:** task creation, validation, planning, and business rules (`tasks.py`).
- **Data and AI services:** SQLite access (`database.py`) and, later, LLM API integration.

Keep AI-specific code separate from the core task management logic.

The basic task management features must continue working even when the LLM API is unavailable.

Use SQLite as the initial database. Keep schema changes in `database.migrate()`, and introduce a migration tool or a more advanced database only when needed.

## 6. How I want GitHub Copilot to teach me

Moved to [`.github/copilot-instructions.md`](.github/copilot-instructions.md), which Copilot reads automatically.

## 7. LLM integration and security

Follow these rules when adding AI functionality:

- Never hardcode API keys or credentials in source code.
- Store secrets in environment variables or GitHub Codespaces secrets.
- Never commit `.env` files or credentials to Git.
- Keep API calls behind a small, clearly defined Python module.
- Validate AI-generated data before using it.
- Treat model responses as untrusted input.
- Handle API errors, timeouts, and rate limits.
- Keep API costs and token usage visible during development.
- Avoid sending unnecessary personal information to external AI services.
- Require explicit user confirmation before performing important actions.
- Keep a deterministic, non-AI fallback for essential agenda operations.

Use mock responses initially if that helps me learn without spending money on API calls.

## 8. Development workflow

Work in small, verifiable increments.

For every feature:

1. Explain the goal.
2. Identify the concepts I will learn.
3. Break the task into small steps.
4. Implement one step at a time.
5. Explain how to run the code.
6. Test the feature.
7. Review what I learned.
8. Commit the working changes to Git when appropriate.

Do not move to the next milestone until the current one works and I understand its basic implementation.

Keep the README updated as the project evolves.

## 9. Initial milestone (completed)

The first milestone has been completed and has since grown (SQLite storage, due dates, planning views). The original exercise is kept here for reference:

- Add a task.
- Display all tasks.
- Mark a task as completed.
- Keep tasks in memory while the program is running.

It used a simple terminal interface, with no LLM, database, or graphical interface, and was followed by persistent storage.

## 10. Definition of success

This project is successful if:

- I have an agenda application I actually use.
- I understand the main parts of its code.
- I can add a feature without relying entirely on generated code.
- I know how to debug common problems.
- I understand how the application communicates with an LLM.
- I can explain the basic principles behind embeddings, RAG, and AI tool calling.
- I have a working foundation that I can continue improving.
