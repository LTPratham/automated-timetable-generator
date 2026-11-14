"""Tests for the pure Python CSP Solver and Timetabling Constraints."""

import pytest
from src.data.sample_generator import create_sample_cs_department
from src.core.problem_builder import build_timetable_csp
from src.core.backtracking import BacktrackingSolver


def test_sample_dataset_generation():
    """Verify sample dataset structures and counts."""
    dataset = create_sample_cs_department()
    assert len(dataset.batches) == 4
    assert len(dataset.rooms) == 7
    assert len(dataset.faculty) == 8
    assert len(dataset.courses) >= 12

    variables = dataset.generate_session_variables()
    assert len(variables) > 0


def test_csp_problem_builder():
    """Verify CSP construction and domain sizes."""
    dataset = create_sample_cs_department()
    csp, variables = build_timetable_csp(dataset)

    assert len(csp.variables) == len(variables)
    for var in csp.variables:
        assert len(csp.domains[var]) > 0, f"Domain for {var.variable_id} must not be empty"


def test_backtracking_solver_mrv_forward_checking():
    """Solve the academic timetable CSP using Backtracking + MRV + Degree + Forward Checking."""
    dataset = create_sample_cs_department()
    csp, variables = build_timetable_csp(dataset)

    solver = BacktrackingSolver(
        use_mrv=True,
        use_degree=True,
        use_lcv=False,
        inference="forward_checking",
        time_limit_sec=30.0,
    )
    solution, stats = solver.solve(csp)

    assert stats.is_solved, "CSP Solver should find a valid clash-free timetable"
    assert solution is not None
    assert len(solution) == len(variables)

    # 1. Faculty clash check
    faculty_slot_map = {}
    for var, assign in solution.items():
        for day, slot in assign.occupied_slots:
            key = (var.faculty_id, day, slot)
            assert key not in faculty_slot_map, f"Faculty {var.faculty_id} double-booked at {day} slot {slot}"
            faculty_slot_map[key] = var.variable_id

    # 2. Batch clash check
    batch_slot_map = {}
    for var, assign in solution.items():
        for day, slot in assign.occupied_slots:
            key = (var.batch_id, day, slot)
            assert key not in batch_slot_map, f"Batch {var.batch_id} double-booked at {day} slot {slot}"
            batch_slot_map[key] = var.variable_id

    # 3. Room clash check
    room_slot_map = {}
    for var, assign in solution.items():
        for day, slot in assign.occupied_slots:
            key = (assign.room_id, day, slot)
            assert key not in room_slot_map, f"Room {assign.room_id} double-booked at {day} slot {slot}"
            room_slot_map[key] = var.variable_id

    # 4. Lab duration check
    for var, assign in solution.items():
        assert assign.duration_slots == var.duration_slots
        if var.duration_slots > 1:
            assert assign.start_slot_index + assign.duration_slots <= dataset.daily_slots_count


def test_ac3_preprocessing():
    """Verify that AC-3 runs cleanly on the CSP instance."""
    from src.core.propagation import ac3

    dataset = create_sample_cs_department()
    csp, _ = build_timetable_csp(dataset)
    consistent, pruned_domains = ac3(csp)
    assert consistent, "AC-3 should succeed without domain wipeout"


def test_genetic_algorithm_and_search_stepper():
    from src.solvers.genetic_solver import GeneticTimetableSolver
    from src.core.stepper import generate_search_execution_trace

    dataset = create_sample_cs_department()
    csp, _ = build_timetable_csp(dataset)

    # Test Stepper trace generator
    trace = generate_search_execution_trace(csp, dataset, max_steps=40)
    assert len(trace) > 5
    assert trace[0]["step_index"] == 1
    assert any(step["action"] == "TRY_ASSIGN" for step in trace)

    # Test Genetic Algorithm Solver
    ga_solver = GeneticTimetableSolver(population_size=15, max_generations=20, time_limit_sec=4.0)
    sol, stats = ga_solver.solve(csp, dataset)
    assert stats.algorithm_name == "Genetic Algorithm (Evolutionary Search)"
    assert stats.nodes_explored >= 15
