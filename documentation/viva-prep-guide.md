# CSE276 Course Project: Viva Preparation Guide

**Project Topic:** Project 20 — Automated Timetable Generation using Constraint-Based Search  
**Group 18:** S V Pavan Kumar Kondamuri, Sawarkar Prathmesh Arun, Jeet Nag  

---

### Q1: What problem does your project solve?
**Answer:**  
Our project solves the university academic timetabling problem. Scheduling dozens of course lectures and lab practicals across classrooms and slots while avoiding teacher or cohort clashes is an **NP-hard combinatorial problem**. We model this as a **Constraint Satisfaction Problem (CSP)** to generate a conflict-free schedule in milliseconds.

---

### Q2: How is the problem formulated in terms of CSP?
**Answer:**  
A CSP is defined by a 3-tuple $(X, D, C)$:
- **Variables ($X$)**: Each individual session that must be scheduled (e.g., $CS101$ Theory for Batch A).
- **Domains ($D$)**: The permissible combinations of $(Day, Slot, Room)$ for each session.
- **Constraints ($C$)**:
  - **Hard Constraints**: No instructor double-booking, no classroom double-booking, no student batch double-booking, room capacity $\ge$ batch strength, and lab room type matching.
  - **Soft Constraints**: Minimizing faculty idle gaps between classes and satisfying teacher time-of-day preferences.

---

### Q3: What is the MRV heuristic, and why do you use it?
**Answer:**  
**MRV (Minimum Remaining Values)** is also known as the *"fail-first"* heuristic. At each step, the search selects the unassigned session that has the smallest number of valid slots remaining in its domain. If an assignment is going to fail, MRV triggers that failure as early as possible in the search tree, preventing unnecessary deep branching.

---

### Q4: What is Forward Checking (FC)?
**Answer:**  
Whenever a session is assigned a specific time slot and room, Forward Checking looks ahead at all remaining unassigned sessions that share the same teacher, room, or student batch, and immediately deletes any conflicting slot-room tuples from their domains. If any unassigned variable's domain becomes empty, the algorithm backtracks immediately.

---

### Q5: What algorithms did you benchmark, and what were the findings?
**Answer:**  
We evaluated three algorithms:
1. **Backtracking + MRV + Forward Checking**: Solves the problem with zero hard conflicts and minimal backtracks due to domain pruning.
2. **Min-Conflicts Local Search**: Rapidly repairs conflicts but can occasionally get stuck in local plateaus for tightly constrained problems.
3. **Google OR-Tools CP-SAT**: Provides an industrial baseline using SAT-based integer programming.

---

### Q6: How does your system address Explainability (Rubric Component 5)?
**Answer:**  
We built an interactive **Click-to-Explain Session Inspector**. Clicking any class on the timetable displays:
- The exact **zero-tolerance hard constraints verified** (teacher availability, room capacity, lab qualifications).
- The **algorithmic search trace** (how MRV prioritized the session and how Forward Checking pruned conflicting domains).
- The impact on soft preferences (preferred time slots).

---

### Q7: How does your system address Responsible AI & Fairness (Rubric Component 5)?
**Answer:**  
- **Workload Fairness**: We calculate the **Gini coefficient** of weekly teaching hours across faculty members to ensure equitable teaching load distribution.
- **Student Fatigue Balance**: We audit the distribution of morning versus late-afternoon classes across student cohorts.
- **Ethical Safeguards & Privacy**: The system is completely PII-free, operating solely on anonymized academic metadata (course codes, section IDs, room numbers).
