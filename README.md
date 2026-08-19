# 🧠 Problem Revision Tracker

A lightweight spaced-repetition web application for tracking and revising coding/DSA problems using the **i111 revision technique — Immediate, 1 Day, 1 Week, and 1 Month**.

The application automatically schedules revisions, tracks revision history, handles overdue problems, and provides a simple dashboard for managing a personal problem-solving revision workflow.

---

## 🚀 Project Overview

When solving a large number of coding problems, remembering to revisit previously solved problems can be difficult.

**Problem Revision Tracker** automates this process using a spaced-repetition schedule.

When a problem is added, the application automatically creates the following revision cycle:

```text
Problem Solved
      │
      ▼
 Immediate Revision
      │
      ▼
   +1 Day
      │
      ▼
   +1 Week
      │
      ▼
   +1 Month
      │
      ▼
   Completed
```

The application maintains the revision schedule in a SQLite database and presents all currently due or overdue problems through an interactive Streamlit dashboard.

---

## ✨ Features

* **Automated i111 Scheduling**

  * Immediate revision
  * 1-day revision
  * 1-week revision
  * 1-month revision

* **Automatic Revision Tracking**

  * Mark a revision as completed with one click
  * Automatically calculate the next revision date
  * Track the current revision stage

* **Overdue Revision Handling**

  * Automatically identify missed revisions
  * Display the number of days a revision is overdue
  * Reschedule the next revision based on the actual completion date

* **Problem Management**

  * Store problem title
  * Store problem URL
  * Add a short description
  * Categorize problems by topic

* **Revision History**

  * Record every completed revision
  * Store scheduled and actual completion dates
  * Track the complete i111 cycle

* **Dashboard**

  * Problems due today
  * Total problems
  * Completed i111 cycles
  * Revisions completed today

* **Search**

  * Search problems by title, description, or topic

* **Persistent Storage**

  * SQLite database
  * No external database server required

---

## 🛠️ Tech Stack

| Technology        | Purpose                              |
| ----------------- | ------------------------------------ |
| **Python**        | Core application logic               |
| **Streamlit**     | Interactive web interface            |
| **SQLite**        | Persistent data storage              |
| **SQL**           | Database queries and data management |
| **HTML/Markdown** | Streamlit-rendered interface         |
| **Git/GitHub**    | Version control and project hosting  |

---

## 🏗️ Architecture

The project follows a simple modular architecture:

```text
                    ┌─────────────────────┐
                    │      Streamlit      │
                    │       app.py        │
                    │                     │
                    │  User Interface     │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
      ┌──────────────────┐          ┌──────────────────┐
      │    scheduler.py  │          │    database.py   │
      │                  │          │                  │
      │ i111 scheduling  │          │ Database CRUD    │
      │ stage transitions│          │ Revision history │
      └────────┬─────────┘          └────────┬─────────┘
               │                             │
               │                             ▼
               │                    ┌──────────────────┐
               └───────────────────►│     SQLite       │
                                    │   revision.db    │
                                    └──────────────────┘
```

### Module Responsibilities

#### `app.py`

Handles the Streamlit user interface:

* Dashboard
* Add Problem page
* Today's Revisions
* All Problems
* Search
* Revision actions

#### `scheduler.py`

Contains the i111 scheduling logic:

```text
Stage 0 → Immediate
Stage 1 → +1 Day
Stage 2 → +1 Week
Stage 3 → +1 Month
Stage 4 → Completed
```

#### `database.py`

Handles:

* SQLite connection
* Problem creation
* Retrieving due problems
* Updating revision stages
* Revision history
* Statistics

---

## 🗄️ Database Design

The application uses two SQLite tables.

### `problems`

Stores the current state of every problem.

```text
problems
├── id
├── title
├── description
├── link
├── topic
├── created_at
├── current_stage
├── next_revision_date
└── completed
```

### `revision_history`

Stores every completed revision.

```text
revision_history
├── id
├── problem_id
├── stage
├── scheduled_date
└── completed_at
```

This separation allows the application to maintain both the **current revision state** and a **historical record of completed revisions**.

---

## 🔄 Revision Workflow

Suppose a problem is solved on:

```text
8 August
```

The application creates:

| Stage     | Scheduled Date |
| --------- | -------------- |
| Immediate | 8 August       |
| 1 Day     | 9 August       |
| 1 Week    | 16 August      |
| 1 Month   | 15 September   |

The next revision is calculated only after the current revision is marked as completed.

### Overdue Handling

If a revision was scheduled for 9 August but is completed on 11 August, the application treats 11 August as the actual revision date and calculates the next interval from that date.

This prevents missed revisions from breaking the revision cycle.

---

## 📸 Screenshots

### Dashboard

> Add a screenshot of the **Today's Revisions** page here.

```text
docs/screenshots/dashboard.png
```

### Add Problem

> Add a screenshot of the **Add Problem** page here.

```text
docs/screenshots/add-problem.png
```

### Revision History

> Add a screenshot of the **All Problems / Revision History** page here.

```text
docs/screenshots/revision-history.png
```

### Adding Screenshots

Create this folder:

```text
docs/
└── screenshots/
    ├── dashboard.png
    ├── add-problem.png
    └── revision-history.png
```

Then replace the screenshot placeholders in this README with:

```markdown
![Dashboard](docs/screenshots/dashboard.png)

![Add Problem](docs/screenshots/add-problem.png)

![Revision History](docs/screenshots/revision-history.png)
```

---

## 💻 Installation & Setup

### Prerequisites

Make sure you have:

* Python 3.10 or newer
* pip

Check your Python version:

```bash
python --version
```

---

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/problem-revision-tracker.git
cd problem-revision-tracker
```

Replace `YOUR_USERNAME` with your GitHub username.

---

### 2. Create a virtual environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Run the application

```bash
streamlit run app.py
```

The application will be available at:

```text
http://localhost:8501
```

---

## 📁 Project Structure

```text
problem-revision-tracker/
│
├── app.py
│
├── database.py
│
├── scheduler.py
│
├── requirements.txt
│
├── README.md
│
└── docs/
    └── screenshots/
```

The SQLite database (`revision.db`) is generated automatically when the application runs and is intended to remain local.

---

## 🎯 Example Usage

### 1. Add a problem

Enter:

```text
Title:
Binary Search - Rotated Array

Link:
https://leetcode.com/...

Topic:
Binary Search
```

### 2. Complete the immediate revision

The problem appears under **Today's Revisions**.

Click:

```text
✓ Mark Revised
```

The application automatically schedules the next revision.

### 3. Return later

The dashboard automatically shows problems whose revision date has arrived.

No manual calendar management is required.

---

## 🔮 Future Improvements

Potential extensions include:

* User authentication
* Cloud deployment
* PostgreSQL support
* REST API
* Mobile-friendly interface
* Calendar-based revision visualization
* Advanced analytics
* Difficulty-based filtering
* Topic-wise statistics
* Customizable spaced-repetition intervals
* Export/import of problem data

---

## 📌 Key Learning Outcomes

This project demonstrates practical experience with:

* Python application development
* Streamlit web application development
* SQLite database design
* SQL queries and persistent storage
* State-based scheduling logic
* CRUD operations
* Date/time manipulation
* Modular application architecture
* Interactive dashboards
* Git/GitHub project management

---

## 📄 License

This project is open-source and available for educational and personal use.
