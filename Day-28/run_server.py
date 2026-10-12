"""Server Runner for FinDoc-AuditEngine.

Executes Uvicorn server via Python interpreter to ensure compliance with
Windows Application Control security policies.
"""

import os
import sys
import uvicorn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)

if __name__ == "__main__":
    port = 8000
    host = "127.0.0.1"
    print("=================================================================")
    print(" FinDoc-AuditEngine Enterprise Server Starting")
    print(f" Host: http://{host}:{port}")
    print(f" Workbench UI: http://{host}:{port}/dashboard")
    print(f" Swagger API Docs: http://{host}:{port}/docs")
    print(" Dual Currency Standard: 1 USD = 86.50 INR")
    print("=================================================================")
    uvicorn.run("app.main:app", host=host, port=port, reload=False)
