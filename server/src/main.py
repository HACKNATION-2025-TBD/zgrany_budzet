from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from contextlib import asynccontextmanager
import json
import uvicorn
from fastapi import Depends
from sqlalchemy.orm import Session

from src.database import get_db, init_db
from src.schemas.dzialy import Dzial
from src.schemas.rozdzialy import Rozdzial
from src.schemas.paragrafy import Paragraf
from src.schemas.grupy_wydatkow import GrupaWydatkow
from src.schemas.czesci_budzetowe import CzescBudzetowa
from src.schemas.zrodla_finansowania import ZrodloFinansowania
from src.tabela import router as tabela_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


api_router = APIRouter(prefix="/api")
app.include_router(tabela_router, prefix="/api", tags=["tabela"])


@app.get("/")
async def root():
    return {"status": "Server is running"}


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint that verifies database connection"""
    try:
        # Simple query to check DB connection
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


@api_router.get("/dzialy")
async def get_dzialy(db: Session = Depends(get_db)):
    dzialy = db.query(Dzial).all()
    return [
        {
            "kod": d.kod,
            "nazwa": d.nazwa,
            "PKD": d.PKD
        }
        for d in dzialy
    ]


@api_router.get("/rozdzialy")
async def get_rozdzialy(db: Session = Depends(get_db)):
    rozdzialy = db.query(Rozdzial).all()
    return [
        {
            "kod": r.kod,
            "nazwa": r.nazwa,
            "dzial": r.dzial
        }
        for r in rozdzialy
    ]

@api_router.get("/paragrafy")
async def get_paragrafy(db: Session = Depends(get_db)):
    paragrafy = db.query(Paragraf).all()
    return [
        {
            "kod": p.kod,
            "tresc": p.tresc
        }
        for p in paragrafy
    ]

@api_router.get("/grupy_wydatkow")
async def get_grupy_wydatkow(db: Session = Depends(get_db)):
    grupy = db.query(GrupaWydatkow).all()
    return [
        {
            "id": g.id,
            "nazwa": g.nazwa,
            "paragrafy": g.paragrafy
        }
        for g in grupy
    ]

@api_router.get("/czesci_budzetowe")
async def get_czesci_budzetowe(db: Session = Depends(get_db)):
    czesci = db.query(CzescBudzetowa).all()
    return [
        {
            "kod": c.kod,
            "nazwa": c.nazwa
        }
        for c in czesci
    ]

@api_router.get("/zrodla_finansowania")
async def get_zrodla_finansowania(db: Session = Depends(get_db)):
    zrodla = db.query(ZrodloFinansowania).all()
    return [
        {
            "kod": z.kod,
            "nazwa": z.nazwa,
            "opis": z.opis
        }
        for z in zrodla
    ]

# Include the API router
app.include_router(api_router)

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
