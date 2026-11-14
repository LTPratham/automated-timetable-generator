# 📅 Automated Academic Timetable Generation System using Constraint Satisfaction (CSP)

**Course:** CSE276 – Artificial Intelligence Foundations | Academic Session 2026–27  
**Institution:** Lovely Professional University (LPU)  
**Section:** K4P25CB | **Group:** 18 | **Project No.:** 20  
**GitHub Repository:** *[URL to be added after push]*  

---

## 👥 Team Members & Responsibilities

| # | Name | Registration No. | Roll No. | GitHub Profile | Project Responsibilities |
|---|---|---|---|---|---|
| 1 | **Sawarkar Prathmesh Arun** | 12509401 | — | — | Project Lead & Core CSP Search Engine Architecture |
| 2 | **Siya Gupta** | 12505235 | 23 | [@siyagupta3103](https://github.com/siyagupta3103) | Algorithm Design, Web UI & Interactive Guided Tour |
| 3 | **Bhavya Verma** | 12513794 | 44 | [@bhavyaverma81](https://github.com/bhavyaverma81) | Responsible AI Fairness Audit, Testing & Documentation |

---

## 📋 Project Summary & Problem Abstract

University academic scheduling is an **NP-hard Constraint Satisfaction Problem (CSP)**. Manually placing lectures and lab sessions across classrooms and time slots while satisfying strict physical constraints (zero instructor clashes, zero room clashes, zero student cohort overlaps, strict room capacity limits) is highly error-prone and time-consuming.

Our system formulates timetable scheduling as a deterministic, mathematically sound **Constraint Satisfaction Problem (CSP)** and solves it using four state-of-the-art AI optimization paradigms:
1. **Classical Backtracking Search** with **MRV** (Minimum Remaining Values), **Degree Heuristic**, **LCV** (Least Constraining Value), and **Forward Checking / AC-3**.
2. **Google OR-Tools CP-SAT Solver** (Industrial SAT-based constraint solver).
3. **Simulated Annealing** (Physics-inspired metaheuristic search).
4. **Genetic Algorithm** (Evolutionary chromosome crossover, elitism, and stochastic mutation).

The platform includes an interactive, browser-based dashboard with instant conflict detection, step-by-step search visualization, an explainable AI inspector, a Responsible AI fairness audit (Gini index), what-if drag-and-drop rescheduling, multi-format exports (PDF, Excel, iCal), and a 9-step interactive guided tour for new users.

---

## 🛠️ Technologies & Tools Used

- **Core Backend:** Python 3.11+, FastAPI (high-performance asynchronous REST API)
- **AI & Optimization:** Google OR-Tools (CP-SAT), NetworkX (Constraint Graph & Bipartite Conflict Analysis)
- **Data Validation & Modeling:** Pydantic v2
- **Frontend & Visualization:** Responsive HTML5/CSS3/JavaScript (Single Page Application), Plotly.js (Real-time benchmark charts)
- **Export & Document Processing:** ReportLab (Print-ready PDF), OpenPyXL (Excel spreadsheets), iCalendar (.ics calendar integration)
- **Testing & Quality Assurance:** Pytest (13 unit tests, 100% passing)

---

## 🌟 Key Features Built

1. **Pure Python Classical CSP Engine:** Backtracking with state rollback, MRV, LCV, and Forward Checking.
2. **Multi-Paradigm Algorithm Arena:** Head-to-head benchmarking comparing Backtracking, OR-Tools, Simulated Annealing, and Genetic Algorithm.
3. **Explainable AI (XAI) Inspector:** Click any assigned session cell to view human-readable reasoning of why it was scheduled in that slot and what alternatives were rejected.
4. **Responsible AI & Workload Fairness Audit:** Computes Gini inequality index for faculty teaching loads and classroom utilization to avoid burnout and underutilization.
5. **Interactive 9-Step Guided Tour:** Automatically introduces new users to all controls and panels upon their first visit.
6. **Live What-If Rescheduler:** Instant clash analysis when moving or reassigning sessions.
7. **Multi-Format Export Engine:** One-click export to official PDF timetable, Excel workbook, and calendar invite (.ics).
8. **Academic Showcase Landing Page:** Presentation-ready introduction page highlighting system architecture and live links.

---

## 📸 Screenshots

- **Landing Page Showcase:** `documentation/screenshots/landing_page.png`
- **Interactive Generator Dashboard:** `documentation/screenshots/dashboard.png`

*(Note: See `documentation/PROJECT_SUBMISSION_REPORT.pdf` or `PROJECT_SUBMISSION_REPORT.html` for embedded high-resolution visual layout).*
