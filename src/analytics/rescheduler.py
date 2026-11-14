"""'What-If' Dynamic Rescheduling & Disruption Simulator."""

from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from src.models.entities import SessionVariable, SlotAssignment, DayOfWeek, SessionType
from src.models.dataset import DepartmentDataset
from src.core.problem_builder import build_timetable_csp


@dataclass
class ReschedulingReport:
    """Report detailing changes made during dynamic rescheduling."""
    success: bool
    scenario: str
    affected_sessions_count: int
    reassigned_sessions: List[Tuple[SessionVariable, SlotAssignment, SlotAssignment]] = field(default_factory=list)
    unresolved_sessions: List[SessionVariable] = field(default_factory=list)
    message: str = ""


class WhatIfRescheduler:
    """Handles emergency real-time schedule perturbations with minimal ripple effect."""

    def __init__(self, dataset: DepartmentDataset):
        self.dataset = dataset

    def handle_faculty_leave(
        self,
        current_schedule: Dict[SessionVariable, SlotAssignment],
        faculty_id: str,
        leave_day: DayOfWeek,
        leave_slots: Optional[List[int]] = None,
    ) -> Tuple[Dict[SessionVariable, SlotAssignment], ReschedulingReport]:
        """
        Reschedules sessions when a faculty member takes sudden leave on a specific day/slot.
        Tries to move affected sessions to other valid slots with minimal disruption.
        """
        updated_schedule = dict(current_schedule)
        affected_vars = []

        for var, assign in current_schedule.items():
            if var.faculty_id == faculty_id and assign.day == leave_day:
                if leave_slots is None or any(s in leave_slots for _, s in assign.occupied_slots):
                    affected_vars.append(var)

        if not affected_vars:
            return updated_schedule, ReschedulingReport(
                success=True,
                scenario=f"Faculty Leave ({faculty_id} on {leave_day.value})",
                affected_sessions_count=0,
                message="No scheduled sessions were affected by this leave request.",
            )

        csp, _ = build_timetable_csp(self.dataset)
        reassigned = []
        unresolved = []

        # Temporarily remove affected sessions
        for v in affected_vars:
            del updated_schedule[v]

        for var in affected_vars:
            found_slot = False
            # Search domain values that are NOT on the leave day/slots
            for candidate in csp.domains[var]:
                if candidate.day == leave_day:
                    if leave_slots is None or any(s in leave_slots for _, s in candidate.occupied_slots):
                        continue

                # Check consistency against updated schedule
                if csp.is_consistent(var, candidate, updated_schedule):
                    old_assign = current_schedule[var]
                    updated_schedule[var] = candidate
                    reassigned.append((var, old_assign, candidate))
                    found_slot = True
                    break

            if not found_slot:
                unresolved.append(var)
                # Revert to original if unresolvable
                updated_schedule[var] = current_schedule[var]

        success = len(unresolved) == 0
        fac_name = self.dataset.faculty_by_id[faculty_id].name if faculty_id in self.dataset.faculty_by_id else faculty_id
        msg = (
            f"Successfully rescheduled {len(reassigned)}/{len(affected_vars)} sessions for {fac_name}."
            if success
            else f"Could not find clash-free alternatives for {len(unresolved)} sessions without broader changes."
        )

        return updated_schedule, ReschedulingReport(
            success=success,
            scenario=f"Faculty Leave: {fac_name} on {leave_day.value}",
            affected_sessions_count=len(affected_vars),
            reassigned_sessions=reassigned,
            unresolved_sessions=unresolved,
            message=msg,
        )

    def handle_room_closure(
        self,
        current_schedule: Dict[SessionVariable, SlotAssignment],
        closed_room_id: str,
        closure_day: DayOfWeek,
    ) -> Tuple[Dict[SessionVariable, SlotAssignment], ReschedulingReport]:
        """
        Reschedules sessions when a classroom or lab is closed for repairs/maintenance on a day.
        Prioritizes keeping the exact same time slot and only changing the physical room.
        """
        updated_schedule = dict(current_schedule)
        affected_vars = []

        for var, assign in current_schedule.items():
            if assign.room_id == closed_room_id and assign.day == closure_day:
                affected_vars.append(var)

        if not affected_vars:
            return updated_schedule, ReschedulingReport(
                success=True,
                scenario=f"Room Maintenance ({closed_room_id} on {closure_day.value})",
                affected_sessions_count=0,
                message="No sessions were scheduled in this room on the specified day.",
            )

        reassigned = []
        unresolved = []

        for var in affected_vars:
            orig = current_schedule[var]
            del updated_schedule[var]
            batch = self.dataset.batches_by_id[var.batch_id]

            # Try candidate rooms at the exact same day and slot
            found_room = False
            for alt_room in self.dataset.rooms:
                if alt_room.id == closed_room_id:
                    continue
                if not alt_room.can_accommodate(batch.strength, var.session_type):
                    continue

                # Check if alt_room is free at this slot
                room_free = True
                for other_var, other_val in updated_schedule.items():
                    if other_val.room_id == alt_room.id and other_val.day == orig.day:
                        if orig.overlaps_in_time(other_val):
                            room_free = False
                            break

                if room_free:
                    new_assign = SlotAssignment(
                        day=orig.day,
                        start_slot_index=orig.start_slot_index,
                        duration_slots=orig.duration_slots,
                        room_id=alt_room.id,
                    )
                    updated_schedule[var] = new_assign
                    reassigned.append((var, orig, new_assign))
                    found_room = True
                    break

            if not found_room:
                unresolved.append(var)
                updated_schedule[var] = orig

        success = len(unresolved) == 0
        return updated_schedule, ReschedulingReport(
            success=success,
            scenario=f"Room Maintenance: {closed_room_id} on {closure_day.value}",
            affected_sessions_count=len(affected_vars),
            reassigned_sessions=reassigned,
            unresolved_sessions=unresolved,
            message=(
                f"Swapped {len(reassigned)} sessions to available alternative rooms."
                if success
                else f"Could not find alternative rooms for {len(unresolved)} sessions."
            ),
        )

