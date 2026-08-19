import streamlit as st
from datetime import date, datetime
from urllib.parse import urlparse

from database import (
    initialize_database,
    add_problem,
    get_due_problems,
    get_all_problems,
    mark_problem_revised,
    get_revision_history,
    get_statistics,
)
from scheduler import get_stage_name

st.set_page_config(
    page_title="Problem Revision Tracker",
    page_icon="🧠",
    layout="wide",
)

initialize_database()


def format_date(value):
    if not value:
        return "—"
    try:
        return date.fromisoformat(value).strftime("%d %b %Y")
    except ValueError:
        return value


def is_valid_url(url):
    if not url:
        return True
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def stage_badge(stage):
    names = {
        0: "🔵 Immediate",
        1: "🟡 1 Day",
        2: "🟠 1 Week",
        3: "🔴 1 Month",
        4: "🟢 Completed",
    }
    return names.get(stage, "Unknown")


st.sidebar.title("🧠 Revision Tracker")
page = st.sidebar.radio(
    "Navigate",
    ["Today's Revisions", "Add Problem", "All Problems"],
)
st.sidebar.divider()
st.sidebar.caption("i111 = Immediate → 1 Day → 1 Week → 1 Month")


if page == "Today's Revisions":
    st.title("Today's Revisions")
    today = date.today()
    st.caption(f"Today: {today.strftime('%A, %d %B %Y')}")

    stats = get_statistics()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Due Today", stats["due"])
    with col2:
        st.metric("Total Problems", stats["total"])
    with col3:
        st.metric("Completed Cycles", stats["completed"])
    with col4:
        st.metric("Revisions Today", stats["revisions_today"])

    st.divider()
    problems = get_due_problems()

    if not problems:
        st.success("No revisions are due today. Your revision queue is clear.")
    else:
        st.subheader(f"{len(problems)} problem(s) to revise")

        for problem in problems:
            with st.container(border=True):
                col1, col2 = st.columns([5, 1])

                with col1:
                    st.markdown(f"### {problem['title']}")

                    if problem["description"]:
                        st.write(problem["description"])

                    if problem["topic"]:
                        st.caption(f"Topic: {problem['topic']}")

                    st.write(f"**Revision:** {stage_badge(problem['current_stage'])}")
                    st.caption(
                        f"Originally solved: {format_date(problem['created_at'])}"
                    )

                    scheduled = problem["next_revision_date"]
                    if scheduled:
                        scheduled_date = date.fromisoformat(scheduled)
                        if scheduled_date < today:
                            days_late = (today - scheduled_date).days
                            st.warning(
                                f"Overdue by {days_late} day(s). "
                                f"Scheduled for {format_date(scheduled)}."
                            )

                    if problem["link"]:
                        if is_valid_url(problem["link"]):
                            st.link_button("🔗 Open Problem", problem["link"])
                        else:
                            st.warning("The saved link is not a valid URL.")

                with col2:
                    st.write("")
                    if st.button(
                        "✓ Mark Revised",
                        key=f"revise_{problem['id']}",
                        type="primary",
                        use_container_width=True,
                    ):
                        if mark_problem_revised(problem["id"]):
                            st.success("Revision recorded.")
                            st.rerun()


elif page == "Add Problem":
    st.title("Add New Problem")
    st.write(
        "Record a problem you solved today. "
        "The app will automatically create the i111 schedule."
    )

    with st.form("add_problem_form"):
        title = st.text_input(
            "Problem title *",
            placeholder="e.g. Binary Search - Rotated Array",
        )
        link = st.text_input(
            "Problem link",
            placeholder="https://leetcode.com/...",
        )
        description = st.text_area(
            "Short description",
            placeholder=(
                "Optional: problem statement, key idea, or "
                "anything useful for identifying it."
            ),
        )
        topic = st.text_input(
            "Topic",
            placeholder="e.g. Binary Search",
        )

        submitted = st.form_submit_button(
            "Add Problem",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            if not title.strip():
                st.error("Please enter a problem title.")
            elif not is_valid_url(link.strip()):
                st.error(
                    "Please enter a valid URL beginning with "
                    "http:// or https://."
                )
            else:
                problem_id = add_problem(
                    title=title,
                    description=description,
                    link=link,
                    topic=topic,
                )
                st.success(
                    f"Problem #{problem_id} added. "
                    "Its Immediate revision is due today."
                )
                st.info(
                    "Schedule: Immediate → 1 Day → 1 Week → 1 Month."
                )


elif page == "All Problems":
    st.title("All Problems")
    problems = get_all_problems()

    if not problems:
        st.info("No problems have been added yet.")
    else:
        search = st.text_input(
            "Search problems",
            placeholder="Search by title, description, or topic...",
        )

        filtered = []
        query = search.lower()

        for problem in problems:
            searchable = " ".join([
                problem["title"] or "",
                problem["description"] or "",
                problem["topic"] or "",
            ]).lower()

            if query in searchable:
                filtered.append(problem)

        st.caption(f"Showing {len(filtered)} of {len(problems)} problems")

        for problem in filtered:
            icon = "🟢" if problem["completed"] else "📚"

            with st.expander(f"{icon} {problem['title']}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(
                        f"**Status:** {stage_badge(problem['current_stage'])}"
                    )
                    st.write(f"**Solved:** {format_date(problem['created_at'])}")

                    if problem["topic"]:
                        st.write(f"**Topic:** {problem['topic']}")

                with col2:
                    if problem["completed"]:
                        st.success("i111 cycle completed")
                    else:
                        st.write(
                            f"**Next revision:** "
                            f"{format_date(problem['next_revision_date'])}"
                        )

                    if problem["link"] and is_valid_url(problem["link"]):
                        st.link_button("🔗 Open Problem", problem["link"])

                if problem["description"]:
                    st.markdown("**Description**")
                    st.write(problem["description"])

                st.divider()
                st.markdown("**Revision History**")

                history = get_revision_history(problem["id"])

                if not history:
                    st.caption("No revisions completed yet.")
                else:
                    for revision in history:
                        completed = datetime.fromisoformat(
                            revision["completed_at"]
                        ).strftime("%d %b %Y, %I:%M %p")

                        st.write(
                            f"✓ **{get_stage_name(revision['stage'])}** — "
                            f"scheduled {format_date(revision['scheduled_date'])} "
                            f"— completed {completed}"
                        )
