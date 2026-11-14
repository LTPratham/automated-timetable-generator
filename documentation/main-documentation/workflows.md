# Operational Workflows

## Workflow 1: Timetable Generation Lifecycle
1. **Dataset Loading**: Ingestion of department entities (`faculty.csv`, `rooms.csv`, `courses.csv`, `batches.csv`).
2. **CSP Problem Formulation**:
   - Variables instantiated for each session block (theory=1h, lab=2h).
   - Initial domain generated: Cartesian product of $(Days \times Slots \times EligibleRooms)$.
   - Unary constraints applied (capacity fit, lab equipment, faculty availability) to prune domains before search.
3. **Backtracking Search Execution**:
   - Variable selection: MRV chooses variable with minimum remaining values.
   - Value assignment: Slot-room tuple assigned.
   - Forward Checking: Conflicting tuples immediately purged from unassigned neighbors.
   - Backtrack: If any domain is emptied, search state is rolled back and an alternate value is explored.
4. **Soft Penalty Evaluation**: Evaluated against faculty idle gap hours and preferred slots.
5. **Multi-Perspective Rendering**: Timetable projected onto Batch, Faculty, and Room matrices.

---

## Workflow 2: What-If Emergency Rescheduling
1. **Disruption Injection**: User selects absent faculty or closed facility + target day.
2. **Impact Isolation**: System flags only the sessions directly affected on that day.
3. **Constrained Reallocation**:
   - For room closure: Swaps physical rooms at the same time slot with another eligible room.
   - For faculty leave: Reallocates sessions to empty slots on other days while freezing all unrelated sessions.
4. **Delta Audit**: Outputs a clear diff report showing shifted sessions without perturbing the campus schedule.
