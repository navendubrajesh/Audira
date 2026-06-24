"""API entrypoint for uvicorn."""

from app.main import create_app

app = create_app()
