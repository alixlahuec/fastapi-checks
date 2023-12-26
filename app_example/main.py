from fastapi import FastAPI

from app_example.routers import resources


app = FastAPI(
    title="Test App",
    description="A sample application for testing",
)

app.include_router(resources.router)
