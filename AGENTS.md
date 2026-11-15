
# Project Instructions — Smart Lost & Found Portal

## 1. Project Context

We are building a Smart Lost & Found Management Portal using:

- Python 3.11+
- Flask 3.x
- SQLite 3 with WAL mode
- Vanilla HTML, CSS and JavaScript

The complete project specification is defined in PRD.md.
Always consult PRD.md before implementing a feature.

## 2. Developer Ownership

I am Developer 1 (Jatin Rawat).

My exclusive responsibilities are:

- database/
- algorithms/
- tests/

Never create, modify or delete files inside:

- routes/
- templates/
- static/

These directories belong to Developer 2.

The following files are shared/frozen. Do not modify them without explicit approval:

- .gitignore
- .gitattributes
- PRD.md
- config.py
- app.py

## 3. Algorithm Implementation Rules

- Implement all DAA algorithms from scratch in pure Python.
- Do not use networkx, scipy or external graph/string-matching libraries.
- Standard Python libraries are allowed, including heapq, collections, math and time.
- Follow the exact function signatures and result structures defined in PRD.md.
- Never independently change a frozen function signature or API contract.
- Use meaningful variable names and clear comments.
- Handle edge cases and invalid inputs appropriately.

## 4. Database Rules

All database work belongs inside database/.

- Follow the exact schema defined in PRD.md.
- Use SQLite WAL mode.
- Enable foreign key constraints.
- Set synchronous=NORMAL.
- Set busy_timeout=5000.
- Use parameterized SQL queries.
- Never commit database files (*.db, *.db-wal, *.db-shm).
- Keep seed data deterministic.

## 5. Telemetry Rules

Every exported algorithm must return the standardized envelope:

{
    "result": {},
    "telemetry": {
        "algorithm": "...",
        "unit": "...",
        "input_size": 0,
        "time_ms": 0.0,
        "complexity": "..."
    }
}

Use the @measure_daa decorator from algorithms/metrics.py.

Follow the exact telemetry contract in PRD.md.

## 6. Code Quality

- Follow PEP 8 conventions.
- Use 4-space indentation.
- Write modular and reusable functions.
- Avoid unnecessary dependencies.
- Add tests for every algorithm.
- Test empty inputs, boundary cases and normal inputs.
- Do not silently change existing behavior.

## 7. Git Rules

- Never commit directly to main.
- Developer 1 branches must start with dev1/.
- Use meaningful commit messages.
- Do not commit .venv/, __pycache__/ or SQLite database files.
- Do not modify another developer's files to fix an integration issue.

## 8. Working Procedure

Before writing code:

1. Inspect the existing project structure.
2. Read the relevant PRD section.
3. Explain the implementation approach briefly.
4. Implement only the requested task.
5. Run relevant tests.
6. Report changed files and test results.

Do not generate the entire project at once.

Work incrementally, one module or feature at a time.
