"""Tests for OR-Tools Solver, What-If Rescheduler, and Exporters."""

import pytest
from src.data.sample_generator import create_sample_cs_department
from src.core.problem_builder import build_timetable_csp
from src.core.backtracking import BacktrackingSolver
from src.solvers.ortools_solver import ORToolsTimetableSolver
from src.analytics.rescheduler import WhatIfRescheduler
from src.exporter.excel_export import export_timetable_to_excel
from src.exporter.pdf_export import export_timetable_to_pdf
from src.exporter.ical_export import export_timetable_to_ics
from src.models.entities import DayOfWeek


@pytest.fixture(scope="module")
def base_data():
    dataset = create_sample_cs_department()
    csp, _ = build_timetable_csp(dataset)
    solver = BacktrackingSolver(use_mrv=True, use_degree=True, use_lcv=False, inference="forward_checking")
    schedule, stats = solver.solve(csp)
    return dataset, schedule


def test_ortools_cp_sat_solver(base_data):
    """Verify that Google OR-Tools CP-SAT finds an optimal/feasible schedule."""
    dataset, _ = base_data
    solver = ORToolsTimetableSolver(time_limit_sec=15.0)
    solution, stats = solver.solve(dataset)

    assert stats.is_solved, "OR-Tools CP-SAT must solve the academic timetable problem"
    assert solution is not None
    assert len(solution) > 0


def test_what_if_faculty_leave_rescheduling(base_data):
    """Test emergency faculty leave rescheduling."""
    dataset, initial_schedule = base_data
    rescheduler = WhatIfRescheduler(dataset)
    # Dr. Turing takes leave on Friday
    updated_schedule, report = rescheduler.handle_faculty_leave(
        initial_schedule,
        faculty_id="FAC_TURING",
        leave_day=DayOfWeek.FRIDAY,
    )

    assert report.success, "Should reschedule or verify no clashing sessions"


def test_what_if_room_closure_rescheduling(base_data):
    """Test room maintenance rerouting."""
    dataset, initial_schedule = base_data
    rescheduler = WhatIfRescheduler(dataset)
    # LH-101 closed on Monday
    updated_schedule, report = rescheduler.handle_room_closure(
        initial_schedule,
        closed_room_id="LH-101",
        closure_day=DayOfWeek.MONDAY,
    )

    assert report.success, "Should swap rooms cleanly"


def test_excel_export_generation(base_data):
    """Verify Excel export creates valid bytes."""
    dataset, schedule = base_data
    excel_buf = export_timetable_to_excel(dataset, schedule)
    assert excel_buf is not None
    assert excel_buf.getvalue().startswith(b"PK"), "Excel file must start with zip PK header"


def test_pdf_export_generation(base_data):
    """Verify PDF export creates valid bytes."""
    dataset, schedule = base_data
    pdf_buf = export_timetable_to_pdf(dataset, schedule)
    assert pdf_buf is not None
    assert pdf_buf.getvalue().startswith(b"%PDF"), "PDF file must start with %PDF header"


def test_ical_export_generation(base_data):
    """Verify iCalendar export string."""
    dataset, schedule = base_data
    ics_str = export_timetable_to_ics(dataset, schedule)
    assert "BEGIN:VCALENDAR" in ics_str
    assert "END:VCALENDAR" in ics_str
    assert "BEGIN:VEVENT" in ics_str
