from fastapi import FastAPI
from starlette.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import settings
from app.presentation.api import router

app = FastAPI(
    title=settings.app_name,
    description="OCR_fast",
    version=settings.app_version,
    debug=settings.debug
)

app.include_router(router)

@app.exception_handler(Exception)
async def universal_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": str(exc)}
    )


@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": f"{settings.app_name} is running",
        "version": settings.app_version
    }
'''
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
'''