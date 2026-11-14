"""Pydantic data models for the Timetable CSP Generator."""

from enum import Enum
from typing import List, Dict, Optional, Tuple, Set
from pydantic import BaseModel, Field, field_validator, model_validator


class SessionType(str, Enum):
    THEORY = "THEORY"
    LAB = "LAB"


class DayOfWeek(str, Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"


class TimeSlot(BaseModel):
    """Represents a standard atomic time slot in the daily schedule."""
    slot_index: int = Field(ge=0, description="0-indexed slot within the day")
    day: DayOfWeek
    start_time: str = Field(description="Start time format e.g. 09:00")
    end_time: str = Field(description="End time format e.g. 10:00")

    @property
    def key(self) -> Tuple[str, int]:
        return (self.day.value, self.slot_index)

    def __str__(self) -> str:
        return f"{self.day.value[:3]} Slot {self.slot_index} ({self.start_time}-{self.end_time})"


class Room(BaseModel):
    """Represents a physical classroom, lecture hall, or computer/hardware laboratory."""
    id: str = Field(min_length=1)
    name: str
    capacity: int = Field(gt=0, description="Maximum seated student capacity")
    room_type: SessionType = Field(default=SessionType.THEORY)
    building: Optional[str] = "Main Academic Block"

    def can_accommodate(self, batch_size: int, session_type: SessionType) -> bool:
        """Check if room capacity and type match requirements."""
        return self.capacity >= batch_size and self.room_type == session_type


class Faculty(BaseModel):
    """Represents an instructor/professor."""
    id: str = Field(min_length=1)
    name: str
    department: str = "Computer Science & Engineering"
    max_hours_per_day: int = Field(default=4, ge=1, le=8)
    # Unavailable slots: list of [Day, slot_index] tuples where faculty cannot teach
    unavailable_slots: List[Tuple[DayOfWeek, int]] = Field(default_factory=list)
    # Preferred slot indices (e.g. [0, 1, 2] for mornings)
    preferred_slots: List[int] = Field(default_factory=list)

    def is_available(self, day: DayOfWeek, slot_index: int) -> bool:
        """Check if faculty is marked available at this day and slot."""
        return (day, slot_index) not in self.unavailable_slots


class StudentBatch(BaseModel):
    """Represents a cohort/section/class of students."""
    id: str = Field(min_length=1)
    name: str
    strength: int = Field(gt=0, description="Number of enrolled students")
    semester: int = Field(ge=1, le=8)


class Course(BaseModel):
    """Represents a course/subject that needs scheduling for a specific batch."""
    id: str = Field(min_length=1)
    code: str
    title: str
    batch_id: str
    faculty_id: str
    course_type: SessionType = Field(default=SessionType.THEORY)
    sessions_per_week: int = Field(gt=0, le=10, description="Number of sessions to schedule per week")
    duration_slots: int = Field(default=1, ge=1, le=4, description="1 for regular lectures, 2-3 for lab blocks")
    is_heavy: bool = Field(default=False, description="Flag for cognitively heavy theory (e.g. Algorithms, Math)")

    @field_validator("duration_slots")
    @classmethod
    def validate_duration(cls, v: int, info) -> int:
        return v


class SessionVariable(BaseModel):
    """An atomic session to be assigned slot and room by the CSP solver."""
    variable_id: str
    course_id: str
    course_code: str
    course_title: str
    batch_id: str
    faculty_id: str
    session_type: SessionType
    duration_slots: int = 1
    session_index: int
    is_heavy: bool = False

    def __hash__(self) -> int:
        return hash(self.variable_id)

    def __eq__(self, other) -> bool:
        if isinstance(other, SessionVariable):
            return self.variable_id == other.variable_id
        return False


class SlotAssignment(BaseModel):
    """Value assigned to a SessionVariable in the timetable."""
    day: DayOfWeek
    start_slot_index: int
    duration_slots: int
    room_id: str

    @property
    def occupied_slots(self) -> List[Tuple[DayOfWeek, int]]:
        """List of (day, slot_index) occupied by this continuous session."""
        return [(self.day, self.start_slot_index + i) for i in range(self.duration_slots)]

    def overlaps_in_time(self, other: "SlotAssignment") -> bool:
        """Check if two slot assignments conflict in time."""
        if self.day != other.day:
            return False
        self_slots = set(range(self.start_slot_index, self.start_slot_index + self.duration_slots))
        other_slots = set(range(other.start_slot_index, other.start_slot_index + other.duration_slots))
        return bool(self_slots & other_slots)

    def __hash__(self) -> int:
        return hash((self.day.value, self.start_slot_index, self.duration_slots, self.room_id))

    def __eq__(self, other) -> bool:
        if isinstance(other, SlotAssignment):
            return (
                self.day == other.day
                and self.start_slot_index == other.start_slot_index
                and self.duration_slots == other.duration_slots
                and self.room_id == other.room_id
            )
        return False


class TimetableEntry(BaseModel):
    """Full detail of a successfully scheduled session."""
    session: SessionVariable
    assignment: SlotAssignment
    faculty_name: str
    batch_name: str
    room_name: str
    time_label: str

