"""Min-Conflicts Local Search Solver for Timetable CSP."""

import time
import random
from typing import Dict, List, Optional, Tuple, TypeVar, Set
from dataclasses import dataclass
from src.core.csp import CSP

V = TypeVar("V")
D = TypeVar("D")


@dataclass
class LocalSearchStatistics:
    algorithm_name: str = "Min-Conflicts Local Search"
    steps_taken: int = 0
    restarts: int = 0
    time_taken_ms: float = 0.0
    is_solved: bool = False
    final_conflicts: int = 0


class MinConflictsSolver:
    """
    Min-Conflicts Local Search Algorithm.
    Starts with a random complete assignment and iteratively chooses a conflicted
    variable, reassigning it to the domain value that minimizes overall conflicts.
    """

    def __init__(
        self,
        max_steps: int = 1500,
        max_restarts: int = 3,
        time_limit_sec: float = 20.0,
    ):
        self.max_steps = max_steps
        self.max_restarts = max_restarts
        self.time_limit_sec = time_limit_sec
        self.stats = LocalSearchStatistics()

    def solve(self, csp: CSP[V, D]) -> Tuple[Optional[Dict[V, D]], LocalSearchStatistics]:
        start_time = time.perf_counter()
        self.stats = LocalSearchStatistics()

        for restart in range(self.max_restarts):
            if (time.perf_counter() - start_time) > self.time_limit_sec:
                break
            self.stats.restarts = restart

            # 1. Initialize random complete assignment
            current_assignment: Dict[V, D] = {
                var: random.choice(csp.domains[var]) for var in csp.variables
            }

            for step in range(self.max_steps):
                if (time.perf_counter() - start_time) > self.time_limit_sec:
                    break
                self.stats.steps_taken += 1

                # 2. Identify all conflicted variables
                conflicted_vars = self._get_conflicted_variables(csp, current_assignment)
                if not conflicted_vars:
                    # Found zero-conflict valid schedule!
                    self.stats.time_taken_ms = (time.perf_counter() - start_time) * 1000
                    self.stats.is_solved = True
                    self.stats.final_conflicts = 0
                    return current_assignment, self.stats

                # 3. Pick a random conflicted variable
                chosen_var = random.choice(conflicted_vars)

                # 4. Pick domain value that minimizes total conflicts
                best_value = self._min_conflict_value(csp, chosen_var, current_assignment)
                current_assignment[chosen_var] = best_value

        self.stats.time_taken_ms = (time.perf_counter() - start_time) * 1000
        self.stats.is_solved = False
        self.stats.final_conflicts = len(self._get_conflicted_variables(csp, current_assignment))
        return None, self.stats

    def _get_conflicted_variables(self, csp: CSP[V, D], assignment: Dict[V, D]) -> List[V]:
        conflicted: Set[V] = set()
        for var in csp.variables:
            for constraint in csp.constraints[var]:
                if not constraint.is_satisfied(assignment):
                    conflicted.add(var)
                    break
        return list(conflicted)

    def _count_conflicts_for_var(self, csp: CSP[V, D], var: V, assignment: Dict[V, D]) -> int:
        conflicts = 0
        for constraint in csp.constraints[var]:
            if not constraint.is_satisfied(assignment):
                conflicts += 1
        return conflicts

    def _min_conflict_value(self, csp: CSP[V, D], var: V, assignment: Dict[V, D]) -> D:
        best_val = assignment[var]
        min_conflicts = float("inf")
        candidate_values = list(csp.domains[var])
        random.shuffle(candidate_values)

        for val in candidate_values:
            assignment[var] = val
            c_count = self._count_conflicts_for_var(csp, var, assignment)
            if c_count < min_conflicts:
                min_conflicts = c_count
                best_val = val
                if min_conflicts == 0:
                    break

        assignment[var] = best_val
        return best_val

