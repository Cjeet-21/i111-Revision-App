import sqlite3
from datetime import date, datetime
from pathlib import Path

from scheduler import get_next_revision_date, get_next_stage

DATABASE_PATH = Path(__file__).parent / "revision.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            link TEXT,
            topic TEXT,
            created_at TEXT NOT NULL,
            current_stage INTEGER NOT NULL DEFAULT 0,
            next_revision_date TEXT,
            completed INTEGER NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS revision_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id INTEGER NOT NULL,
            stage INTEGER NOT NULL,
            scheduled_date TEXT NOT NULL,
            completed_at TEXT NOT NULL,
            FOREIGN KEY (problem_id) REFERENCES problems(id)
        )
    """)

    connection.commit()
    connection.close()


def add_problem(title, description="", link="", topic=""):
    today = date.today()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO problems (
            title, description, link, topic,
            created_at, current_stage,
            next_revision_date, completed
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title.strip(),
        description.strip(),
        link.strip(),
        topic.strip(),
        today.isoformat(),
        0,
        today.isoformat(),
        0,
    ))

    problem_id = cursor.lastrowid
    connection.commit()
    connection.close()

    return problem_id


def get_due_problems():
    today = date.today().isoformat()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM problems
        WHERE completed = 0
          AND next_revision_date <= ?
        ORDER BY next_revision_date ASC, id ASC
    """, (today,))

    problems = cursor.fetchall()
    connection.close()
    return problems


def get_all_problems():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM problems
        ORDER BY completed ASC,
                 next_revision_date ASC,
                 created_at DESC
    """)

    problems = cursor.fetchall()
    connection.close()
    return problems


def mark_problem_revised(problem_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM problems WHERE id = ?",
        (problem_id,),
    )
    problem = cursor.fetchone()

    if problem is None:
        connection.close()
        return False

    current_stage = problem["current_stage"]
    scheduled_date = problem["next_revision_date"]
    completed_at = datetime.now().isoformat(timespec="seconds")

    cursor.execute("""
        INSERT INTO revision_history (
            problem_id, stage, scheduled_date, completed_at
        )
        VALUES (?, ?, ?, ?)
    """, (
        problem_id,
        current_stage,
        scheduled_date,
        completed_at,
    ))

    next_stage = get_next_stage(current_stage)

    if next_stage >= 4:
        cursor.execute("""
            UPDATE problems
            SET current_stage = ?,
                next_revision_date = NULL,
                completed = 1
            WHERE id = ?
        """, (4, problem_id))
    else:
        # Schedule from the date the user actually completed the revision.
        next_date = get_next_revision_date(current_stage, date.today())

        cursor.execute("""
            UPDATE problems
            SET current_stage = ?,
                next_revision_date = ?,
                completed = 0
            WHERE id = ?
        """, (
            next_stage,
            next_date.isoformat(),
            problem_id,
        ))

    connection.commit()
    connection.close()
    return True


def get_revision_history(problem_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM revision_history
        WHERE problem_id = ?
        ORDER BY completed_at ASC
    """, (problem_id,))

    history = cursor.fetchall()
    connection.close()
    return history


def get_statistics():
    connection = get_connection()
    cursor = connection.cursor()
    today = date.today().isoformat()

    cursor.execute("SELECT COUNT(*) FROM problems")
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM problems
        WHERE completed = 0
          AND next_revision_date <= ?
    """, (today,))
    due = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM problems
        WHERE completed = 1
    """)
    completed = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM revision_history
        WHERE DATE(completed_at) = ?
    """, (today,))
    revisions_today = cursor.fetchone()[0]

    connection.close()

    return {
        "total": total,
        "due": due,
        "completed": completed,
        "revisions_today": revisions_today,
    }
