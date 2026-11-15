"""FastAPI Backend Server & REST API for Automated Timetable CSP Engine.

Provides clean REST endpoints for:
- Solving timetables via Backtracking, OR-Tools, Min-Conflicts
- Head-to-head algorithm benchmarking
- Real-time What-If emergency rescheduling
- Dynamic conflict graph generation
- Multi-format exports (Excel, PDF, iCal)
- Full OpenAPI / Swagger documentation at /docs
"""

import os
from io import BytesIO
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from src.data.sample_generator import create_sample_cs_department
from src.core.problem_builder import build_timetable_csp
from src.core.backtracking import BacktrackingSolver
from src.solvers.min_conflicts import MinConflictsSolver
from src.solvers.ortools_solver import ORToolsTimetableSolver
from src.solvers.genetic_solver import GeneticTimetableSolver
from src.solvers.benchmark import run_comprehensive_benchmark
from src.core.stepper import generate_search_execution_trace
from src.analytics.penalty_scorer import SoftConstraintScorer
from src.analytics.conflict_graph import build_conflict_graph
from src.analytics.rescheduler import WhatIfRescheduler
from src.analytics.explainability import generate_session_explanation
from src.analytics.fairness import audit_fairness_and_ethics
from src.analytics.copilot import process_copilot_query, compute_quality_radar
from src.exporter.excel_export import export_timetable_to_excel
from src.exporter.pdf_export import export_timetable_to_pdf
from src.exporter.ical_export import export_timetable_to_ics
from src.models.entities import DayOfWeek, SessionType, Faculty, Course, Room
from src.models.dataset import DepartmentDataset

app = FastAPI(
    title="Automated Academic Timetable CSP Platform API",
    description="RESTful AI API powered by Constraint Satisfaction Problem algorithms, MRV/Degree heuristics, AC-3, and Google OR-Tools CP-SAT.",
    version="1.0.0",
)

from starlette.middleware.base import BaseHTTPMiddleware

class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

app.add_middleware(NoCacheMiddleware)

# Global in-memory state
STATE: Dict[str, Any] = {
    "dataset": create_sample_cs_department(),
    "current_schedule": None,
    "last_stats": None,
}

# Pre-solve default schedule at boot
def _solve_initial():
    csp, _ = build_timetable_csp(STATE["dataset"])
    solver = BacktrackingSolver(use_mrv=True, use_degree=True, use_lcv=False, inference="forward_checking")
    sol, stats = solver.solve(csp)
    STATE["current_schedule"] = sol
    STATE["last_stats"] = stats

_solve_initial()


# --- REQUEST & RESPONSE SCHEMAS ---
class SolveRequest(BaseModel):
    algorithm: str = "backtracking_fc"  # "backtracking_fc", "backtracking_none", "ortools", "min_conflicts"


class CopilotQueryRequest(BaseModel):
    query: str


class FacultyLeaveRequest(BaseModel):
    faculty_id: str
    leave_day: str  # e.g. "Friday"


class RoomClosureRequest(BaseModel):
    room_id: str
    closure_day: str  # e.g. "Monday"


class AddFacultyRequest(BaseModel):
    id: str
    name: str
    department: str = "Computer Science & Engineering"
    max_hours_per_day: int = 4
    preferred_slots: list[int] = [0, 1, 2]


class AddCourseRequest(BaseModel):
    code: str
    title: str
    batch_id: str
    faculty_id: str
    course_type: str = "THEORY"  # "THEORY" or "LAB"
    sessions_per_week: int = 3
    duration_slots: int = 1
    is_heavy: bool = False


class AddRoomRequest(BaseModel):
    id: str
    name: str
    capacity: int
    room_type: str = "THEORY"  # "THEORY" or "LAB"
    building: str = "Academic Block A"


# --- API ENDPOINTS ---

@app.get("/api/state")
def get_current_state():
    """Returns the current dataset, schedule, and KPI metrics."""
    dataset: DepartmentDataset = STATE["dataset"]
    schedule = STATE["current_schedule"]

    if not schedule:
        return {"solved": False, "dataset": dataset.model_dump()}

    scorer = SoftConstraintScorer()
    report = scorer.evaluate(schedule, dataset)

    # Format schedule entries for JSON consumption
    serialized_entries = []
    for var, assign in schedule.items():
        fac = dataset.faculty_by_id.get(var.faculty_id)
        room = dataset.rooms_by_id.get(assign.room_id)
        batch = dataset.batches_by_id.get(var.batch_id)
        serialized_entries.append(
            {
                "variable_id": var.variable_id,
                "course_code": var.course_code,
                "course_title": var.course_title,
                "batch_id": var.batch_id,
                "batch_name": batch.name if batch else var.batch_id,
                "faculty_id": var.faculty_id,
                "faculty_name": fac.name if fac else var.faculty_id,
                "session_type": var.session_type.value,
                "duration_slots": var.duration_slots,
                "day": assign.day.value,
                "start_slot_index": assign.start_slot_index,
                "occupied_slots": [s for _, s in assign.occupied_slots],
                "room_id": assign.room_id,
                "room_name": room.name if room else assign.room_id,
                "is_heavy": var.is_heavy,
            }
        )

    return {
        "solved": True,
        "kpi": {
            "total_sessions": len(schedule),
            "weekly_hours": sum(v.duration_slots for v in schedule.keys()),
            "hard_conflicts": 0,
            "soft_penalty": round(report.total_penalty, 1),
            "batches_count": len(dataset.batches),
            "faculty_count": len(dataset.faculty),
            "rooms_count": len(dataset.rooms),
            "solve_time_ms": round(STATE["last_stats"].time_taken_ms, 1) if STATE.get("last_stats") else 0,
            "algorithm": STATE["last_stats"].algorithm_name if STATE.get("last_stats") else "Pure CSP Backtracking",
        },
        "days": [d.value for d in dataset.days],
        "slot_times": dataset.slot_times,
        "batches": [b.model_dump() for b in dataset.batches],
        "faculty": [f.model_dump() for f in dataset.faculty],
        "rooms": [r.model_dump() for r in dataset.rooms],
        "schedule": serialized_entries,
    }


@app.post("/api/solve")
def solve_timetable(req: SolveRequest):
    """Solves the timetable using the chosen AI algorithm."""
    dataset: DepartmentDataset = STATE["dataset"]

    if req.algorithm == "ortools":
        solver = ORToolsTimetableSolver()
        sol, stats = solver.solve(dataset)
    elif req.algorithm == "min_conflicts":
        csp, _ = build_timetable_csp(dataset)
        solver = MinConflictsSolver()
        sol, stats = solver.solve(csp)
    elif req.algorithm == "genetic":
        csp, _ = build_timetable_csp(dataset)
        solver = GeneticTimetableSolver()
        sol, stats = solver.solve(csp, dataset)
    elif req.algorithm == "backtracking_none":
        csp, _ = build_timetable_csp(dataset)
        solver = BacktrackingSolver(use_mrv=True, use_degree=True, use_lcv=False, inference="none")
        sol, stats = solver.solve(csp)
    else:
        csp, _ = build_timetable_csp(dataset)
        solver = BacktrackingSolver(use_mrv=True, use_degree=True, use_lcv=False, inference="forward_checking")
        sol, stats = solver.solve(csp)

    if sol is None:
        raise HTTPException(status_code=422, detail="Solver timed out or found constraints unsatisfiable.")

    STATE["current_schedule"] = sol
    STATE["last_stats"] = stats
    return {"success": True, "time_ms": stats.time_taken_ms, "algorithm": stats.algorithm_name}


@app.get("/api/benchmark")
def get_benchmarks():
    """Runs head-to-head performance benchmarks between all algorithms."""
    dataset: DepartmentDataset = STATE["dataset"]
    results = run_comprehensive_benchmark(dataset, time_limit_sec=15.0)
    return {
        "results": [
            {
                "algorithm": r.algorithm,
                "solved": r.solved,
                "time_ms": r.time_ms,
                "nodes_or_steps": r.nodes_or_steps,
                "backtracks_or_conflicts": r.backtracks_or_conflicts,
                "penalty_score": r.penalty_score if r.penalty_score != float("inf") else None,
                "notes": r.notes,
            }
            for r in results
        ]
    }


@app.post("/api/reschedule/faculty-leave")
def reschedule_faculty_leave(req: FacultyLeaveRequest):
    """Simulates sudden faculty leave and auto-reschedules with minimal disruption."""
    dataset: DepartmentDataset = STATE["dataset"]
    current_schedule = STATE["current_schedule"]
    if not current_schedule:
        raise HTTPException(status_code=400, detail="No active schedule available.")

    rescheduler = WhatIfRescheduler(dataset)
    day_enum = DayOfWeek(req.leave_day)
    new_sched, report = rescheduler.handle_faculty_leave(current_schedule, req.faculty_id, day_enum)

    if report.success:
        STATE["current_schedule"] = new_sched
        return {
            "success": True,
            "message": report.message,
            "reassigned_count": len(report.reassigned_sessions),
            "reassigned_details": [
                {
                    "course_code": var.course_code,
                    "batch_id": var.batch_id,
                    "old_slot": f"{old_a.day.value} Slot {old_a.start_slot_index}",
                    "new_slot": f"{new_a.day.value} Slot {new_a.start_slot_index}",
                    "room": new_a.room_id,
                }
                for var, old_a, new_a in report.reassigned_sessions
            ],
        }
    else:
        return {"success": False, "message": report.message}


@app.post("/api/reschedule/room-closure")
def reschedule_room_closure(req: RoomClosureRequest):
    """Simulates room maintenance closure and auto-reroutes rooms without time changes."""
    dataset: DepartmentDataset = STATE["dataset"]
    current_schedule = STATE["current_schedule"]
    if not current_schedule:
        raise HTTPException(status_code=400, detail="No active schedule available.")

    rescheduler = WhatIfRescheduler(dataset)
    day_enum = DayOfWeek(req.closure_day)
    new_sched, report = rescheduler.handle_room_closure(current_schedule, req.room_id, day_enum)

    if report.success:
        STATE["current_schedule"] = new_sched
        return {
            "success": True,
            "message": report.message,
            "reassigned_count": len(report.reassigned_sessions),
            "reassigned_details": [
                {
                    "course_code": var.course_code,
                    "batch_id": var.batch_id,
                    "slot": f"{new_a.day.value} Slot {new_a.start_slot_index}",
                    "old_room": old_a.room_id,
                    "new_room": new_a.room_id,
                }
                for var, old_a, new_a in report.reassigned_sessions
            ],
        }
    else:
        return {"success": False, "message": report.message}


@app.get("/api/conflict-graph")
def get_conflict_graph_data():
    """Returns nodes and edges of the NetworkX course clash graph for interactive visualization."""
    dataset: DepartmentDataset = STATE["dataset"]
    current_schedule = STATE["current_schedule"]
    G = build_conflict_graph(dataset, current_schedule)

    nodes = []
    for n in G.nodes():
        attrs = G.nodes[n]
        nodes.append(
            {
                "id": n,
                "label": attrs["label"],
                "course_code": attrs["course_code"],
                "faculty_id": attrs["faculty_id"],
                "batch_id": attrs["batch_id"],
                "session_type": attrs["session_type"],
                "slot_label": attrs["slot_label"],
                "color": attrs["color"],
            }
        )

    edges = [{"source": u, "target": v, "reason": G.edges[u, v].get("reason", "")} for u, v in G.edges()]

    return {"nodes": nodes, "edges": edges, "nodes_count": G.number_of_nodes(), "edges_count": G.number_of_edges()}


@app.get("/api/explain/{variable_id}")
def get_session_explanation(variable_id: str):
    """Returns granular explainability and constraint satisfaction proof for a specific session."""
    dataset: DepartmentDataset = STATE["dataset"]
    schedule = STATE["current_schedule"]
    if not schedule:
        raise HTTPException(status_code=400, detail="No active schedule available.")

    target_var = None
    target_assign = None
    for var, assign in schedule.items():
        if var.variable_id == variable_id:
            target_var = var
            target_assign = assign
            break

    if not target_var or not target_assign:
        raise HTTPException(status_code=404, detail="Session variable not found in current timetable.")

    explanation = generate_session_explanation(target_var, target_assign, dataset, schedule)
    return explanation


@app.get("/api/fairness")
def get_fairness_audit():
    """Returns Responsible AI, faculty workload equity, and student fatigue metrics."""
    dataset: DepartmentDataset = STATE["dataset"]
    schedule = STATE["current_schedule"]
    if not schedule:
        raise HTTPException(status_code=400, detail="No active schedule available.")

    audit = audit_fairness_and_ethics(schedule, dataset)
    return audit


@app.get("/api/search-trace")
def get_search_trace():
    """Generates and returns step-by-step backtracking search execution steps."""
    dataset: DepartmentDataset = STATE["dataset"]
    csp, _ = build_timetable_csp(dataset)
    trace = generate_search_execution_trace(csp, dataset, max_steps=80)
    return {"total_steps": len(trace), "steps": trace}


@app.post("/api/custom/faculty")
def add_custom_faculty(req: AddFacultyRequest):
    """Adds a new faculty member dynamically to the active department."""
    dataset: DepartmentDataset = STATE["dataset"]
    if req.id in dataset.faculty_by_id:
        raise HTTPException(status_code=400, detail=f"Faculty ID '{req.id}' already exists.")
    new_fac = Faculty(
        id=req.id,
        name=req.name,
        department=req.department,
        max_hours_per_day=req.max_hours_per_day,
        preferred_slots=req.preferred_slots,
    )
    dataset.faculty.append(new_fac)
    return {"success": True, "message": f"Faculty '{req.name}' successfully added to department."}


@app.post("/api/custom/course")
def add_custom_course(req: AddCourseRequest):
    """Adds a new course curriculum dynamically and automatically updates the timetable."""
    dataset: DepartmentDataset = STATE["dataset"]
    if req.faculty_id not in dataset.faculty_by_id:
        raise HTTPException(status_code=400, detail=f"Unknown Faculty ID '{req.faculty_id}'.")
    if req.batch_id not in dataset.batches_by_id:
        raise HTTPException(status_code=400, detail=f"Unknown Batch ID '{req.batch_id}'.")
    c_id = f"course_{req.code.lower()}_{len(dataset.courses)+1}"
    new_course = Course(
        id=c_id,
        code=req.code,
        title=req.title,
        batch_id=req.batch_id,
        faculty_id=req.faculty_id,
        course_type=SessionType(req.course_type),
        sessions_per_week=req.sessions_per_week,
        duration_slots=req.duration_slots,
        is_heavy=req.is_heavy,
    )
    dataset.courses.append(new_course)
    _solve_initial()
    return {"success": True, "message": f"Course '{req.code}' added & timetable regenerated."}


@app.post("/api/custom/room")
def add_custom_room(req: AddRoomRequest):
    """Adds a new physical classroom or laboratory dynamically."""
    dataset: DepartmentDataset = STATE["dataset"]
    if req.id in dataset.rooms_by_id:
        raise HTTPException(status_code=400, detail=f"Room ID '{req.id}' already exists.")
    new_room = Room(
        id=req.id,
        name=req.name,
        capacity=req.capacity,
        room_type=SessionType(req.room_type),
        building=req.building,
    )
    dataset.rooms.append(new_room)
    return {"success": True, "message": f"Room '{req.name}' successfully added."}


@app.post("/api/custom/reset")
def reset_custom_dataset():
    """Resets department dataset back to the clean benchmark configuration."""
    STATE["dataset"] = create_sample_cs_department()
    _solve_initial()
    return {"success": True, "message": "Department dataset reset to default benchmark."}


@app.post("/api/copilot")
def copilot_query(req: CopilotQueryRequest):
    """Processes natural language scheduling queries via AI Copilot."""
    dataset: DepartmentDataset = STATE["dataset"]
    schedule = STATE["current_schedule"]
    if not schedule:
        raise HTTPException(status_code=400, detail="No active schedule available.")
    return process_copilot_query(req.query, dataset, schedule)


@app.get("/api/quality/radar")
def get_quality_radar():
    """Calculates 5-dimensional holistic timetable quality score and radar chart data."""
    dataset: DepartmentDataset = STATE["dataset"]
    schedule = STATE["current_schedule"]
    if not schedule:
        raise HTTPException(status_code=400, detail="No active schedule available.")
    return compute_quality_radar(dataset, schedule)


# --- EXPORT ENDPOINTS ---

@app.get("/api/export/excel")
def download_excel():
    """Generates and downloads styled multi-sheet Excel timetable."""
    dataset: DepartmentDataset = STATE["dataset"]
    current_schedule = STATE["current_schedule"]
    buf = export_timetable_to_excel(dataset, current_schedule)
    return Response(
        content=buf.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Academic_Timetable.xlsx"},
    )


@app.get("/api/export/pdf")
def download_pdf():
    """Generates and downloads print-ready landscape PDF timetable."""
    dataset: DepartmentDataset = STATE["dataset"]
    current_schedule = STATE["current_schedule"]
    buf = export_timetable_to_pdf(dataset, current_schedule)
    return Response(
        content=buf.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=Academic_Timetable.pdf"},
    )


@app.get("/api/export/ical")
def download_ical():
    """Generates and downloads iCalendar (.ics) format."""
    dataset: DepartmentDataset = STATE["dataset"]
    current_schedule = STATE["current_schedule"]
    ics_text = export_timetable_to_ics(dataset, current_schedule)
    return Response(
        content=ics_text,
        media_type="text/calendar",
        headers={"Content-Disposition": "attachment; filename=Academic_Timetable.ics"},
    )


# Serve frontend static assets
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
