"""Heuristics for Variable and Value ordering in CSP Backtracking Search."""

from typing import List, Dict, Set, Optional, TypeVar
from src.core.csp import CSP

V = TypeVar("V")
D = TypeVar("D")


def select_unassigned_variable(
    csp: CSP[V, D],
    assignment: Dict[V, D],
    domains: Dict[V, List[D]],
    use_mrv: bool = True,
    use_degree: bool = True,
) -> V:
    """
    Selects the next unassigned variable using:
    1. Minimum Remaining Values (MRV): fewest domain choices left.
    2. Degree Heuristic (as tie-breaker): largest number of constraints with other unassigned variables.
    """
    unassigned = [v for v in csp.variables if v not in assignment]
    if not unassigned:
        raise ValueError("All variables are already assigned")

    if not use_mrv:
        return unassigned[0]

    # Calculate remaining domain sizes (MRV)
    min_domain_size = min(len(domains[v]) for v in unassigned)
    mrv_candidates = [v for v in unassigned if len(domains[v]) == min_domain_size]

    if len(mrv_candidates) == 1 or not use_degree:
        return mrv_candidates[0]

    # Degree Heuristic: Select variable involved in largest number of constraints with other unassigned vars
    unassigned_set = set(unassigned)

    def degree(var: V) -> int:
        count = 0
        for constraint in csp.constraints[var]:
            for other_var in constraint.variables:
                if other_var != var and other_var in unassigned_set:
                    count += 1
        return count

    return max(mrv_candidates, key=degree)


def order_domain_values(
    var: V,
    domain_values: List[D],
    csp: CSP[V, D],
    assignment: Dict[V, D],
    domains: Dict[V, List[D]],
    use_lcv: bool = False,
) -> List[D]:
    """
    Orders domain values for the chosen variable.
    If use_lcv is True, sorts domain values by least constraining value.
    Otherwise returns domain_values directly.
    """
    if not use_lcv or len(domain_values) <= 1:
        return domain_values

    unassigned_neighbors = [n for n in csp.get_neighbors(var) if n not in assignment]
    if not unassigned_neighbors:
        return domain_values

    # Pre-filter constraints between var and unassigned neighbors
    neighbor_constraints = {}
    for n in unassigned_neighbors:
        shared = [c for c in csp.constraints[var] if n in c.variables]
        if shared:
            neighbor_constraints[n] = shared

    def score_value(val: D) -> int:
        eliminated = 0
        temp = dict(assignment)
        temp[var] = val
        for n, c_list in neighbor_constraints.items():
            for n_val in domains[n]:
                temp[n] = n_val
                if not all(c.is_satisfied(temp) for c in c_list):
                    eliminated += 1
                del temp[n]
        return eliminated

    # Sort values: lowest eliminated choices first
    return sorted(domain_values, key=score_value)
