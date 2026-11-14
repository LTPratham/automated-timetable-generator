"""Builds the concrete CSP instance from a DepartmentDataset."""

from typing import Dict, List, Tuple
from src.models.entities import (
    SessionVariable,
    SlotAssignment,
    SessionType,
    DayOfWeek,
)
from src.models.dataset import DepartmentDataset
from src.core.csp import CSP
from src.core.constraints import (
    FacultyNoClashConstraint,
    BatchNoClashConstraint,
    RoomNoClashConstraint,
    CourseSpreadConstraint,
    FacultyDailyWorkloadConstraint,
)


def build_timetable_csp(dataset: DepartmentDataset) -> Tuple[CSP[SessionVariable, SlotAssignment], List[SessionVariable]]:
    """
    Transforms the department dataset into a fully formulated CSP instance
    with pruned initial domains and all binary/global hard constraints registered.
    """
    variables = dataset.generate_session_variables()
    domains: Dict[SessionVariable, List[SlotAssignment]] = {}

    faculty_map = dataset.faculty_by_id
    batch_map = dataset.batches_by_id
    rooms = dataset.rooms

    # Pre-compute valid domains for each variable using unary constraints
    for var in variables:
        var_domains: List[SlotAssignment] = []
        batch = batch_map[var.batch_id]
        faculty = faculty_map[var.faculty_id]

        for day in dataset.days:
            # Continuous duration boundary check
            max_start_slot = dataset.daily_slots_count - var.duration_slots
            for slot_idx in range(max_start_slot + 1):
                # Check faculty availability across all occupied consecutive slots
                slots_needed = [(day, slot_idx + i) for i in range(var.duration_slots)]
                if not all(faculty.is_available(d, s) for d, s in slots_needed):
                    continue

                # Check compatible rooms
                for room in rooms:
                    if room.can_accommodate(batch.strength, var.session_type):
                        var_domains.append(
                            SlotAssignment(
                                day=day,
                                start_slot_index=slot_idx,
                                duration_slots=var.duration_slots,
                                room_id=room.id,
                            )
                        )

        domains[var] = var_domains

    csp = CSP(variables, domains)

    # Register binary constraints
    num_vars = len(variables)
    for i in range(num_vars):
        var1 = variables[i]
        for j in range(i + 1, num_vars):
            var2 = variables[j]

            # 1. Faculty conflict (Same instructor teaching 2 classes)
            if var1.faculty_id == var2.faculty_id:
                csp.add_constraint(FacultyNoClashConstraint(var1, var2))

            # 2. Batch conflict (Same student section attending 2 classes)
            if var1.batch_id == var2.batch_id:
                csp.add_constraint(BatchNoClashConstraint(var1, var2))

            # 3. Room conflict (Same physical room hosting 2 classes)
            csp.add_constraint(RoomNoClashConstraint(var1, var2))

            # 4. Course spread (Avoid two lectures of same course on same day)
            if var1.course_id == var2.course_id:
                csp.add_constraint(CourseSpreadConstraint(var1, var2))

    # Register faculty daily workload constraints
    for faculty in dataset.faculty:
        fac_vars = [v for v in variables if v.faculty_id == faculty.id]
        if fac_vars:
            csp.add_constraint(FacultyDailyWorkloadConstraint(faculty, fac_vars))

    return csp, variables

