"""Academic Timetabling Constraints implementation."""

from typing import Dict, List, Set, Tuple
from src.core.csp import Constraint
from src.models.entities import SessionVariable, SlotAssignment, Room, Faculty, StudentBatch, SessionType


class FacultyNoClashConstraint(Constraint[SessionVariable, SlotAssignment]):
    """Ensures a faculty member is never scheduled for overlapping sessions."""

    def __init__(self, var1: SessionVariable, var2: SessionVariable):
        super().__init__([var1, var2], name=f"FacultyNoClash_{var1.variable_id}_{var2.variable_id}")
        self.var1 = var1
        self.var2 = var2

    def is_satisfied(self, assignment: Dict[SessionVariable, SlotAssignment]) -> bool:
        if self.var1 not in assignment or self.var2 not in assignment:
            return True
        val1 = assignment[self.var1]
        val2 = assignment[self.var2]
        # Same faculty cannot teach at the same time
        return not val1.overlaps_in_time(val2)


class BatchNoClashConstraint(Constraint[SessionVariable, SlotAssignment]):
    """Ensures a student batch/cohort is never scheduled for overlapping sessions."""

    def __init__(self, var1: SessionVariable, var2: SessionVariable):
        super().__init__([var1, var2], name=f"BatchNoClash_{var1.variable_id}_{var2.variable_id}")
        self.var1 = var1
        self.var2 = var2

    def is_satisfied(self, assignment: Dict[SessionVariable, SlotAssignment]) -> bool:
        if self.var1 not in assignment or self.var2 not in assignment:
            return True
        val1 = assignment[self.var1]
        val2 = assignment[self.var2]
        # Same student batch cannot attend two classes at once
        return not val1.overlaps_in_time(val2)


class RoomNoClashConstraint(Constraint[SessionVariable, SlotAssignment]):
    """Ensures a physical room/lab is never booked for two sessions simultaneously."""

    def __init__(self, var1: SessionVariable, var2: SessionVariable):
        super().__init__([var1, var2], name=f"RoomNoClash_{var1.variable_id}_{var2.variable_id}")
        self.var1 = var1
        self.var2 = var2

    def is_satisfied(self, assignment: Dict[SessionVariable, SlotAssignment]) -> bool:
        if self.var1 not in assignment or self.var2 not in assignment:
            return True
        val1 = assignment[self.var1]
        val2 = assignment[self.var2]
        # If rooms are different, no room clash
        if val1.room_id != val2.room_id:
            return True
        # If same room, cannot overlap in time
        return not val1.overlaps_in_time(val2)


class CourseSpreadConstraint(Constraint[SessionVariable, SlotAssignment]):
    """Avoids scheduling multiple theory lectures of the exact same course for the same batch on the same day."""

    def __init__(self, var1: SessionVariable, var2: SessionVariable):
        super().__init__([var1, var2], name=f"CourseSpread_{var1.variable_id}_{var2.variable_id}")
        self.var1 = var1
        self.var2 = var2

    def is_satisfied(self, assignment: Dict[SessionVariable, SlotAssignment]) -> bool:
        if self.var1 not in assignment or self.var2 not in assignment:
            return True
        val1 = assignment[self.var1]
        val2 = assignment[self.var2]
        # Theory lectures for the same course should be on different days
        if self.var1.session_type == SessionType.THEORY and self.var2.session_type == SessionType.THEORY:
            return val1.day != val2.day
        return True


class FacultyDailyWorkloadConstraint(Constraint[SessionVariable, SlotAssignment]):
    """Ensures an instructor does not exceed their daily teaching hours limit."""

    def __init__(self, faculty: Faculty, faculty_variables: List[SessionVariable]):
        super().__init__(faculty_variables, name=f"FacultyDailyMaxHours_{faculty.id}")
        self.faculty = faculty

    def is_satisfied(self, assignment: Dict[SessionVariable, SlotAssignment]) -> bool:
        # Tally hours per day for assigned variables of this faculty
        daily_hours: Dict[str, int] = {}
        for var in self.variables:
            if var in assignment:
                val = assignment[var]
                day_key = val.day.value
                daily_hours[day_key] = daily_hours.get(day_key, 0) + val.duration_slots
                if daily_hours[day_key] > self.faculty.max_hours_per_day:
                    return False
        return True

