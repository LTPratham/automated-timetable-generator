"""Export individual faculty and batch timetables to standard iCalendar (.ics) files."""

from datetime import datetime, date, timedelta, timezone
from typing import Dict
from src.models.entities import SessionVariable, SlotAssignment
from src.models.dataset import DepartmentDataset


DAY_MAP = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
}


def export_timetable_to_ics(
    dataset: DepartmentDataset,
    assignment: Dict[SessionVariable, SlotAssignment],
    faculty_id: str = None,
    batch_id: str = None,
) -> str:
    """
    Generates a standard RFC 5545 iCalendar format string.
    Can be imported directly into Google Calendar, Apple Calendar, or Outlook.
    """
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Automated Timetable CSP Generator//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Academic Schedule",
    ]

    # Reference week (e.g., upcoming Monday)
    today = date.today()
    days_ahead = (0 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    monday = today + timedelta(days=days_ahead)

    for var, assign in assignment.items():
        if faculty_id and var.faculty_id != faculty_id:
            continue
        if batch_id and var.batch_id != batch_id:
            continue

        day_offset = DAY_MAP.get(assign.day.value, 0)
        session_date = monday + timedelta(days=day_offset)

        start_time_str = dataset.slot_times[assign.start_slot_index][0]
        end_time_str = dataset.slot_times[assign.start_slot_index + assign.duration_slots - 1][1]

        start_dt = datetime.strptime(f"{session_date} {start_time_str}", "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(f"{session_date} {end_time_str}", "%Y-%m-%d %H:%M")

        fac = dataset.faculty_by_id.get(var.faculty_id)
        fac_name = fac.name if fac else var.faculty_id
        room = dataset.rooms_by_id.get(assign.room_id)
        room_name = room.name if room else assign.room_id

        uid = f"{var.variable_id}-{session_date.strftime('%Y%m%d')}@timetable.csp"
        dtstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        dtstart = start_dt.strftime("%Y%m%dT%H%M%S")
        dtend = end_dt.strftime("%Y%m%dT%H%M%S")

        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{dtstamp}",
                f"DTSTART:{dtstart}",
                f"DTEND:{dtend}",
                f"SUMMARY:{var.course_code}: {var.course_title}",
                f"DESCRIPTION:Batch: {var.batch_id}\\nFaculty: {fac_name}\\nType: {var.session_type.value}",
                f"LOCATION:{room_name}",
                "RRULE:FREQ=WEEKLY;COUNT=14",  # 14 weeks semester recurrence
                "END:VEVENT",
            ]
        )

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)
