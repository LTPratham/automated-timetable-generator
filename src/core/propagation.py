"""Constraint Propagation: Forward Checking & AC-3 (Arc Consistency)."""

from typing import Dict, List, Optional, Set, Tuple, TypeVar
from collections import deque
from src.core.csp import CSP

V = TypeVar("V")
D = TypeVar("D")


def forward_check(
    csp: CSP[V, D],
    var: V,
    value: D,
    assignment: Dict[V, D],
    domains: Dict[V, List[D]],
) -> Optional[Dict[V, List[D]]]:
    """
    Applies forward checking after assigning `var = value`.
    Prunes domain values from unassigned neighbors that conflict with this assignment.
    Returns the new pruned domains dict, or None if any neighbor's domain is wiped out.
    """
    new_domains: Dict[V, List[D]] = {k: list(v) for k, v in domains.items()}
    new_domains[var] = [value]

    temp_assignment = dict(assignment)
    temp_assignment[var] = value

    for neighbor in csp.get_neighbors(var):
        if neighbor not in assignment:
            shared = [c for c in csp.constraints[var] if neighbor in c.variables]
            if not shared:
                continue

            valid_values: List[D] = []
            for n_val in new_domains[neighbor]:
                temp_assignment[neighbor] = n_val
                if all(c.is_satisfied(temp_assignment) for c in shared):
                    valid_values.append(n_val)

            if neighbor in temp_assignment:
                del temp_assignment[neighbor]

            if not valid_values:
                return None
            new_domains[neighbor] = valid_values

    return new_domains


def revise(
    csp: CSP[V, D],
    xi: V,
    xj: V,
    domains: Dict[V, List[D]],
) -> bool:
    """
    Revises the domain of xi such that every value in xi has at least one
    consistent value in xj's domain.
    """
    revised = False
    new_xi_domain: List[D] = []

    shared = [c for c in csp.constraints[xi] if xj in c.variables]
    if not shared:
        return False

    temp: Dict[V, D] = {}
    for x in domains[xi]:
        temp[xi] = x
        has_support = False
        for y in domains[xj]:
            temp[xj] = y
            if all(c.is_satisfied(temp) for c in shared):
                has_support = True
                break
        del temp[xi]
        if xj in temp:
            del temp[xj]

        if has_support:
            new_xi_domain.append(x)
        else:
            revised = True

    if revised:
        domains[xi] = new_xi_domain
    return revised


def ac3(
    csp: CSP[V, D],
    queue: Optional[List[Tuple[V, V]]] = None,
    domains: Optional[Dict[V, List[D]]] = None,
) -> Tuple[bool, Dict[V, List[D]]]:
    """Arc Consistency Algorithm #3."""
    active_domains = (
        {k: list(v) for k, v in domains.items()}
        if domains is not None
        else {k: list(v) for k, v in csp.domains.items()}
    )

    if queue is None:
        arc_queue: deque[Tuple[V, V]] = deque()
        for var in csp.variables:
            for neighbor in csp.get_neighbors(var):
                arc_queue.append((var, neighbor))
    else:
        arc_queue = deque(queue)

    while arc_queue:
        xi, xj = arc_queue.popleft()
        if revise(csp, xi, xj, active_domains):
            if len(active_domains[xi]) == 0:
                return False, active_domains
            for xk in csp.get_neighbors(xi):
                if xk != xj:
                    arc_queue.append((xk, xi))

    return True, active_domains
