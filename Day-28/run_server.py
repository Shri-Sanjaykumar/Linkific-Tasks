"""Server Runner for FinDoc-AuditEngine.

Executes Uvicorn server via Python interpreter to ensure compliance with
Windows Application Control security policies.
"""

import sys
import uvicorn

if __name__ == "__main__":
    port = 8000
    host = "127.0.0.1"
    print(f"=================================================================")
    print(f" FinDoc-AuditEngine Enterprise Server Starting")
    print(f" Host: http://{host}:{port}")
    print(f" Dashboard: http://{host}:{port}/dashboard")
    print(f" Swagger API Docs: http://{host}:{port}/docs")
    print(f" Dual Currency Standard: 1 USD = 86.50 INR")
    print(f"=================================================================")
    uvicorn.run("app.main:app", host=host, port=port, reload=False)
