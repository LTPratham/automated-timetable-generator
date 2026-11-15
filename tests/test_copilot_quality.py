"""Tests for AI Copilot and Multi-Objective Quality Radar."""

from src.data.sample_generator import create_sample_cs_department
from src.core.problem_builder import build_timetable_csp
from src.core.backtracking import BacktrackingSolver
from src.analytics.copilot import process_copilot_query, compute_quality_radar


def test_copilot_queries_and_quality_radar():
    dataset = create_sample_cs_department()
    csp, _ = build_timetable_csp(dataset)
    solver = BacktrackingSolver(use_mrv=True, use_degree=True, inference="forward_checking")
    schedule, stats = solver.solve(csp)
    assert stats.is_solved is True

    # 1. Test Quality Radar
    radar = compute_quality_radar(dataset, schedule)
    assert "radar_metrics" in radar
    assert len(radar["radar_metrics"]) == 5
    assert radar["overall_score"] > 60
    assert "grade" in radar

    # 2. Test Copilot query - Workload
    res1 = process_copilot_query("Who has the highest workload?", dataset, schedule)
    assert res1["intent"] == "WORKLOAD_AUDIT"
    assert "hours/week" in res1["reply"]

    # 3. Test Copilot query - Availability
    res2 = process_copilot_query("Is Dr. Alan Turing free on Friday?", dataset, schedule)
    assert res2["intent"] == "FACULTY_AVAILABILITY"
    assert "Turing" in res2["title"]

    # 4. Test Copilot query - Room Utilization
    res3 = process_copilot_query("Which room has the highest utilization?", dataset, schedule)
    assert res3["intent"] == "ROOM_UTILIZATION"

    # 5. Test Copilot query - General Help
    res4 = process_copilot_query("Hello, what can you do?", dataset, schedule)
    assert res4["intent"] == "GENERAL_HELP"
