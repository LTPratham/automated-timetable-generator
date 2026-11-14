"""One-Click Desktop Launcher for Automated Timetable Generation System.

Starts the FastAPI server with the token-driven web dashboard
and automatically opens your default web browser to http://localhost:8000.
"""

import sys
import time
import webbrowser
import threading
import uvicorn

def open_browser():
    """Waits for the server to start, then opens the browser."""
    time.sleep(1.2)
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    print("=" * 70)
    print("📅 Automated Academic Timetable Generation Platform (CSP)")
    print("AI Constraint Satisfaction Formulation • MRV/Degree • AC-3 • OR-Tools")
    print("=" * 70)
    print("\n👉 Web Dashboard: http://localhost:8000")
    print("👉 Interactive REST API Docs: http://localhost:8000/docs")
    print("\nOpening web dashboard in your browser...\n")

    # Launch browser in separate thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Run uvicorn server
    uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=False, log_level="info")
