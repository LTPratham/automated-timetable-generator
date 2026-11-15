# 📅 Automated Timetable Generation System using Constraint-Based Search (CSP)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg)](https://streamlit.io)
[![OR-Tools](https://img.shields.io/badge/Google%20OR--Tools-9.15+-orange.svg)](https://developers.google.com/optimization)
[![Tests Passing](https://img.shields.io/badge/tests-14%20passed-brightgreen.svg)]()
[![Responsible AI](https://img.shields.io/badge/Fairness-Gini%200.081-success.svg)]()

> **Course Project:** CSE276 · Artificial Intelligence Foundations (2026–27)  
> **Institution:** Lovely Professional University (LPU)  
> **Section:** K4P25CB | **Group 18** | **Project 20**  
> **Assigned Problem Statement:** *Automated Timetable Generation using Constraint-Based Search*

---

## 👥 Project Team & Collaborators

| Name | Role / Focus | Reg. No. | Roll No. | GitHub |
| :--- | :--- | :--- | :--- | :--- |
| **Sawarkar Prathmesh Arun** | Project Lead & Core CSP Search Engine | `12509401` | 47 | [`@LTPratham`](https://github.com/LTPratham) |
| **Siya Gupta** | Algorithm Design, Frontend UI & Guided Tour | `12505235` | 23 | [`@siyagupta3103`](https://github.com/siyagupta3103) |
| **Bhavya Verma** | Fairness Audit, Testing & Documentation | `12513794` | 44 | [`@bhavyaverma81`](https://github.com/bhavyaverma81) |

---

## 🌟 Key Platform Features

1. **Academic Rigor (Pure Python CSP Engine)**:
   - Zero-external-dependency classical CSP solver implementing:
     - Backtracking Search with state rollback.
     - **Minimum Remaining Values (MRV)** & **Degree Heuristic** for variable ordering.
     - **Least Constraining Value (LCV)** for value ordering.
     - **Forward Checking (FC)** & **AC-3 Arc Consistency** for domain pruning.
2. **Head-to-Head Algorithm Arena (4 Optimization Paradigms)**:
   - **Backtracking + MRV/FC** (Constraint Propagation)
   - **Google OR-Tools CP-SAT** (Industrial SAT Solver)
   - **Genetic Algorithm** (Evolutionary Chromosome Crossover & Mutation)
   - **Min-Conflicts** (Local Search Iterative Repair)
3. **Click-to-Explain Session Inspector (Rubric Component 5)**:
   - Click on any class card to inspect verified zero-tolerance hard constraints (faculty exclusivity, room capacity fit, lab continuity) and algorithmic search traces.
4. **Responsible AI & Workload Equity Audit (Rubric Component 5)**:
   - Gini coefficient evaluation of teaching hours across professors ($Gini = 0.081$, indicating high equity).
   - Student cohort morning vs afternoon fatigue distribution.
   - PII-free privacy compliance and documented failure modes.
5. **Interactive Step-by-Step Search Visualizer**:
   - Step forward/backward through the CSP search tree to watch the AI select variables, prune domains, and backtrack live with MRV diagnostics.
6. **Conversational AI Timetable Copilot**:
   - Natural language assistant answering scheduling queries: busiest faculty, professor availability, room usage, and instant what-if contingencies.
7. **5-Axis Multi-Objective Quality Radar**:
   - Evaluates schedule fitness across mathematical constraint integrity, faculty equity, student spacing, campus room efficiency, and morning/afternoon distribution.
8. **Mobile Calendar QR Sync & Master Grid**:
   - Instant scannable QR codes for mobile sync into Google & Apple Calendar, plus a Master University Grid view across all student cohorts.
9. **Emergency "What-If" Rescheduler**:
   - Dynamic simulation for sudden faculty sick leave or room maintenance shutdowns, reallocating sessions with minimal schedule perturbation.
10. **Interactive Conflict Network**:
   - Force-directed **NetworkX** graph visualizing course clashing relationships and chromatic slot coloring (Graph Coloring).
11. **One-Click Multi-Format Export**:
   - Formatted color-coded **Excel (.xlsx)** workbooks.
   - Print-ready notice-board **PDF (.pdf)** documents.
   - RFC 5545 **iCalendar (.ics)** direct sync with Google Calendar, Outlook, and Apple Calendar.

---

## 📐 Mathematical Formulation

### 1. Variables ($X$)
Every atomic weekly session is modeled as a discrete CSP variable:
$$X = \{ S_{c, b, t, k} \}$$
Where $c$ = Course ID, $b$ = Student Cohort, $t \in \{\text{Theory}, \text{Lab}\}$, and $k$ = Session index.

### 2. Domains ($D_i$)
Permissible slot-room tuples:
$$D_i \subseteq \{ (d, s, r) \mid d \in \text{Days}, s \in \text{Slots}, r \in \text{Rooms} \}$$

### 3. Hard Constraints (Zero-Tolerance)
- **Faculty Exclusivity**: No faculty member scheduled for overlapping sessions.
- **Room Exclusivity**: No physical classroom or laboratory double-booked.
- **Batch Exclusivity**: Student cohorts cannot attend simultaneous lectures.
- **Room Capacity Fit**: $\text{Capacity}(r) \ge \text{Enrollment}(b)$.
- **Room Type Match**: Lab sessions scheduled only in certified laboratory facilities.
- **Lab Continuity**: Continuous multi-hour practical blocks without interval splitting.
- **Faculty Availability**: Sessions never scheduled in professor blackout slots.

### 4. Soft Constraints (Optimization Objectives)
- Minimize faculty idle gap hours between classes on the same day ($w = 5.0$).
- Satisfy faculty morning/afternoon slot preferences ($w = 2.0$).
- Avoid back-to-back heavy theory lectures for students ($w = 8.0$).

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Web Platform
```bash
python run_app.py
```
- **Web Dashboard:** [http://localhost:8000](http://localhost:8000)
- **Showcase Landing Page:** [http://localhost:8000/landing.html](http://localhost:8000/landing.html)
- **Interactive REST API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Run Automated Tests
```bash
python -m pytest -v
```

---

## 📂 Project Structure

```text
d:/prathamesh ai project/prathamesh ai project/
├── frontend/
│   ├── index.html         # Interactive token-driven web dashboard
│   └── landing.html       # Academic showcase landing page
├── src/
│   ├── models/            # Pydantic schemas (Entities, Batches, Rooms, Courses)
│   ├── core/              # Pure CSP engine (Variables, Constraints, Heuristics, Backtracking, Stepper)
│   ├── solvers/           # Benchmarks (Min-Conflicts, OR-Tools CP-SAT, Genetic Algorithm)
│   ├── analytics/         # Soft scorer, Conflict graphs, What-If rescheduler, Explainability, Fairness
│   ├── exporter/          # Excel, PDF, and iCalendar export engines
│   └── api.py             # FastAPI backend REST API
├── documentation/
│   ├── main-documentation/ # PRD, System Architecture, Workflows
│   ├── progress-tracking/  # Progress tracking
│   ├── licensing/          # Academic license
│   └── viva-prep-guide.md  # Comprehensive viva Q&A defense guide
├── tests/                 # Automated pytest suite (13 tests)
├── requirements.txt       # Dependencies
└── run_app.py             # Desktop launcher
```
