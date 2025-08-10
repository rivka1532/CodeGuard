from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.routers import analysis

app = FastAPI()
app.include_router(analysis.router)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return {"message": "CodeGuard API is running"}
