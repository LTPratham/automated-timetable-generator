"""Generates realistic academic dataset for a Computer Science & Engineering department."""

from typing import Tuple
from src.models.entities import (
    Faculty,
    Course,
    StudentBatch,
    Room,
    DayOfWeek,
    SessionType,
)
from src.models.dataset import DepartmentDataset


def create_sample_cs_department() -> DepartmentDataset:
    """Builds a rich, realistic CSE Department configuration."""
    # 1. Student Batches (4 Sections across Semesters 3, 5, 7)
    batches = [
        StudentBatch(id="CS_SEM3_A", name="B.Tech CS Sem 3 - Div A", strength=50, semester=3),
        StudentBatch(id="CS_SEM3_B", name="B.Tech CS Sem 3 - Div B", strength=50, semester=3),
        StudentBatch(id="CS_SEM5", name="B.Tech CS Sem 5", strength=55, semester=5),
        StudentBatch(id="CS_SEM7", name="B.Tech CS Sem 7", strength=50, semester=7),
    ]

    # 2. Rooms (Classrooms + Specialized Labs)
    rooms = [
        # Lecture Halls (Theory)
        Room(id="LH-101", name="Lecture Hall 101", capacity=65, room_type=SessionType.THEORY, building="Block A"),
        Room(id="LH-102", name="Lecture Hall 102", capacity=65, room_type=SessionType.THEORY, building="Block A"),
        Room(id="LH-201", name="Lecture Hall 201", capacity=70, room_type=SessionType.THEORY, building="Block B"),
        Room(id="CR-301", name="Classroom 301", capacity=55, room_type=SessionType.THEORY, building="Block B"),
        # Computing Laboratories (Labs)
        Room(id="LAB-A", name="Software Engineering Lab A", capacity=60, room_type=SessionType.LAB, building="IT Block"),
        Room(id="LAB-B", name="Systems & Networks Lab B", capacity=60, room_type=SessionType.LAB, building="IT Block"),
        Room(id="LAB-AI", name="AI & Robotics Lab", capacity=55, room_type=SessionType.LAB, building="Innovation Center"),
    ]

    # 3. Faculty Members with availability constraints and preferences
    faculty = [
        Faculty(
            id="FAC_TURING",
            name="Dr. Alan Turing",
            department="CSE",
            max_hours_per_day=3,
            preferred_slots=[0, 1],  # Prefers morning slots
            unavailable_slots=[(DayOfWeek.FRIDAY, 4), (DayOfWeek.FRIDAY, 5)],  # Research afternoon
        ),
        Faculty(
            id="FAC_LOVELACE",
            name="Dr. Ada Lovelace",
            department="CSE",
            max_hours_per_day=4,
            preferred_slots=[1, 2],
            unavailable_slots=[(DayOfWeek.MONDAY, 0)],  # Dept meetings
        ),
        Faculty(
            id="FAC_NEUMANN",
            name="Dr. John von Neumann",
            department="CSE",
            max_hours_per_day=4,
            preferred_slots=[2, 3],
            unavailable_slots=[],
        ),
        Faculty(
            id="FAC_HOPPER",
            name="Dr. Grace Hopper",
            department="CSE",
            max_hours_per_day=4,
            preferred_slots=[0, 1, 2],
            unavailable_slots=[(DayOfWeek.WEDNESDAY, 5)],
        ),
        Faculty(
            id="FAC_KNUTH",
            name="Dr. Donald Knuth",
            department="CSE",
            max_hours_per_day=3,
            preferred_slots=[3, 4],  # Prefers afternoon
            unavailable_slots=[(DayOfWeek.TUESDAY, 0), (DayOfWeek.TUESDAY, 1)],
        ),
        Faculty(
            id="FAC_DIJKSTRA",
            name="Dr. Edsger Dijkstra",
            department="CSE",
            max_hours_per_day=3,
            preferred_slots=[1, 2],
            unavailable_slots=[],
        ),
        Faculty(
            id="FAC_LISKOV",
            name="Dr. Barbara Liskov",
            department="CSE",
            max_hours_per_day=4,
            preferred_slots=[0, 1],
            unavailable_slots=[],
        ),
        Faculty(
            id="FAC_HINTON",
            name="Dr. Geoffrey Hinton",
            department="CSE",
            max_hours_per_day=3,
            preferred_slots=[4, 5],
            unavailable_slots=[(DayOfWeek.THURSDAY, 0)],
        ),
    ]

    # 4. Courses (Theory + 2-Hour Continuous Lab Blocks)
    courses = [
        # Semester 3 - Div A
        Course(
            id="C_CS301_A",
            code="CS301",
            title="Data Structures & Algorithms",
            batch_id="CS_SEM3_A",
            faculty_id="FAC_TURING",
            course_type=SessionType.THEORY,
            sessions_per_week=3,
            duration_slots=1,
            is_heavy=True,
        ),
        Course(
            id="C_CS301_LAB_A",
            code="CS301L",
            title="Data Structures Lab",
            batch_id="CS_SEM3_A",
            faculty_id="FAC_TURING",
            course_type=SessionType.LAB,
            sessions_per_week=1,
            duration_slots=2,  # 2-hour continuous block
            is_heavy=False,
        ),
        Course(
            id="C_CS302_A",
            code="CS302",
            title="Digital Logic & Architecture",
            batch_id="CS_SEM3_A",
            faculty_id="FAC_NEUMANN",
            course_type=SessionType.THEORY,
            sessions_per_week=3,
            duration_slots=1,
            is_heavy=False,
        ),
        Course(
            id="C_CS303_A",
            code="CS303",
            title="Discrete Mathematics",
            batch_id="CS_SEM3_A",
            faculty_id="FAC_DIJKSTRA",
            course_type=SessionType.THEORY,
            sessions_per_week=3,
            duration_slots=1,
            is_heavy=True,
        ),

        # Semester 3 - Div B
        Course(
            id="C_CS301_B",
            code="CS301",
            title="Data Structures & Algorithms",
            batch_id="CS_SEM3_B",
            faculty_id="FAC_KNUTH",
            course_type=SessionType.THEORY,
            sessions_per_week=3,
            duration_slots=1,
            is_heavy=True,
        ),
        Course(
            id="C_CS301_LAB_B",
            code="CS301L",
            title="Data Structures Lab",
            batch_id="CS_SEM3_B",
            faculty_id="FAC_KNUTH",
            course_type=SessionType.LAB,
            sessions_per_week=1,
            duration_slots=2,
            is_heavy=False,
        ),
        Course(
            id="C_CS302_B",
            code="CS302",
            title="Digital Logic & Architecture",
            batch_id="CS_SEM3_B",
            faculty_id="FAC_NEUMANN",
            course_type=SessionType.THEORY,
            sessions_per_week=3,
            duration_slots=1,
            is_heavy=False,
        ),
        Course(
            id="C_CS303_B",
            code="CS303",
            title="Discrete Mathematics",
            batch_id="CS_SEM3_B",
            faculty_id="FAC_DIJKSTRA",
            course_type=SessionType.THEORY,
            sessions_per_week=3,
            duration_slots=1,
            is_heavy=True,
        ),

        # Semester 5
        Course(
            id="C_CS501",
            code="CS501",
            title="Database Management Systems",
            batch_id="CS_SEM5",
            faculty_id="FAC_LISKOV",
            course_type=SessionType.THEORY,
            sessions_per_week=3,
            duration_slots=1,
            is_heavy=False,
        ),
        Course(
            id="C_CS501_LAB",
            code="CS501L",
            title="Database Systems Lab",
            batch_id="CS_SEM5",
            faculty_id="FAC_LISKOV",
            course_type=SessionType.LAB,
            sessions_per_week=1,
            duration_slots=2,
            is_heavy=False,
        ),
        Course(
            id="C_CS502",
            code="CS502",
            title="Operating Systems",
            batch_id="CS_SEM5",
            faculty_id="FAC_HOPPER",
            course_type=SessionType.THEORY,
            sessions_per_week=3,
            duration_slots=1,
            is_heavy=True,
        ),
        Course(
            id="C_CS502_LAB",
            code="CS502L",
            title="Operating Systems Lab",
            batch_id="CS_SEM5",
            faculty_id="FAC_HOPPER",
            course_type=SessionType.LAB,
            sessions_per_week=1,
            duration_slots=2,
            is_heavy=False,
        ),

        # Semester 7
        Course(
            id="C_CS701",
            code="CS701",
            title="Artificial Intelligence & ML",
            batch_id="CS_SEM7",
            faculty_id="FAC_HINTON",
            course_type=SessionType.THEORY,
            sessions_per_week=3,
            duration_slots=1,
            is_heavy=True,
        ),
        Course(
            id="C_CS701_LAB",
            code="CS701L",
            title="AI & Machine Learning Lab",
            batch_id="CS_SEM7",
            faculty_id="FAC_HINTON",
            course_type=SessionType.LAB,
            sessions_per_week=1,
            duration_slots=2,
            is_heavy=False,
        ),
        Course(
            id="C_CS702",
            code="CS702",
            title="Compiler Design & Theory",
            batch_id="CS_SEM7",
            faculty_id="FAC_LOVELACE",
            course_type=SessionType.THEORY,
            sessions_per_week=3,
            duration_slots=1,
            is_heavy=True,
        ),
    ]

    return DepartmentDataset(
        name="Department of Computer Science & Engineering",
        faculty=faculty,
        courses=courses,
        batches=batches,
        rooms=rooms,
    )

