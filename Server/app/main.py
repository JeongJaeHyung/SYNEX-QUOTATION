# SYNEX+QUOTATION/Server/app/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from service.router import router as service_router
from api.router import router as api_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")

templates = Jinja2Templates(directory="frontend")

@app.get("/")
async def root():
    return {"message": "SYNEX Quotation API"}








@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """로그인 페이지"""
    return templates.TemplateResponse(
        "template/login.html",
        {"request": request}
    )

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """회원가입 페이지"""
    return templates.TemplateResponse(
        "template/register.html",
        {"request": request}
    )









app.include_router(api_router, prefix="/api")
app.include_router(service_router, prefix="/service", tags=["service"])