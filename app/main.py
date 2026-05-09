from fastapi import FastAPI

from routers import router

app = FastAPI(
    title="LibTrack API",
    version="1.0"
)

app.include_router(router)