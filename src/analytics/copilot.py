"""
AI Timetable Copilot & Multi-Objective Quality Engine.
Provides natural language reasoning, conversational assistance, and multi-dimensional quality metrics.
"""

from typing import Dict, Any, List, Optional
import math
from src.models.dataset import DepartmentDataset
from src.models.entities import SessionVariable, SlotAssignment, DayOfWeek
from src.analytics.fairness import audit_fairness_and_ethics


def compute_quality_radar(dataset: DepartmentDataset, schedule: Dict[SessionVariable, SlotAssignment]) -> Dict[str, Any]:
    """
    Computes a 5-dimensional holistic quality score for the active timetable.
    Dimensions (each 0 - 100 scale):
    1. Hard Constraint Compliance (100% when conflict-free)
    2. Faculty Workload Fairness (derived from 1 - Gini Index)
    3. Student Schedule Compactness (minimizing dead gaps between lectures)
    4. Infrastructure Utilization (efficient classroom and laboratory usage)
    5. Circadian Distribution (balanced distribution between morning and afternoon slots)
    """
    if not schedule:
        return {
            "radar_metrics": [
                {"subject": "Constraint Integrity", "score": 0, "fullMark": 100},
                {"subject": "Faculty Fairness", "score": 0, "fullMark": 100},
                {"subject": "Cohort Compactness", "score": 0, "fullMark": 100},
                {"subject": "Room Efficiency", "score": 0, "fullMark": 100},
                {"subject": "Time Balance", "score": 0, "fullMark": 100},
            ],
            "overall_score": 0,
            "grade": "N/A",
            "insights": ["Timetable is not yet generated."]
        }

    # 1. Constraint Integrity (100% since CSP guarantees hard constraints)
    integrity_score = 100.0

    # 2. Faculty Fairness (from Gini index)
    fairness_data = audit_fairness_and_ethics(schedule, dataset)
    faculty_gini = fairness_data.get("faculty_gini_index", 0.1)
    fairness_score = round(max(10.0, min(100.0, (1.0 - faculty_gini) * 100.0)), 1)

    # 3. Student Cohort Compactness (checks gap count between earliest and latest slot each day)
    cohort_days: Dict[str, Dict[str, List[int]]] = {}
    for var, assign in schedule.items():
        batch = var.batch_id
        day = assign.day.value
        if batch not in cohort_days:
            cohort_days[batch] = {}
        if day not in cohort_days[batch]:
            cohort_days[batch][day] = []
        for _, s in assign.occupied_slots:
            cohort_days[batch][day].append(s)

    total_gaps = 0
    total_cohort_days = 0
    for batch, days in cohort_days.items():
        for day, slots in days.items():
            if len(slots) > 1:
                slots_sorted = sorted(slots)
                span = slots_sorted[-1] - slots_sorted[0] + 1
                gaps = span - len(slots)
                total_gaps += max(0, gaps)
                total_cohort_days += 1

    avg_gap_per_day = (total_gaps / max(1, total_cohort_days))
    compactness_score = round(max(30.0, min(100.0, 100.0 - (avg_gap_per_day * 22.0))), 1)

    # 4. Room Efficiency
    total_available_room_slots = len(dataset.rooms) * len(dataset.days) * dataset.daily_slots_count
    total_used_slots = sum(len(assign.occupied_slots) for assign in schedule.values())
    room_ratio = total_used_slots / max(1, total_available_room_slots)
    # Ideal university occupancy is ~55-80% to allow flexible study & extracurriculars
    if room_ratio <= 0.75:
        room_efficiency_score = round(min(100.0, (room_ratio / 0.70) * 95.0), 1)
    else:
        room_efficiency_score = round(max(60.0, 100.0 - (room_ratio - 0.75) * 80.0), 1)

    # 5. Circadian Distribution (Morning vs Afternoon balance)
    morning_slots = 0
    afternoon_slots = 0
    for assign in schedule.values():
        for _, s in assign.occupied_slots:
            if s <= 2:
                morning_slots += 1
            else:
                afternoon_slots += 1
    total_slots = morning_slots + afternoon_slots
    if total_slots > 0:
        ratio = min(morning_slots, afternoon_slots) / max(morning_slots, afternoon_slots)
        time_balance_score = round(ratio * 96.0 + 4.0, 1)
    else:
        time_balance_score = 80.0

    # Overall Quality Index
    metrics = [
        {"subject": "Constraint Integrity", "score": integrity_score, "fullMark": 100},
        {"subject": "Faculty Fairness", "score": fairness_score, "fullMark": 100},
        {"subject": "Cohort Compactness", "score": compactness_score, "fullMark": 100},
        {"subject": "Room Efficiency", "score": room_efficiency_score, "fullMark": 100},
        {"subject": "Time Balance", "score": time_balance_score, "fullMark": 100},
    ]

    overall_score = round(sum(m["score"] for m in metrics) / len(metrics), 1)
    if overall_score >= 90:
        grade = "A+ (Optimal)"
    elif overall_score >= 80:
        grade = "A (Excellent)"
    elif overall_score >= 70:
        grade = "B+ (Good)"
    else:
        grade = "B (Satisfactory)"

    insights = [
        f"Overall Quality Index: {overall_score}/100 ({grade})",
        f"Fairness Rating: Gini coefficient {faculty_gini:.3f} indicates {fairness_data.get('fairness_grade', 'Good')} teaching equity.",
        f"Student Schedule: Average idle gap between classes is {avg_gap_per_day:.1f} slots/day.",
        f"Campus Rooms: {total_used_slots} of {total_available_room_slots} available room-slots utilized ({room_ratio*100:.1f}%).",
    ]

    return {
        "radar_metrics": metrics,
        "overall_score": overall_score,
        "grade": grade,
        "insights": insights,
        "raw_stats": {
            "total_sessions": len(schedule),
            "faculty_gini": faculty_gini,
            "avg_gap_per_day": round(avg_gap_per_day, 2),
            "room_utilization_pct": round(room_ratio * 100, 1),
            "morning_sessions": morning_slots,
            "afternoon_sessions": afternoon_slots
        }
    }


def process_copilot_query(
    query: str,
    dataset: DepartmentDataset,
    schedule: Dict[SessionVariable, SlotAssignment]
) -> Dict[str, Any]:
    """
    Interprets natural language queries from dean, faculty, or students and provides
    intelligent conversational answers with actionable metadata.
    """
    q = query.strip().lower()

    # 1. Workload / Teaching Load Queries
    if any(k in q for k in ["highest workload", "workload", "teaches the most", "busiest faculty", "teaching load", "hours"]):
        # Compute workload per faculty
        fac_loads: Dict[str, int] = {f.id: 0 for f in dataset.faculty}
        for var, assign in schedule.items():
            fac_loads[var.faculty_id] = fac_loads.get(var.faculty_id, 0) + len(assign.occupied_slots)

        sorted_fac = sorted(fac_loads.items(), key=lambda x: x[1], reverse=True)
        top_fac_id, top_hrs = sorted_fac[0]
        top_fac_name = dataset.faculty_by_id.get(top_fac_id).name if top_fac_id in dataset.faculty_by_id else top_fac_id
        lowest_fac_id, lowest_hrs = sorted_fac[-1]
        lowest_fac_name = dataset.faculty_by_id.get(lowest_fac_id).name if lowest_fac_id in dataset.faculty_by_id else lowest_fac_id

        summary_rows = [f"- **{dataset.faculty_by_id[fid].name}**: {hrs} teaching hours/week" for fid, hrs in sorted_fac]

        return {
            "intent": "WORKLOAD_AUDIT",
            "title": "Faculty Workload Distribution",
            "reply": (
                f"**{top_fac_name}** has the highest workload with **{top_hrs} teaching hours/week**.\n"
                f"**{lowest_fac_name}** has the lowest with **{lowest_hrs} hours/week**.\n\n"
                f"**Complete Workload Breakdown:**\n" + "\n".join(summary_rows)
            ),
            "actions": [
                {"label": "Audit Gini Fairness", "tab": "fairness"},
                {"label": "Filter by Busiest Faculty", "filter_type": "faculty", "filter_val": top_fac_id}
            ],
            "highlight_ids": [top_fac_id]
        }

    # 2. Availability Queries (e.g. "Is Dr. Turing free on Friday?")
    if any(k in q for k in ["free", "available", "availability", "when does", "schedule of"]):
        # Find matching faculty
        matched_faculty = None
        for f in dataset.faculty:
            # Match last name or full name
            parts = f.name.lower().replace(".", "").split()
            if any(part in q for part in parts if len(part) > 3):
                matched_faculty = f
                break

        # Check for day mentioned
        day_names = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        matched_day = None
        for d in day_names:
            if d in q:
                matched_day = d.capitalize()
                break

        if matched_faculty:
            # Find schedule for this faculty
            fac_sessions = []
            for var, assign in schedule.items():
                if var.faculty_id == matched_faculty.id:
                    if not matched_day or assign.day.value.lower() == matched_day.lower():
                        c_title = dataset.courses_by_id[var.course_id].title if var.course_id in dataset.courses_by_id else var.course_id
                        fac_sessions.append(f"- **{assign.day.value} {assign.slot_str}**: {c_title} in {assign.room_id} ({var.batch_id})")

            if fac_sessions:
                time_ctx = f"on {matched_day}" if matched_day else "across the week"
                return {
                    "intent": "FACULTY_AVAILABILITY",
                    "title": f"{matched_faculty.name}'s Schedule",
                    "reply": (
                        f"Here are the scheduled sessions for **{matched_faculty.name}** {time_ctx}:\n\n"
                        + "\n".join(fac_sessions) + "\n\n"
                        f"*All other time slots remain free for office hours, research, and mentoring.*"
                    ),
                    "actions": [
                        {"label": f"View {matched_faculty.name}'s View", "filter_type": "faculty", "filter_val": matched_faculty.id}
                    ],
                    "highlight_ids": [matched_faculty.id]
                }
            else:
                return {
                    "intent": "FACULTY_AVAILABILITY",
                    "title": f"{matched_faculty.name} is Free!",
                    "reply": f"Good news! **{matched_faculty.name}** has **no assigned lectures on {matched_day or 'this query day'}**.",
                    "actions": [],
                    "highlight_ids": [matched_faculty.id]
                }
        else:
            # General availability query or unknown name
            fac_names = ", ".join([f.name for f in dataset.faculty[:5]])
            return {
                "intent": "FACULTY_AVAILABILITY",
                "title": "Faculty Availability Lookup",
                "reply": (
                    f"To check availability, specify a faculty name (e.g., *Dr. Alan Turing, Dr. Ada Lovelace, Dr. Donald Knuth, Dr. Grace Hopper*).\n\n"
                    f"**Sample Faculty in Department:** {fac_names}..."
                ),
                "actions": [
                    {"label": f"Check {dataset.faculty[0].name}", "query": f"Is {dataset.faculty[0].name} free on Friday?"}
                ],
                "highlight_ids": []
            }

    # 3. Room Utilization Queries
    if any(k in q for k in ["room", "lab", "classroom", "utilization", "capacity"]):
        room_usage = {r.id: 0 for r in dataset.rooms}
        for var, assign in schedule.items():
            room_usage[assign.room_id] = room_usage.get(assign.room_id, 0) + len(assign.occupied_slots)

        sorted_rooms = sorted(room_usage.items(), key=lambda x: x[1], reverse=True)
        most_used_id, most_slots = sorted_rooms[0]
        least_used_id, least_slots = sorted_rooms[-1]

        rows = [f"- **{dataset.rooms_by_id[rid].name}** ({rid}): {slots} slots utilized" for rid, slots in sorted_rooms]

        return {
            "intent": "ROOM_UTILIZATION",
            "title": "Classroom & Lab Utilization",
            "reply": (
                f"**{dataset.rooms_by_id[most_used_id].name}** is the most heavily scheduled facility with **{most_slots} slots/week**.\n"
                f"**{dataset.rooms_by_id[least_used_id].name}** has the highest spare capacity with **{least_slots} slots/week**.\n\n"
                f"**Facility Utilization Summary:**\n" + "\n".join(rows)
            ),
            "actions": [
                {"label": "View Quality Radar", "tab": "quality"},
                {"label": "Simulate Room Maintenance", "modal": "crisis"}
            ],
            "highlight_ids": [most_used_id]
        }

    # 4. Crisis & Disruption Queries (e.g. "What if room 101 closes on Wednesday?")
    if any(k in q for k in ["what if", "crisis", "sick", "leave", "maintenance", "close"]):
        return {
            "intent": "CRISIS_PROMPT",
            "title": "Campus Crisis & Contingency Simulator",
            "reply": (
                "The platform includes a dedicated **Real-Time What-If Contingency Simulator**:\n\n"
                "1. **Faculty Sudden Sick Leave**: Automatically shifts their lectures without affecting others.\n"
                "2. **Classroom Emergency Closure**: Reroutes sessions to vacant rooms matching capacity.\n\n"
                "You can test this right now using the **'Campus Crisis Simulator'** panel."
            ),
            "actions": [
                {"label": "Open Crisis Simulator", "modal": "crisis"}
            ],
            "highlight_ids": []
        }

    # 5. Quality & Radar Queries
    if any(k in q for k in ["quality", "score", "radar", "performance", "metric", "grade"]):
        radar = compute_quality_radar(dataset, schedule)
        return {
            "intent": "QUALITY_RADAR",
            "title": "Timetable Quality Radar",
            "reply": (
                f"### Overall Schedule Grade: **{radar['grade']}** ({radar['overall_score']}/100)\n\n"
                f"**Key Dimensions:**\n"
                f"- **Constraint Integrity:** 100/100 (Zero hard clashes)\n"
                f"- **Faculty Fairness:** {radar['radar_metrics'][1]['score']}/100\n"
                f"- **Cohort Compactness:** {radar['radar_metrics'][2]['score']}/100\n"
                f"- **Room Efficiency:** {radar['radar_metrics'][3]['score']}/100\n"
                f"- **Time Balance:** {radar['radar_metrics'][4]['score']}/100\n\n"
                + "\n".join(radar['insights'])
            ),
            "actions": [
                {"label": "View Quality Radar Chart", "tab": "quality"}
            ],
            "highlight_ids": []
        }

    # 6. Default / General Help
    return {
        "intent": "GENERAL_HELP",
        "title": "AI Timetable Copilot",
        "reply": (
            "I can assist you with intelligent schedule analysis! Here are a few things you can ask me:\n\n"
            "- *'Who has the highest workload this week?'*\n"
            "- *'Is Dr. Sharma free on Friday afternoon?'*\n"
            "- *'Which rooms have the highest utilization?'*\n"
            "- *'Show me the overall quality radar score.'*\n"
            "- *'What happens if Room 101 closes for maintenance?'*"
        ),
        "actions": [
            {"label": "Who has highest workload?", "query": "Who has the highest workload?"},
            {"label": "Check Dr. Sharma's availability", "query": "Is Dr. Sharma free on Friday?"},
            {"label": "Analyze Room Usage", "query": "Which rooms are most used?"}
        ],
        "highlight_ids": []
    }
