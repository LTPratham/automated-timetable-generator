"""Step-by-step Search Trace Generator for Backtracking CSP.

Records fine-grained state transitions during backtracking search:
variable selection (MRV), candidate assignment, forward checking domain pruning,
and backtrack points to power the interactive visualizer.
"""

from typing import Dict, List, Any, Set
from src.core.csp import CSP
from src.models.entities import SessionVariable, SlotAssignment
from src.models.dataset import DepartmentDataset
from src.core.heuristics import select_unassigned_variable
from src.core.propagation import forward_check


def generate_search_execution_trace(
    csp: CSP[SessionVariable, SlotAssignment],
    dataset: DepartmentDataset,
    max_steps: int = 100,
) -> List[Dict[str, Any]]:
    """Runs backtracking with FC while logging discrete visual steps."""
    trace: List[Dict[str, Any]] = []
    assignment: Dict[SessionVariable, SlotAssignment] = {}
    domains = {v: list(csp.domains[v]) for v in csp.variables}

    def log_step(action: str, var: SessionVariable = None, assign: SlotAssignment = None, detail: str = "", pruned_count: int = 0):
        if len(trace) >= max_steps:
            return
        snapshot = [
            {
                "variable_id": v.variable_id,
                "course_code": v.course_code,
                "batch_id": v.batch_id,
                "day": a.day.value,
                "slot": a.start_slot_index,
                "room_id": a.room_id,
            }
            for v, a in assignment.items()
        ]
        trace.append({
            "step_index": len(trace) + 1,
            "action": action,
            "variable_id": var.variable_id if var else "",
            "course_code": var.course_code if var else "",
            "batch_id": var.batch_id if var else "",
            "day": assign.day.value if assign else "",
            "slot": assign.start_slot_index if assign else -1,
            "room_id": assign.room_id if assign else "",
            "detail": detail,
            "pruned_count": pruned_count,
            "assigned_count": len(assignment),
            "total_variables": len(csp.variables),
            "snapshot": snapshot,
        })

    def backtrack_recursive(current_domains: Dict[SessionVariable, List[SlotAssignment]]) -> bool:
        if len(assignment) == len(csp.variables):
            log_step("SUCCESS", None, None, f"🎉 All {len(csp.variables)} sessions successfully placed with 0 conflicts!")
            return True

        if len(trace) >= max_steps:
            return True  # Cap trace size for clean UI rendering

        var = select_unassigned_variable(csp, assignment, current_domains, use_mrv=True, use_degree=True)
        remaining_domain_len = len(current_domains[var])
        fac_name = dataset.faculty_by_id[var.faculty_id].name.split()[-1] if var.faculty_id in dataset.faculty_by_id else var.faculty_id
        
        log_step(
            "SELECT_VAR",
            var,
            None,
            f"🧠 <b>MRV Heuristic</b> prioritized <b>{var.course_code}</b> ({var.batch_id}, Prof. {fac_name}) with {remaining_domain_len} remaining valid slot(s)."
        )

        for val in list(current_domains[var]):
            if csp.is_consistent(var, val, assignment):
                assignment[var] = val
                log_step(
                    "TRY_ASSIGN",
                    var,
                    val,
                    f"Testing <b>{var.course_code}</b> on <b>{val.day.value} Slot {val.start_slot_index}</b> in <b>{val.room_id}</b>."
                )

                # Forward Checking
                new_domains = forward_check(csp, var, val, assignment, current_domains)
                if new_domains is not None:
                    # Calculate pruned count
                    pruned_count = sum(
                        len(current_domains[k]) - len(new_domains[k])
                        for k in current_domains if k not in assignment and k != var
                    )
                    if pruned_count > 0:
                        log_step(
                            "FORWARD_CHECK",
                            var,
                            val,
                            f"⚡ <b>Forward Checking</b> eliminated {pruned_count} clashing slot-room option(s) from neighboring courses.",
                            pruned_count=pruned_count,
                        )

                    result = backtrack_recursive(new_domains)
                    if result:
                        return True

                del assignment[var]
                log_step(
                    "BACKTRACK",
                    var,
                    val,
                    f"🔙 <b>Backtrack!</b> Dead-end reached after {var.course_code} at Slot {val.start_slot_index}. Pruning branches and rolling back."
                )

        return False

    backtrack_recursive(domains)
    return trace
