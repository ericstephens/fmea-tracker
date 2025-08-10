from __future__ import annotations

from fastapi import FastAPI

from .routers import fmeas, failure_modes, actions, failure_causes, failure_effects, controls

app = FastAPI(
    title="FMEA Tracker API",
    description="API for managing Failure Mode and Effects Analysis (FMEA) data",
    version="1.0.0"
)

app.include_router(fmeas.router)
app.include_router(failure_modes.router)
app.include_router(actions.router)
app.include_router(failure_causes.router)
app.include_router(failure_effects.router)
app.include_router(controls.router)


@app.get("/")
def read_root():
    return {"message": "FMEA Tracker API", "version": "1.0.0"}