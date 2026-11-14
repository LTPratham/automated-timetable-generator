# Implementation Plan: Explainability Inspector & Responsible AI Audit

**Date:** 2026-11-14  
**Project:** Automated Timetable Generation System using Constraint-Based Search (CSE276 - Project 20, Group 18)  
**Authors:** S V Pavan Kumar Kondamuri, Sawarkar Prathmesh Arun, Jeet Nag  

---

## 1. Objective
Fulfill mandatory Rubric Component 5 (*Explainability & Responsible AI*) from the CSE276 Course Project Evaluation Scheme:
1. Explain **why** the AI produced each specific course allocation (constraint proof and heuristic search trace).
2. Measure and report **algorithmic fairness & workload equity** across teaching faculty using standard inequality metrics (Gini coefficient).
3. Evaluate **student cohort cognitive spacing** (morning vs afternoon balance).
4. Formalize ethical safeguards, privacy guarantees (PII-free), and documented failure modes.

---

## 2. Modules Created & Extended
- `src/analytics/explainability.py`: `generate_session_explanation()` extracting zero-tolerance hard constraint verifications, soft preference impacts, and MRV/Forward Checking pruning logs for any scheduled session.
- `src/analytics/fairness.py`: `audit_fairness_and_ethics()` and `calculate_gini()` computing faculty teaching hour equity, utilization rates, and student fatigue balance.
- `src/api.py`: Exposed `/api/explain/{variable_id}` and `/api/fairness` endpoints.
- `src/app/app.py`: Integrated "⚖️ Responsible AI & Fairness Audit" navigation tab and granular session inspector.
- `frontend/index.html`: Added Interactive Session Inspector Modal on class click, fairness KPI metrics, and Plotly equity charts.
- `tests/test_explainability_fairness.py`: Automated unit tests for Gini calculation and explainability payload verification.

---

## 3. Verification & Acceptance
- All 12 unit tests passed in 3.8s.
- FastAPI backend running at `http://127.0.0.1:8000`.
- Swagger docs verified at `/docs`.
