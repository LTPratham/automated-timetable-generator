"""Soft constraint evaluation and penalty score reporting."""

from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from src.models.entities import SessionVariable, SlotAssignment, DayOfWeek, SessionType
from src.models.dataset import DepartmentDataset


@dataclass
class SoftConstraintReport:
    """Detailed audit of soft constraint satisfaction."""
    total_penalty: float = 0.0
    faculty_idle_gap_penalty: float = 0.0
    faculty_slot_preference_penalty: float = 0.0
    student_heavy_back_to_back_penalty: float = 0.0
    day_balance_penalty: float = 0.0
    violation_details: List[str] = field(default_factory=list)


class SoftConstraintScorer:
    """
    Calculates soft constraint violation penalties for a given timetable assignment.
    Weights can be customized by the user in the UI.
    """

    def __init__(
        self,
        weight_idle_gap: float = 5.0,
        weight_faculty_pref: float = 2.0,
        weight_heavy_back_to_back: float = 8.0,
        weight_day_balance: float = 3.0,
    ):
        self.weight_idle_gap = weight_idle_gap
        self.weight_faculty_pref = weight_faculty_pref
        self.weight_heavy_back_to_back = weight_heavy_back_to_back
        self.weight_day_balance = weight_day_balance

    def evaluate(
        self,
        assignment: Dict[SessionVariable, SlotAssignment],
        dataset: DepartmentDataset,
    ) -> SoftConstraintReport:
        report = SoftConstraintReport()
        faculty_map = dataset.faculty_by_id

        # 1. Faculty Idle Gaps Penalty
        # For each faculty and each day, find slots occupied. Idle gap = (max_slot - min_slot + 1) - total_occupied_slots
        faculty_daily_slots: Dict[Tuple[str, DayOfWeek], List[int]] = {}
        for var, assign in assignment.items():
            for day, slot in assign.occupied_slots:
                key = (var.faculty_id, day)
                if key not in faculty_daily_slots:
                    faculty_daily_slots[key] = []
                faculty_daily_slots[key].append(slot)

        for (fac_id, day), slots in faculty_daily_slots.items():
            if len(slots) > 1:
                slots.sort()
                span = slots[-1] - slots[0] + 1
                idle_slots = span - len(slots)
                if idle_slots > 0:
                    penalty = idle_slots * self.weight_idle_gap
                    report.faculty_idle_gap_penalty += penalty
                    fac_name = faculty_map[fac_id].name if fac_id in faculty_map else fac_id
                    report.violation_details.append(
                        f"Faculty {fac_name} has {idle_slots} idle gap hour(s) on {day.value}"
                    )

        # 2. Faculty Slot Preference Penalty
        for var, assign in assignment.items():
            faculty = faculty_map.get(var.faculty_id)
            if faculty and faculty.preferred_slots:
                # If assigned start slot is not in preferred slots
                if assign.start_slot_index not in faculty.preferred_slots:
                    report.faculty_slot_preference_penalty += self.weight_faculty_pref
                    report.violation_details.append(
                        f"Faculty {faculty.name} assigned to non-preferred slot {assign.start_slot_index} for {var.course_code}"
                    )

        # 3. Student Heavy Theory Back-to-Back Penalty
        # Check if a student batch has consecutive heavy theory classes
        batch_daily_heavy: Dict[Tuple[str, DayOfWeek], Set[int]] = {}
        for var, assign in assignment.items():
            if var.is_heavy and var.session_type == SessionType.THEORY:
                for day, slot in assign.occupied_slots:
                    key = (var.batch_id, day)
                    if key not in batch_daily_heavy:
                        batch_daily_heavy[key] = set()
                    batch_daily_heavy[key].add(slot)

        for (batch_id, day), heavy_slots in batch_daily_heavy.items():
            sorted_slots = sorted(heavy_slots)
            for i in range(len(sorted_slots) - 1):
                if sorted_slots[i + 1] == sorted_slots[i] + 1:
                    report.student_heavy_back_to_back_penalty += self.weight_heavy_back_to_back
                    report.violation_details.append(
                        f"Batch {batch_id} has back-to-back heavy theory at slots {sorted_slots[i]} & {sorted_slots[i+1]} on {day.value}"
                    )

        # Total penalty calculation
        report.total_penalty = (
            report.faculty_idle_gap_penalty
            + report.faculty_slot_preference_penalty
            + report.student_heavy_back_to_back_penalty
            + report.day_balance_penalty
        )

        return report

