My AI Agenda — Python & LLM Learning Project
1. Project vision

I want to build my own personal agenda application using Python. The application should help me organize tasks, plan my week, and eventually interact with an AI assistant using natural language.

This project is also my way of learning Python and understanding how Large Language Models (LLMs) work, from basic API usage to more advanced concepts such as embeddings, RAG, and AI agents.

The main goal is to build a genuinely useful application while understanding the code and AI concepts behind it.

## Current milestone: terminal agenda with SQLite storage

A small Python program that can add tasks, show them, mark them complete, and delete them. Tasks are saved in a local SQLite file (`agenda.db`, created automatically and ignored by Git), so they survive restarts.

Run it with Python 3.10 or newer:

```bash
python agenda.py
```

Choose an option from the menu. Try adding a task, completing or deleting one by its number, and then quitting. Restart the program to see that the tasks were saved. The numbers shown are positions in the list (1, 2, 3...); the program maps them to the real database IDs.

To inspect the data: `sqlite3 agenda.db "SELECT * FROM tasks;"`

### Concepts in this milestone

- The `sqlite3` module and a `tasks` table (`id`, `title`, `completed`).
- SQL `INSERT`, `SELECT`, `UPDATE`, and `DELETE`, with `?` placeholders for safe input.
- Functions separate adding, displaying, completing, and deleting tasks.
- `enumerate` numbers the displayed list; the chosen number is mapped back to the database ID.
- Input checks handle blank task names and invalid task numbers.

The next milestone is due dates, followed by planning features. The AI assistant comes after those foundations: it will propose structured tasks for you to review, and only confirmed, validated tasks will be saved.

I am a beginner, so the project must grow incrementally. Do not build the entire application at once.

2. Learning objectives

By the end of this project, I want to understand:

Python
Variables, data types, lists, and dictionaries.
Conditions, loops, and functions.
Modules, packages, and virtual environments.
Dates and times.
Reading and writing files.
Error handling and debugging.
Classes and object-oriented programming when appropriate.
Automated testing and clean code.
Application development
Building a simple user interface.
Separating the interface, business logic, and data storage.
Persisting data in a database.
Using Git and GitHub.
Managing dependencies and configuration.
Debugging and testing an application.
LLMs and AI
What LLMs are and how they generate text.
Tokens, context windows, and prompts.
Calling an LLM through an API.
Structured outputs and JSON.
Embeddings and semantic similarity.
Retrieval-Augmented Generation (RAG).
Tool calling and AI agents.
Evaluating AI responses, handling errors, and managing costs.
Exploring transformers and attention mechanisms at a later stage.
Experimenting with local models and model training if appropriate.
3. Technology stack

Use a simple, beginner-friendly stack.

Language: Python.
Development environment: GitHub Codespaces.
Coding assistant: GitHub Copilot.
Future interface: Nuxt (Vue), connected to a Python API after the core agenda works.
Database: SQLite.
Data validation: Python standard library initially; introduce Pydantic if it becomes useful.
LLM integration: A provider API, introduced after the basic agenda works.
Version control: Git and GitHub.
Testing: pytest, introduced gradually.

Prefer simple, established tools over unnecessary frameworks.

Do not introduce complex infrastructure, microservices, Docker, orchestration frameworks, or vector databases until there is a clear learning or product reason to do so.

4. Application features
Version 1 — Basic agenda
Add a task.
Display all tasks.
Mark a task as completed.
Edit and delete tasks.
Assign a due date.
Store tasks persistently.
Version 2 — Personal planning
Display today's agenda.
Display the next seven days.
Add priorities and categories.
Filter tasks by status, date, and category.
Identify overdue tasks.
Create a weekly overview.
Version 3 — AI assistant

Allow the user to describe tasks in natural language.

Example:

"I need to prepare a presentation by Friday, buy groceries tomorrow, and exercise twice this week."

The assistant should:

Interpret the request.
Identify proposed tasks and dates.
Return structured task data.
Validate the proposed data.
Ask the user to confirm.
Save the approved tasks through normal Python application logic.

The application must not save arbitrary AI-generated data without validation.

Version 4 — Understanding LLMs
Experiment with different prompts.
Examine structured outputs.
Compare model responses.
Learn about tokens and context limits.
Measure response time and API usage.
Explore embeddings and semantic search.
Build a small RAG feature using my own agenda data.

Example question:

"What tasks have I postponed several times, and what should I prioritize this week?"

The application should retrieve relevant records before asking the LLM to generate an answer.

Version 5 — AI planning assistant
Suggest a realistic weekly schedule.
Identify conflicts and overloaded days.
Suggest priorities based on deadlines.
Summarize the previous week.
Allow the assistant to request specific application tools.
Require user approval for consequential changes.
Version 6 — Advanced learning

When the foundations are solid, explore:

Transformer architecture.
Self-attention and attention mechanisms.
Tokenization and embeddings in more depth.
Running a small local language model.
Fine-tuning concepts and small experiments.
Evaluating model quality and reliability.

These are optional advanced topics, not prerequisites for building the application.

5. Architecture principles

Keep the initial architecture simple.

Separate the application into three main responsibilities:

User interface: Streamlit pages, forms, and displays.
Application logic: Task creation, validation, planning, and business rules.
Data and AI services: SQLite access and LLM API integration.

Keep AI-specific code separate from the core task management logic.

The basic task management features must continue working even when the LLM API is unavailable.

Use SQLite as the initial database. Introduce migrations or a more advanced database only when needed.

6. How I want GitHub Copilot to teach me

These instructions are important.

Act as my Python tutor and coding partner, not just a code generator.

I want to learn by building small, useful features.

Follow these rules:

Start by explaining the objective of each task in plain English.
Introduce no more than one or two major new concepts at a time.
Before writing code, explain the approach and why it is appropriate.
Prefer small, understandable implementations over clever or overly abstract solutions.
Explain important lines of code and new syntax.
Give me small exercises or questions that encourage me to write some code myself.
Let me attempt a solution before providing the complete answer when practical.
When modifying existing code, explain which files change and why.
Do not rewrite the entire application to implement one small feature.
Explain errors and debugging techniques instead of simply replacing broken code.
Ask me to run and test each feature before moving on.
Introduce automated tests gradually.
Explain important design trade-offs without overwhelming me with theory.
Relate new concepts to features in my agenda.
If I ask for a complete solution, provide it, but explain how it works.
Never claim that code works without a reasonable way to verify it.

At each milestone, summarize:

What I built.
What Python concepts I learned.
What AI concepts I learned.
What I should be able to explain independently.
What the next small step will be.
7. LLM integration and security

Follow these rules when adding AI functionality:

Never hardcode API keys or credentials in source code.
Store secrets in environment variables or GitHub Codespaces secrets.
Never commit .env files or credentials to Git.
Keep API calls behind a small, clearly defined Python module.
Validate AI-generated data before using it.
Treat model responses as untrusted input.
Handle API errors, timeouts, and rate limits.
Keep API costs and token usage visible during development.
Avoid sending unnecessary personal information to external AI services.
Require explicit user confirmation before performing important actions.
Keep a deterministic, non-AI fallback for essential agenda operations.

Use mock responses initially if that helps me learn without spending money on API calls.

8. Development workflow

Work in small, verifiable increments.

For every feature:

Explain the goal.
Identify the concepts I will learn.
Break the task into small steps.
Implement one step at a time.
Explain how to run the code.
Test the feature.
Review what I learned.
Commit the working changes to Git when appropriate.

Do not move to the next milestone until the current one works and I understand its basic implementation.

Keep the README updated as the project evolves.

9. Initial milestone

Start with the smallest useful version of the agenda. This milestone is implemented in `agenda.py`.

Create a Python program that allows me to:

Add a task.
Display all tasks.
Mark a task as completed.
Keep tasks in memory while the program is running.

Use a simple terminal interface initially if that makes the first lesson easier.

Do not introduce an LLM, database, or graphical interface in this first exercise.

Teach me the relevant concepts while building it. Once the basic version works, introduce persistent storage and then Streamlit.

10. Definition of success

This project is successful if:

I have an agenda application I actually use.
I understand the main parts of its code.
I can add a feature without relying entirely on generated code.
I know how to debug common problems.
I understand how the application communicates with an LLM.
I can explain the basic principles behind embeddings, RAG, and AI tool calling.
I have a working foundation that I can continue improving.

Start with Milestone 1. Explain the first exercise before generating the code.