from datetime import date, timedelta

REVISION_STAGES = {
    0: "Immediate",
    1: "1 Day",
    2: "1 Week",
    3: "1 Month",
    4: "Completed",
}


def get_stage_name(stage: int) -> str:
    return REVISION_STAGES.get(stage, "Unknown")


def get_next_revision_date(
    current_stage: int,
    revision_date: date,
) -> date | None:
    if current_stage == 0:
        return revision_date + timedelta(days=1)

    if current_stage == 1:
        return revision_date + timedelta(days=7)

    if current_stage == 2:
        return revision_date + timedelta(days=30)

    return None


def get_next_stage(current_stage: int) -> int:
    if current_stage >= 3:
        return 4

    return current_stage + 1
