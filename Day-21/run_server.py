"""
Day 21 — Local Uvicorn Server Runner
Provides CLI startup entrypoint with configurable port and host.
"""

import sys
import os
import argparse
import uvicorn

# Ensure Day-21 root is on sys.path
DAY21_DIR = os.path.dirname(os.path.abspath(__file__))
if DAY21_DIR not in sys.path:
    sys.path.insert(0, DAY21_DIR)


def main():
    parser = argparse.ArgumentParser(description="Run Linkific Enterprise AI Service (Day 21)")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable live auto-reload for development")

    args = parser.parse_args()

    print("=" * 70)
    print(f"Starting Linkific Enterprise AI Service (Day 21)")
    print(f"Listening on: http://{args.host}:{args.port}")
    print(f"Swagger Docs: http://{args.host}:{args.port}/docs")
    print(f"Redoc:        http://{args.host}:{args.port}/redoc")
    print("=" * 70)

    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
