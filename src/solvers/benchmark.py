"""Comparative benchmarking runner for CSP and optimization algorithms."""

import time
from typing import Dict, List, Any
from dataclasses import dataclass
from src.models.entities import SessionVariable, SlotAssignment
from src.models.dataset import DepartmentDataset
from src.core.problem_builder import build_timetable_csp
from src.core.backtracking import BacktrackingSolver
from src.solvers.min_conflicts import MinConflictsSolver
from src.solvers.ortools_solver import ORToolsTimetableSolver
from src.solvers.genetic_solver import GeneticTimetableSolver
from src.analytics.penalty_scorer import SoftConstraintScorer


@dataclass
class BenchmarkRow:
    algorithm: str
    solved: bool
    time_ms: float
    nodes_or_steps: int
    backtracks_or_conflicts: int
    penalty_score: float
    notes: str


def run_comprehensive_benchmark(dataset: DepartmentDataset, time_limit_sec: float = 15.0) -> List[BenchmarkRow]:
    """Runs all available algorithms on the dataset and compiles comparative performance metrics."""
    scorer = SoftConstraintScorer()
    results: List[BenchmarkRow] = []

    # 1. Backtracking + MRV + Degree + Forward Checking
    csp1, _ = build_timetable_csp(dataset)
    solver_fc = BacktrackingSolver(
        use_mrv=True,
        use_degree=True,
        use_lcv=False,
        inference="forward_checking",
        time_limit_sec=time_limit_sec,
    )
    sol_fc, stats_fc = solver_fc.solve(csp1)
    penalty_fc = scorer.evaluate(sol_fc, dataset).total_penalty if sol_fc else float("inf")
    results.append(
        BenchmarkRow(
            algorithm="Backtracking + MRV + Degree + FC",
            solved=stats_fc.is_solved,
            time_ms=round(stats_fc.time_taken_ms, 2),
            nodes_or_steps=stats_fc.nodes_explored,
            backtracks_or_conflicts=stats_fc.backtracks,
            penalty_score=penalty_fc,
            notes="Strong constraint pruning via forward checking",
        )
    )

    # 2. Backtracking + MRV + Degree (No Inference)
    csp2, _ = build_timetable_csp(dataset)
    solver_mrv = BacktrackingSolver(
        use_mrv=True,
        use_degree=True,
        use_lcv=False,
        inference="none",
        time_limit_sec=time_limit_sec,
    )
    sol_mrv, stats_mrv = solver_mrv.solve(csp2)
    penalty_mrv = scorer.evaluate(sol_mrv, dataset).total_penalty if sol_mrv else float("inf")
    results.append(
        BenchmarkRow(
            algorithm="Backtracking + MRV + Degree (No Inference)",
            solved=stats_mrv.is_solved,
            time_ms=round(stats_mrv.time_taken_ms, 2),
            nodes_or_steps=stats_mrv.nodes_explored,
            backtracks_or_conflicts=stats_mrv.backtracks,
            penalty_score=penalty_mrv,
            notes="Fast variable ordering without intermediate domain pruning",
        )
    )

    # 3. Google OR-Tools CP-SAT
    ortools_solver = ORToolsTimetableSolver(time_limit_sec=time_limit_sec)
    sol_or, stats_or = ortools_solver.solve(dataset)
    penalty_or = scorer.evaluate(sol_or, dataset).total_penalty if sol_or else float("inf")
    results.append(
        BenchmarkRow(
            algorithm="Google OR-Tools CP-SAT",
            solved=stats_or.is_solved,
            time_ms=round(stats_or.time_taken_ms, 2),
            nodes_or_steps=stats_or.branches,
            backtracks_or_conflicts=stats_or.conflicts,
            penalty_score=penalty_or,
            notes="Industrial SAT solver with mathematical objective optimization",
        )
    )

    # 4. Min-Conflicts Local Search
    csp_mc, _ = build_timetable_csp(dataset)
    mc_solver = MinConflictsSolver(max_steps=1200, max_restarts=2, time_limit_sec=time_limit_sec)
    sol_mc, stats_mc = mc_solver.solve(csp_mc)
    penalty_mc = scorer.evaluate(sol_mc, dataset).total_penalty if sol_mc else float("inf")
    results.append(
        BenchmarkRow(
            algorithm="Min-Conflicts Local Search",
            solved=stats_mc.is_solved,
            time_ms=round(stats_mc.time_taken_ms, 2),
            nodes_or_steps=stats_mc.steps_taken,
            backtracks_or_conflicts=stats_mc.final_conflicts,
            penalty_score=penalty_mc,
            notes=f"Stochastic repair (restarts: {stats_mc.restarts})",
        )
    )

    # 5. Genetic Algorithm (Evolutionary Search)
    csp_ga, _ = build_timetable_csp(dataset)
    ga_solver = GeneticTimetableSolver(population_size=30, max_generations=80, time_limit_sec=min(time_limit_sec, 6.0))
    sol_ga, stats_ga = ga_solver.solve(csp_ga, dataset)
    penalty_ga = scorer.evaluate(sol_ga, dataset).total_penalty if sol_ga else float("inf")
    results.append(
        BenchmarkRow(
            algorithm="Genetic Algorithm (Evolutionary)",
            solved=stats_ga.is_solved,
            time_ms=round(stats_ga.time_taken_ms, 2),
            nodes_or_steps=stats_ga.nodes_explored,
            backtracks_or_conflicts=stats_ga.backtracks,
            penalty_score=penalty_ga,
            notes="Population-based crossover, mutation, and clash fitness",
        )
    )

    return results

