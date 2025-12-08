# SYNEX+QUOTATION/Server/app/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from service.router import router as service_router
from api.router import router as api_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")

templates = Jinja2Templates(directory="frontend")

@app.get("/")
async def root():
    return {"message": "SYNEX Quotation API"}

app.include_router(api_router, prefix="/api")
app.include_router(service_router, prefix="/service", tags=["service"])