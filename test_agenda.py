from datetime import date

import pytest

import agenda
import database

TODAY = date(2026, 11, 13)


@pytest.fixture
def connection():
    connection = database.connect(":memory:")
    yield connection
    connection.close()


def titles(tasks):
    return [task["title"] for task in tasks]


def test_parse_due_date_accepts_valid_blank_and_rejects_invalid():
    assert agenda.parse_due_date(" 2026-12-31 ") == "2026-12-31"
    assert agenda.parse_due_date("   ") is None
    with pytest.raises(ValueError):
        agenda.parse_due_date("31/12/2026")
    with pytest.raises(ValueError):
        agenda.parse_due_date("2026-02-30")


def test_get_tasks_sorts_by_due_date_with_undated_last(connection):
    database.insert_task(connection, "no date")
    database.insert_task(connection, "later", "2026-12-01")
    database.insert_task(connection, "sooner", "2026-11-20")

    assert titles(database.get_tasks(connection)) == ["sooner", "later", "no date"]


def test_update_due_date_sets_and_clears(connection):
    database.insert_task(connection, "report", "2026-11-20")
    task_id = database.get_tasks(connection)[0]["id"]

    database.update_due_date(connection, task_id, "2026-11-25")
    assert database.get_tasks(connection)[0]["due_date"] == "2026-11-25"

    database.update_due_date(connection, task_id, None)
    assert database.get_tasks(connection)[0]["due_date"] is None


def test_overdue_excludes_completed_undated_today_and_future(connection):
    database.insert_task(connection, "late", "2026-11-12")
    database.insert_task(connection, "late but done", "2026-11-01")
    database.insert_task(connection, "due today", "2026-11-13")
    database.insert_task(connection, "future", "2026-11-14")
    database.insert_task(connection, "no date")
    done_id = next(t["id"] for t in database.get_tasks(connection) if t["title"] == "late but done")
    database.mark_completed(connection, done_id)

    assert titles(database.get_overdue_tasks(connection, TODAY.isoformat())) == ["late"]

    tasks = {task["title"]: task for task in database.get_tasks(connection)}
    assert agenda.is_overdue(tasks["late"], TODAY)
    assert not agenda.is_overdue(tasks["late but done"], TODAY)
    assert not agenda.is_overdue(tasks["due today"], TODAY)
    assert not agenda.is_overdue(tasks["no date"], TODAY)


def test_tasks_due_between_includes_both_ends(connection):
    for title, due in [("before", "2026-11-12"), ("first day", "2026-11-13"),
                       ("last day", "2026-11-19"), ("after", "2026-11-20")]:
        database.insert_task(connection, title, due)

    result = database.get_tasks_due_between(connection, "2026-11-13", "2026-11-19")
    assert titles(result) == ["first day", "last day"]


def test_show_today_lists_overdue_and_due_today(connection, capsys):
    database.insert_task(connection, "late", "2026-11-10")
    database.insert_task(connection, "now", "2026-11-13")
    database.insert_task(connection, "tomorrow", "2026-11-14")

    agenda.show_today(connection, TODAY)
    output = capsys.readouterr().out

    assert "late" in output and "now" in output
    assert "tomorrow" not in output


def test_show_next_seven_days_covers_today_through_day_seven(connection, capsys):
    database.insert_task(connection, "day one", "2026-11-13")
    database.insert_task(connection, "day seven", "2026-11-19")
    database.insert_task(connection, "day eight", "2026-11-20")

    agenda.show_next_seven_days(connection, TODAY)
    output = capsys.readouterr().out

    assert "day one" in output and "day seven" in output
    assert "day eight" not in output


def test_parse_priority_accepts_valid_blank_and_rejects_invalid():
    assert agenda.parse_priority("low") == "low"
    assert agenda.parse_priority("medium") == "medium"
    assert agenda.parse_priority("high") == "high"
    assert agenda.parse_priority("   ") == "medium"
    with pytest.raises(ValueError):
        agenda.parse_priority("urgent")
    with pytest.raises(ValueError):
        agenda.parse_priority("123")