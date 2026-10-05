"""
Linkific Enterprise AI Service - Local Service Runner
Starts the Uvicorn ASGI server with parameters loaded from .env.
"""

import sys
import uvicorn
from app.core.config import get_settings


def main():
    settings = get_settings()
    print("=" * 80)
    print(f"  {settings.APP_NAME} - v{settings.APP_VERSION}")
    print("=" * 80)
    print(f"  Environment:  {settings.ENVIRONMENT}")
    print(f"  Host:         {settings.HOST}")
    print(f"  Port:         {settings.PORT}")
    print(f"  Log Level:    {settings.LOG_LEVEL}")
    print(f"  Log Format:   {settings.LOG_FORMAT}")
    print(f"  Swagger Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"  Health Check: http://{settings.HOST}:{settings.PORT}/health/ready")
    print(f"  Metrics:      http://{settings.HOST}:{settings.PORT}/metrics")
    print("=" * 80)

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.DEBUG
    )


if __name__ == "__main__":
    main()
