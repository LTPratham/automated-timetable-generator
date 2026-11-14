# Product Requirements Document (PRD)

## Project Details
- **Course**: CSE276 · Artificial Intelligence Foundations
- **Academic Session**: 2026–27
- **Institution**: Lovely Professional University (LPU)
- **Section**: K4P25CB
- **Group 18**:
  - S V Pavan Kumar Kondamuri (`12509779`)
  - Sawarkar Prathmesh Arun (`12509401`)
  - Jeet Nag (`12511135`)
- **Assigned Topic**: Project 20 — Automated Timetable Generation using Constraint-Based Search

---

## 1. Problem Definition & Real-World Scope
University academic scheduling is an NP-hard combinatorial problem. Scheduling hundreds of sessions across limited facilities while honoring room capacities, instructor availability, and student cohorts leads to severe human bottlenecking and frequent scheduling clashes.

The objective of this platform is to formulate timetable scheduling as a deterministic **Constraint Satisfaction Problem (CSP)** that guarantees 100% hard-conflict-free schedules while optimizing faculty comfort and student cognitive load.

---

## 2. Mathematical AI Problem Formulation

### Variables ($X$)
Every course session to be scheduled is an atomic variable:
$$X = \{ S_{c, b, t, k} \}$$
Where:
- $c$: Course identifier (e.g., CS101)
- $b$: Student cohort / batch (e.g., Batch CS-A)
- $t \in \{\text{Theory}, \text{Lab}\}$: Pedagogical session type
- $k$: Session sequence index within the week

### Domains ($D_i$)
The domain of permissible assignments consists of $(day, slot, room)$ tuples:
$$D_i \subseteq \{ (d, s, r) \mid d \in \text{Days}, s \in \text{Slots}, r \in \text{Rooms} \}$$

### Hard Constraints (Zero-Tolerance)
1. **Faculty Exclusivity**: $\forall s_1, s_2$, if $\text{Faculty}(s_1) = \text{Faculty}(s_2)$, then $\text{Time}(s_1) \cap \text{Time}(s_2) = \emptyset$.
2. **Room Exclusivity**: $\forall s_1, s_2$, if $\text{Room}(s_1) = \text{Room}(s_2)$, then $\text{Time}(s_1) \cap \text{Time}(s_2) = \emptyset$.
3. **Cohort Exclusivity**: $\forall s_1, s_2$, if $\text{Batch}(s_1) = \text{Batch}(s_2)$, then $\text{Time}(s_1) \cap \text{Time}(s_2) = \emptyset$.
4. **Capacity Fit**: $\text{Capacity}(\text{Room}(s_i)) \ge \text{Strength}(\text{Batch}(s_i))$.
5. **Lab Room Qualification**: $\text{Type}(s_i) = \text{Lab} \implies \text{RoomType}(\text{Room}(s_i)) = \text{Lab}$.
6. **Lab Continuity**: Practical sessions must span 2 contiguous slots without interruption.
7. **Faculty Blackout**: Sessions must not coincide with declared instructor unavailability.

### Soft Constraints (Optimization Objective)
1. **Minimize Faculty Idle Gap Hours**: Penalize disjoint teaching gaps on the same day ($w=5.0$).
2. **Satisfy Faculty Time Preferences**: Morning or afternoon preferences ($w=2.0$).
3. **Avoid Back-to-Back Heavy Lectures**: Prevent student cognitive burnout ($w=8.0$).

---

## 3. Implemented AI Algorithms
1. **Classical CSP Backtracking with Forward Checking (FC) & Arc Consistency (AC-3)**.
2. **Variable Ordering Heuristics**: Minimum Remaining Values (MRV) and Degree Heuristic.
3. **Value Ordering Heuristic**: Least Constraining Value (LCV).
4. **Local Search**: Min-Conflicts algorithm.
5. **Industrial CP Benchmark**: Google OR-Tools CP-SAT.

---

## 4. Deliverables & Outputs
- **Interactive Web Application**: Token-driven interface with multi-perspective grids (Student Batch, Faculty, Room).
- **Algorithm Arena**: Real-time benchmarking of search time, nodes explored, and backtracks.
- **Explainability Inspector**: Click-to-explain modal detailing constraint satisfaction proofs for any class.
- **Responsible AI Audit**: Workload Gini coefficient, student fatigue spread, and ethical transparency disclosures.
- **What-If Emergency Rescheduler**: Dynamic perturbation-minimizing replanning for faculty sick leave or room closures.
- **Multi-Format Exporters**: Excel (.xlsx), PDF (.pdf), and iCalendar (.ics).
