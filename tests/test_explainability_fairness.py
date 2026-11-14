"""Unit tests for Explainability Inspector and Responsible AI / Fairness Audit."""

import pytest
from src.data.sample_generator import create_sample_cs_department
from src.core.problem_builder import build_timetable_csp
from src.core.backtracking import BacktrackingSolver
from src.analytics.explainability import generate_session_explanation
from src.analytics.fairness import audit_fairness_and_ethics, calculate_gini


def test_gini_calculation():
    # Perfect equality
    assert calculate_gini([10.0, 10.0, 10.0, 10.0]) == 0.0
    # Inequality
    gini = calculate_gini([0.0, 0.0, 0.0, 40.0])
    assert gini > 0.5


def test_explainability_and_fairness_audit():
    dataset = create_sample_cs_department()
    csp, _ = build_timetable_csp(dataset)
    solver = BacktrackingSolver(use_mrv=True, use_degree=True, use_lcv=False, inference="forward_checking")
    schedule, stats = solver.solve(csp)
    assert schedule is not None

    # Test Explainability for first session
    sample_var = list(schedule.keys())[0]
    sample_assign = schedule[sample_var]
    explanation = generate_session_explanation(sample_var, sample_assign, dataset, schedule)

    assert explanation["variable_id"] == sample_var.variable_id
    assert explanation["course_code"] == sample_var.course_code
    assert len(explanation["hard_checks"]) >= 5
    assert all(hc["status"] == "Satisfied" for hc in explanation["hard_checks"])
    assert "MRV" in explanation["search_trace"]["variable_ordering_heuristic"]

    # Test Fairness Audit
    audit = audit_fairness_and_ethics(schedule, dataset)
    assert "faculty_workload" in audit
    assert "batch_fatigue" in audit
    assert "responsible_ai" in audit
    assert audit["responsible_ai"]["gini_index"] >= 0.0
    assert len(audit["faculty_workload"]) == len(dataset.faculty)
