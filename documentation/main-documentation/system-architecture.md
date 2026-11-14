# System Architecture

## 1. Architectural Overview
The platform follows a clean decoupled architecture separating core AI search algorithms, analytical audit modules, REST APIs, and presentation layers.

```
                           +---------------------------+
                           |   Presentation Layer      |
                           |  (FastAPI / Streamlit UI) |
                           +-------------+-------------+
                                         |
                                         v
                           +---------------------------+
                           |     FastAPI REST API      |
                           |   (Swagger Docs /docs)    |
                           +-------------+-------------+
                                         |
                 +-----------------------+-----------------------+
                 |                                               |
                 v                                               v
    +-------------------------+                     +-------------------------+
    |     AI Search Engine    |                     |   Analytics & Auditing  |
    |-------------------------|                     |-------------------------|
    | - Pure CSP Backtracking |                     | - Soft Constraint Scorer|
    | - MRV & Degree Heuristic|                     | - Conflict Graph (Nx)   |
    | - Forward Checking/AC-3 |                     | - What-If Rescheduler   |
    | - Min-Conflicts Search  |                     | - Explainability Engine |
    | - Google OR-Tools CP-SAT|                     | - Fairness & Gini Audit |
    +------------+------------+                     +------------+------------+
                 |                                               |
                 +-----------------------+-----------------------+
                                         |
                                         v
                           +---------------------------+
                           |  Domain Data Models       |
                           |  (Entities, Batches, CSP) |
                           +---------------------------+
```

---

## 2. Component Descriptions

### `src/core/` (Pure Symbolic AI Engine)
- `csp.py`: Formal generic CSP container holding variables, domains, and unary/binary constraints.
- `heuristics.py`: Variable selection (MRV with Degree heuristic tie-breaker) and value ordering (LCV).
- `propagation.py`: Forward Checking and AC-3 constraint propagation engines that prune domains during search.
- `backtracking.py`: Recursive search with search state rollback and statistics tracking (nodes explored, backtracks, elapsed milliseconds).

### `src/solvers/` (Comparative Benchmarks)
- `min_conflicts.py`: Local search repair heuristic for CSPs.
- `ortools_solver.py`: SAT-based integer constraint solver via Google OR-Tools CP-SAT.
- `benchmark.py`: Unified comparative test harness evaluating algorithms across identical problem instances.

### `src/analytics/` (Explainability & Evaluation)
- `explainability.py`: Deconstructs scheduled sessions into verifiable hard constraint proofs and MRV search traces.
- `fairness.py`: Evaluates teaching workload variance, Gini coefficient, and student cohort morning/afternoon balance.
- `conflict_graph.py`: Constructs a NetworkX constraint clash graph with chromatic slot coloring.
- `rescheduler.py`: Emergency rescheduling simulator for faculty leave and room maintenance.

### `src/exporter/` (Distribution Engines)
- `excel_export.py`: OpenPyXL formatted multi-sheet workbooks.
- `pdf_export.py`: ReportLab landscape notice-board documents.
- `ical_export.py`: RFC 5545 `.ics` calendar generator.
