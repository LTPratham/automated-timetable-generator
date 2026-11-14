"""Dataset container and validation for academic department scheduling."""

from typing import List, Dict, Optional, Tuple, Set
from pydantic import BaseModel, Field, model_validator
from src.models.entities import (
    Faculty,
    Course,
    StudentBatch,
    Room,
    TimeSlot,
    DayOfWeek,
    SessionType,
    SessionVariable,
)


class DepartmentDataset(BaseModel):
    """Holds all academic configuration and entities for the timetable CSP."""
    name: str = "Department of Computer Science & Engineering"
    days: List[DayOfWeek] = Field(
        default_factory=lambda: [
            DayOfWeek.MONDAY,
            DayOfWeek.TUESDAY,
            DayOfWeek.WEDNESDAY,
            DayOfWeek.THURSDAY,
            DayOfWeek.FRIDAY,
        ]
    )
    daily_slots_count: int = Field(default=6, ge=4, le=10)
    slot_times: List[Tuple[str, str]] = Field(
        default_factory=lambda: [
            ("09:00", "10:00"),
            ("10:00", "11:00"),
            ("11:15", "12:15"),
            ("12:15", "13:15"),
            ("14:00", "15:00"),
            ("15:00", "16:00"),
        ]
    )
    faculty: List[Faculty] = Field(default_factory=list)
    courses: List[Course] = Field(default_factory=list)
    batches: List[StudentBatch] = Field(default_factory=list)
    rooms: List[Room] = Field(default_factory=list)

    @property
    def faculty_by_id(self) -> Dict[str, Faculty]:
        return {f.id: f for f in self.faculty}

    @property
    def batches_by_id(self) -> Dict[str, StudentBatch]:
        return {b.id: b for b in self.batches}

    @property
    def rooms_by_id(self) -> Dict[str, Room]:
        return {r.id: r for r in self.rooms}

    @property
    def courses_by_id(self) -> Dict[str, Course]:
        return {c.id: c for c in self.courses}

    @property
    def all_time_slots(self) -> List[TimeSlot]:
        slots = []
        for day in self.days:
            for idx in range(min(self.daily_slots_count, len(self.slot_times))):
                start, end = self.slot_times[idx]
                slots.append(TimeSlot(slot_index=idx, day=day, start_time=start, end_time=end))
        return slots

    @model_validator(mode="after")
    def validate_references(self) -> "DepartmentDataset":
        fac_ids = {f.id for f in self.faculty}
        batch_ids = {b.id for b in self.batches}

        for c in self.courses:
            if c.faculty_id not in fac_ids:
                raise ValueError(f"Course '{c.code}' references unknown faculty ID: '{c.faculty_id}'")
            if c.batch_id not in batch_ids:
                raise ValueError(f"Course '{c.code}' references unknown batch ID: '{c.batch_id}'")
        return self

    def generate_session_variables(self) -> List[SessionVariable]:
        """Expands course requirements into individual session variables to be scheduled."""
        variables: List[SessionVariable] = []
        for course in self.courses:
            for s_idx in range(1, course.sessions_per_week + 1):
                type_code = "LAB" if course.course_type == SessionType.LAB else "TH"
                var_id = f"{course.code}_{course.batch_id}_{type_code}_{s_idx}"
                variables.append(
                    SessionVariable(
                        variable_id=var_id,
                        course_id=course.id,
                        course_code=course.code,
                        course_title=course.title,
                        batch_id=course.batch_id,
                        faculty_id=course.faculty_id,
                        session_type=course.course_type,
                        duration_slots=course.duration_slots,
                        session_index=s_idx,
                        is_heavy=course.is_heavy,
                    )
                )
        return variables

