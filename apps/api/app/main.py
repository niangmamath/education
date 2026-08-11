from fastapi import FastAPI

app = FastAPI(
    title="StudentConnect API",
    version="0.1.0",
)


@app.get("/health/live", tags=["Health"])
async def health_live() -> dict[str, str]:
    return {"status": "alive"}


@app.get("/health/ready", tags=["Health"])
async def health_ready() -> dict[str, str]:
    return {"status": "ready"}