"""Backtracking search solver with configurable heuristics and inference."""

import time
from typing import Dict, List, Optional, Tuple, TypeVar, Callable
from dataclasses import dataclass, field
from src.core.csp import CSP
from src.core.heuristics import select_unassigned_variable, order_domain_values
from src.core.propagation import forward_check, ac3

V = TypeVar("V")
D = TypeVar("D")


@dataclass
class SolverStatistics:
    """Metrics recorded during the CSP search."""
    algorithm_name: str
    nodes_explored: int = 0
    backtracks: int = 0
    time_taken_ms: float = 0.0
    is_solved: bool = False
    solution_length: int = 0
    inference_prunes: int = 0


class BacktrackingSolver:
    """
    Configurable CSP Backtracking Search Engine.
    Supports:
      - Variable heuristics: MRV (Minimum Remaining Values), Degree Heuristic
      - Value heuristics: LCV (Least Constraining Value)
      - Constraint propagation: None, Forward Checking (FC), Arc Consistency (AC-3)
    """

    def __init__(
        self,
        use_mrv: bool = True,
        use_degree: bool = True,
        use_lcv: bool = False,
        inference: str = "forward_checking",  # "none", "forward_checking", "ac3"
        time_limit_sec: float = 60.0,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ):
        self.use_mrv = use_mrv
        self.use_degree = use_degree
        self.use_lcv = use_lcv
        self.inference = inference.lower()
        self.time_limit_sec = time_limit_sec
        self.progress_callback = progress_callback
        self.stats = SolverStatistics(algorithm_name=self._get_algo_label())

    def _get_algo_label(self) -> str:
        heuristics = []
        if self.use_mrv:
            heuristics.append("MRV")
        if self.use_degree:
            heuristics.append("Degree")
        if self.use_lcv:
            heuristics.append("LCV")
        h_str = "+".join(heuristics) if heuristics else "None"
        return f"Backtracking (Heuristics: {h_str}, Inference: {self.inference})"

    def solve(self, csp: CSP[V, D]) -> Tuple[Optional[Dict[V, D]], SolverStatistics]:
        """Runs the search on the given CSP instance."""
        start_time = time.perf_counter()
        self.stats = SolverStatistics(algorithm_name=self._get_algo_label())

        # Initial domains copy
        initial_domains = {var: list(domain) for var, domain in csp.domains.items()}

        # Optional initial AC-3 preprocessing
        if self.inference == "ac3":
            is_consistent, initial_domains = ac3(csp, domains=initial_domains)
            if not is_consistent:
                self.stats.time_taken_ms = (time.perf_counter() - start_time) * 1000
                return None, self.stats

        assignment: Dict[V, D] = {}
        solution = self._backtrack(csp, assignment, initial_domains, start_time)

        self.stats.time_taken_ms = (time.perf_counter() - start_time) * 1000
        self.stats.is_solved = solution is not None
        self.stats.solution_length = len(solution) if solution else 0
        return solution, self.stats

    def _backtrack(
        self,
        csp: CSP[V, D],
        assignment: Dict[V, D],
        domains: Dict[V, List[D]],
        start_time: float,
    ) -> Optional[Dict[V, D]]:
        # Check time limit
        if (time.perf_counter() - start_time) > self.time_limit_sec:
            return None

        # Check completeness
        if csp.is_complete(assignment):
            return assignment

        # Select next variable
        var = select_unassigned_variable(
            csp,
            assignment,
            domains,
            use_mrv=self.use_mrv,
            use_degree=self.use_degree,
        )

        # Order domain values
        ordered_values = order_domain_values(
            var,
            domains[var],
            csp,
            assignment,
            domains,
            use_lcv=self.use_lcv,
        )

        for value in ordered_values:
            self.stats.nodes_explored += 1
            if self.progress_callback and self.stats.nodes_explored % 25 == 0:
                self.progress_callback(len(assignment), len(csp.variables))

            if csp.is_consistent(var, value, assignment):
                # Speculatively assign
                assignment[var] = value

                # Inference propagation
                new_domains = domains
                inferred = True

                if self.inference == "forward_checking":
                    pruned_domains = forward_check(csp, var, value, assignment, domains)
                    if pruned_domains is None:
                        inferred = False
                    else:
                        new_domains = pruned_domains

                elif self.inference == "ac3":
                    # Run AC-3 on neighboring arcs
                    arcs = [(neighbor, var) for neighbor in csp.get_neighbors(var) if neighbor not in assignment]
                    consistent, pruned_domains = ac3(csp, queue=arcs, domains=domains)
                    if not consistent:
                        inferred = False
                    else:
                        new_domains = pruned_domains

                if inferred:
                    result = self._backtrack(csp, assignment, new_domains, start_time)
                    if result is not None:
                        return result

                # Backtrack
                del assignment[var]
                self.stats.backtracks += 1

        return None
