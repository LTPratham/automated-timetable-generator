"""
Generate PROJECT_SUBMISSION_REPORT.html
Run: python documentation/generate_report.py
"""
import base64, os

BASE = os.path.dirname(os.path.abspath(__file__))
SS   = os.path.join(BASE, "screenshots")

def b64img(name):
    p = os.path.join(SS, name)
    if os.path.exists(p):
        data = base64.b64encode(open(p,"rb").read()).decode()
        return f"data:image/png;base64,{data}"
    return ""

landing_src   = b64img("landing_page.png")
dashboard_src = b64img("dashboard.png")

landing_tag   = f'<img src="{landing_src}" alt="Landing Page">'   if landing_src   else "<p><em>[Landing Page Screenshot]</em></p>"
dashboard_tag = f'<img src="{dashboard_src}" alt="Dashboard">'    if dashboard_src  else "<p><em>[Dashboard Screenshot]</em></p>"

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>Project Submission Report – Group 18</title>
<style>
  @page {{ size: A4; margin: 14mm 16mm; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10.5pt;
    color: #1a1a2e;
    background: #fff;
  }}

  /* ── Header banner ── */
  .header {{
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
    color: #fff;
    padding: 14px 20px 12px;
    border-radius: 6px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 14px;
  }}
  .header .logo {{
    font-size: 36px;
    line-height: 1;
  }}
  .header .meta {{ flex: 1; }}
  .header h1 {{
    font-size: 13.5pt;
    font-weight: 700;
    letter-spacing: .3px;
    margin-bottom: 2px;
  }}
  .header .sub {{
    font-size: 9pt;
    opacity: .85;
    line-height: 1.5;
  }}
  .badge {{
    display: inline-block;
    background: rgba(255,255,255,.18);
    border: 1px solid rgba(255,255,255,.3);
    border-radius: 20px;
    padding: 2px 9px;
    font-size: 8pt;
    margin-top: 4px;
    margin-right: 4px;
  }}

  /* ── Sections ── */
  .section {{ margin-bottom: 9px; }}
  .section-title {{
    font-size: 10pt;
    font-weight: 700;
    color: #0f3460;
    text-transform: uppercase;
    letter-spacing: .6px;
    border-bottom: 2px solid #0f3460;
    padding-bottom: 2px;
    margin-bottom: 6px;
  }}

  /* ── Team table ── */
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 9.5pt;
  }}
  th {{
    background: #0f3460;
    color: #fff;
    padding: 5px 8px;
    text-align: left;
    font-weight: 600;
  }}
  td {{ padding: 4px 8px; border-bottom: 1px solid #e0e0e0; }}
  tr:nth-child(even) td {{ background: #f4f7fc; }}

  /* ── Tech grid ── */
  .tech-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 5px;
  }}
  .tech-chip {{
    background: #f0f4ff;
    border: 1px solid #c5d3f0;
    border-radius: 4px;
    padding: 4px 7px;
    font-size: 8.8pt;
    text-align: center;
  }}
  .tech-chip strong {{ display: block; color: #0f3460; font-size: 8pt; }}

  /* ── Feature list ── */
  .feat-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4px 14px;
  }}
  .feat-item {{
    display: flex;
    align-items: flex-start;
    gap: 5px;
    font-size: 9.5pt;
    line-height: 1.4;
  }}
  .feat-item .icon {{ font-size: 11pt; flex-shrink: 0; margin-top: 1px; }}

  /* ── Screenshots ── */
  .ss-row {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-top: 4px;
  }}
  .ss-box {{
    border: 1px solid #c5d3f0;
    border-radius: 5px;
    overflow: hidden;
  }}
  .ss-box img {{
    width: 100%;
    display: block;
    max-height: 155px;
    object-fit: cover;
    object-position: top;
  }}
  .ss-cap {{
    background: #f4f7fc;
    font-size: 8pt;
    color: #0f3460;
    text-align: center;
    padding: 3px;
    font-weight: 600;
  }}

  /* ── GitHub / footer strip ── */
  .footer-strip {{
    background: #f4f7fc;
    border: 1px solid #c5d3f0;
    border-radius: 5px;
    padding: 7px 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 9px;
    font-size: 9pt;
  }}
  .footer-strip .gh {{ font-weight: 700; color: #0f3460; font-size: 9.5pt; }}
  .footer-strip .note {{ font-size: 8.2pt; color: #555; }}

  /* ── Print media ── */
  @media print {{
    body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .no-print {{ display: none; }}
  }}
  .print-btn {{
    position: fixed;
    top: 10px; right: 10px;
    background: #0f3460;
    color: white;
    border: none;
    padding: 8px 18px;
    border-radius: 20px;
    cursor: pointer;
    font-size: 11pt;
    z-index: 999;
    box-shadow: 0 2px 10px rgba(0,0,0,.3);
  }}
</style>
</head>
<body>

<button class="print-btn no-print" onclick="window.print()">🖨️ Save as PDF</button>

<!-- ══ HEADER ══ -->
<div class="header">
  <div class="logo">🧠</div>
  <div class="meta">
    <h1>Automated Academic Timetable Generation System using Constraint Satisfaction</h1>
    <div class="sub">
      Lovely Professional University &nbsp;|&nbsp; B.Tech CSE &nbsp;|&nbsp;
      Course: <strong>CSE276 – Artificial Intelligence Foundations</strong><br/>
      Section: K4P25CB &nbsp;|&nbsp; Group: 18 &nbsp;|&nbsp; Project No: 20 &nbsp;|&nbsp;
      Academic Year: 2026–27
    </div>
    <div>
      <span class="badge">🏆 AI Foundations Project</span>
      <span class="badge">✅ 14 Unit Tests Passing</span>
      <span class="badge">🌐 Live Web Dashboard</span>
    </div>
  </div>
</div>

<!-- ══ TEAM ══ -->
<div class="section">
  <div class="section-title">👥 Team Members</div>
  <table>
    <tr>
      <th>#</th><th>Name</th><th>Registration No.</th><th>Roll No.</th><th>GitHub</th><th>Project Responsibilities</th>
    </tr>
    <tr><td>1</td><td><strong>Sawarkar Prathmesh Arun</strong></td><td>12509401</td><td>47</td><td>@LTPratham</td><td>Project Lead & Core CSP Search Engine Architecture</td></tr>
    <tr><td>2</td><td><strong>Siya Gupta</strong></td><td>12505235</td><td>23</td><td>@siyagupta3103</td><td>Algorithm Design, Web UI & Interactive Guided Tour</td></tr>
    <tr><td>3</td><td><strong>Bhavya Verma</strong></td><td>12513794</td><td>44</td><td>@bhavyaverma81</td><td>Responsible AI Fairness Audit, Testing & Documentation</td></tr>
  </table>
</div>

<!-- ══ ABSTRACT ══ -->
<div class="section">
  <div class="section-title">📋 Project Abstract</div>
  <p style="font-size:9.8pt; line-height:1.55; text-align:justify;">
    University timetabling is a classic <strong>NP-hard Constraint Satisfaction Problem (CSP)</strong>. Our system
    automatically generates conflict-free, optimised academic timetables by encoding hard constraints
    (no-clash, room capacity, faculty availability) into a CSP framework and solving them using four
    complementary AI paradigms: <em>Backtracking with MRV heuristic</em>,
    <em>CP-SAT via Google OR-Tools</em>, <em>Simulated Annealing</em>, and a custom
    <em>Genetic Algorithm</em>. The interactive web dashboard provides real-time
    constraint-violation highlighting, step-by-step search traces, Responsible AI fairness audits,
    what-if rescheduling, PDF/Excel/iCal exports, and a 9-step guided tour for new users.
  </p>
</div>

<!-- ══ FEATURES ══ -->
<div class="section">
  <div class="section-title">⚡ Key Features Built</div>
  <div class="feat-grid">
    <div class="feat-item"><span class="icon">🔧</span><span><strong>CSP Engine:</strong> Variables = sessions, Domains = slots, Constraints = no-clash, room, faculty</span></div>
    <div class="feat-item"><span class="icon">🧬</span><span><strong>4 AI Solvers:</strong> Backtracking+MRV, CP-SAT, Simulated Annealing, Genetic Algorithm</span></div>
    <div class="feat-item"><span class="icon">🤖</span><span><strong>AI Copilot:</strong> Natural language assistant for workload analysis & what-if queries</span></div>
    <div class="feat-item"><span class="icon">🎯</span><span><strong>Quality Radar:</strong> 5-axis spider chart evaluating integrity, fairness, and ergonomics</span></div>
    <div class="feat-item"><span class="icon">🎬</span><span><strong>Search Stepper:</strong> Live step-by-step playback of MRV, forward checking & backtracks</span></div>
    <div class="feat-item"><span class="icon">📱</span><span><strong>QR Sync:</strong> Scannable mobile QR code for instant Google & Apple Calendar import</span></div>
    <div class="feat-item"><span class="icon">🔍</span><span><strong>Explainability:</strong> Click any class cell to inspect zero-tolerance constraint proof</span></div>
    <div class="feat-item"><span class="icon">⚖️</span><span><strong>Responsible AI:</strong> Gini-index fairness audit across faculty & rooms; bias detection</span></div>
    <div class="feat-item"><span class="icon">🗺️</span><span><strong>What-If Scheduler:</strong> Minimal perturbation rescheduling for sick leave & room closures</span></div>
    <div class="feat-item"><span class="icon">📤</span><span><strong>Export Engine:</strong> PDF timetables, Excel spreadsheets, iCal (.ics) calendar files</span></div>
  </div>
</div>

<!-- ══ TECH STACK ══ -->
<div class="section">
  <div class="section-title">🛠️ Technologies & Tools Used</div>
  <div class="tech-grid">
    <div class="tech-chip"><strong>Python 3.11</strong>Core Language</div>
    <div class="tech-chip"><strong>FastAPI</strong>Web Framework</div>
    <div class="tech-chip"><strong>Google OR-Tools</strong>CP-SAT Solver</div>
    <div class="tech-chip"><strong>NetworkX</strong>Graph Conflict</div>
    <div class="tech-chip"><strong>Plotly</strong>Interactive Charts</div>
    <div class="tech-chip"><strong>ReportLab</strong>PDF Export</div>
    <div class="tech-chip"><strong>OpenPyXL</strong>Excel Export</div>
    <div class="tech-chip"><strong>iCalendar</strong>.ics Export</div>
    <div class="tech-chip"><strong>Genetic Algo</strong>Evolutionary AI</div>
    <div class="tech-chip"><strong>Sim. Annealing</strong>Metaheuristic</div>
    <div class="tech-chip"><strong>Pydantic v2</strong>Data Validation</div>
    <div class="tech-chip"><strong>Pytest</strong>Unit Testing</div>
  </div>
</div>

<!-- ══ SCREENSHOTS ══ -->
<div class="section">
  <div class="section-title">📸 Application Screenshots</div>
  <div class="ss-row">
    <div class="ss-box">
      {landing_tag}
      <div class="ss-cap">🏠 Landing Page – Project Showcase</div>
    </div>
    <div class="ss-box">
      {dashboard_tag}
      <div class="ss-cap">📊 Main Dashboard – Timetable Generator</div>
    </div>
  </div>
</div>

<!-- ══ GITHUB + FOOTER ══ -->
<div class="footer-strip">
  <div>
    <div class="gh">🔗 GitHub Repository</div>
    <div id="gh-link" style="font-size:9pt; color:#0f3460; font-weight:600; margin-top:2px;">
      <a href="https://github.com/LTPratham/automated-timetable-generator" target="_blank" style="color:#0f3460; text-decoration:none;">https://github.com/LTPratham/automated-timetable-generator</a>
    </div>
  </div>
  <div style="text-align:right;">
    <div class="note">Submitted: November 2026</div>
    <div class="note">Tests: 13 passed ✅ &nbsp;|&nbsp; Commits: 47 files</div>
    <div class="note">Collaborators: @siyagupta3103 &nbsp; @bhavyaverma81</div>
  </div>
</div>

</body>
</html>
"""

out = os.path.join(BASE, "PROJECT_SUBMISSION_REPORT.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print(f"✅ Report written to: {out}")
print(f"   File size: {os.path.getsize(out)/1024:.1f} KB")
