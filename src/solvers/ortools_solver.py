"""Google OR-Tools CP-SAT Industrial Solver implementation for Academic Timetabling."""

import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from ortools.sat.python import cp_model
from src.models.entities import SessionVariable, SlotAssignment, DayOfWeek, SessionType
from src.models.dataset import DepartmentDataset
from src.core.problem_builder import build_timetable_csp


@dataclass
class ORToolsStatistics:
    algorithm_name: str = "Google OR-Tools CP-SAT"
    time_taken_ms: float = 0.0
    is_solved: bool = False
    solver_status: str = "UNKNOWN"
    branches: int = 0
    conflicts: int = 0
    objective_value: float = 0.0


class ORToolsTimetableSolver:
    """Industrial CP-SAT solver mapping academic timetabling constraints."""

    def __init__(self, time_limit_sec: float = 30.0):
        self.time_limit_sec = time_limit_sec
        self.stats = ORToolsStatistics()

    def solve(self, dataset: DepartmentDataset) -> Tuple[Optional[Dict[SessionVariable, SlotAssignment]], ORToolsStatistics]:
        start_time = time.perf_counter()
        self.stats = ORToolsStatistics()

        csp, variables = build_timetable_csp(dataset)
        model = cp_model.CpModel()

        # Decision variables: x[var_id, val_index] is True iff var is assigned val
        var_choice_vars: Dict[Tuple[str, int], cp_model.IntVar] = {}
        var_val_map: Dict[Tuple[str, int], Tuple[SessionVariable, SlotAssignment]] = {}

        for var in variables:
            var_domain = csp.domains[var]
            bool_vars_for_var = []
            for idx, val in enumerate(var_domain):
                b_var = model.NewBoolVar(f"x_{var.variable_id}_{idx}")
                var_choice_vars[(var.variable_id, idx)] = b_var
                var_val_map[(var.variable_id, idx)] = (var, val)
                bool_vars_for_var.append(b_var)

            # Hard Constraint: Every session variable must have exactly one assignment
            model.AddExactlyOne(bool_vars_for_var)

        # Build Resource x Time occupation maps
        faculty_time_map: Dict[Tuple[str, DayOfWeek, int], List[cp_model.IntVar]] = {}
        batch_time_map: Dict[Tuple[str, DayOfWeek, int], List[cp_model.IntVar]] = {}
        room_time_map: Dict[Tuple[str, DayOfWeek, int], List[cp_model.IntVar]] = {}
        course_day_map: Dict[Tuple[str, DayOfWeek], List[cp_model.IntVar]] = {}

        objective_terms = []

        faculty_map = dataset.faculty_by_id

        for (var_id, idx), b_var in var_choice_vars.items():
            var, val = var_val_map[(var_id, idx)]

            # 1. Faculty conflicts
            for d, s in val.occupied_slots:
                fac_key = (var.faculty_id, d, s)
                faculty_time_map.setdefault(fac_key, []).append(b_var)

            # 2. Batch conflicts
            for d, s in val.occupied_slots:
                batch_key = (var.batch_id, d, s)
                batch_time_map.setdefault(batch_key, []).append(b_var)

            # 3. Room conflicts
            for d, s in val.occupied_slots:
                room_key = (val.room_id, d, s)
                room_time_map.setdefault(room_key, []).append(b_var)

            # 4. Course spread on same day
            if var.session_type == SessionType.THEORY:
                c_key = (var.course_id, val.day)
                course_day_map.setdefault(c_key, []).append(b_var)

            # Soft constraint in objective: Faculty slot preference penalty
            fac = faculty_map.get(var.faculty_id)
            if fac and fac.preferred_slots:
                if val.start_slot_index not in fac.preferred_slots:
                    objective_terms.append(b_var * 2)

        # Enforce resource exclusivity (At most one session per time slot per resource)
        for vars_list in faculty_time_map.values():
            model.AddAtMostOne(vars_list)

        for vars_list in batch_time_map.values():
            model.AddAtMostOne(vars_list)

        for vars_list in room_time_map.values():
            model.AddAtMostOne(vars_list)

        for vars_list in course_day_map.values():
            model.AddAtMostOne(vars_list)

        # Minimize soft penalty
        if objective_terms:
            model.Minimize(sum(objective_terms))

        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.time_limit_sec
        status = solver.Solve(model)

        self.stats.time_taken_ms = (time.perf_counter() - start_time) * 1000
        self.stats.solver_status = solver.StatusName(status)
        self.stats.branches = solver.NumBranches()
        self.stats.conflicts = solver.NumConflicts()

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            self.stats.is_solved = True
            if objective_terms:
                self.stats.objective_value = solver.ObjectiveValue()

            solution: Dict[SessionVariable, SlotAssignment] = {}
            for (var_id, idx), b_var in var_choice_vars.items():
                if solver.Value(b_var) == 1:
                    var, val = var_val_map[(var_id, idx)]
                    solution[var] = val

            return solution, self.stats

        self.stats.is_solved = False
        return None, self.stats

