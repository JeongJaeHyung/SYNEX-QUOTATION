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

@app.get("/test1", response_class=HTMLResponse)
async def test1(request: Request):
    # 샘플 데이터
    machines = [
        {
        "id": "000001",
        "maker_id": "J012",
        "category_id": 8,
        "name": "LCP-32FM 15A WA",
        "unit": "ea",
        "solo_price": 22000,
        },
        {
        "id": "000001",
        "maker_id": "J012",
        "category_id": 8,
        "name": "LCP-32FM 15A WA",
        "unit": "ea",
        "solo_price": 22000,
        },
        {
        "id": "000001",
        "maker_id": "J012",
        "category_id": 8,
        "name": "LCP-32FM 15A WA",
        "unit": "ea",
        "solo_price": 22000,
        },
    ]
    
    return templates.TemplateResponse("template/machine_quote_list_final.html", {
        "request": request,
        "current_page": "quotation_maintenance",
        "machines": machines
    })

app.include_router(api_router, prefix="/api")
app.include_router(service_router, prefix="/service", tags=["service"])