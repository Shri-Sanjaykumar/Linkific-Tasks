"""FastAPI Server Runner for FinDoc-AuditEngine.

Bypasses Windows Application Control restrictions on uvicorn.exe
by running uvicorn directly in Python runtime.
"""

import uvicorn

if __name__ == "__main__":
    print("=" * 70)
    print(" Starting FinDoc-AuditEngine REST Microservice...")
    print(" Swagger UI : http://127.0.0.1:8000/docs")
    print(" Health Live: http://127.0.0.1:8000/health/live")
    print(" Press Ctrl + C to stop the server.")
    print("=" * 70)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
