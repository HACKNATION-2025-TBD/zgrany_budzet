from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json
import uvicorn
from fastapi import Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.dzialy import Dzial
from src.schemas.rozdzialy import Rozdzial
from src.schemas.paragrafy import Paragraf
from src.schemas.grupy_wydatkow import GrupaWydatkow
from src.schemas.czesci_budzetowe import CzescBudzetowa
from src.schemas.zrodla_finansowania import ZrodloFinansowania
from src.tabela import router as tabela_router


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tabela_router, prefix="/api", tags=["tabela"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


@app.get("/")
async def root():
    return {"status": "Server is running"}


@app.get("/dzialy")
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


@app.get("/rozdzialy")
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

@app.get("/paragrafy")
async def get_paragrafy(db: Session = Depends(get_db)):
    paragrafy = db.query(Paragraf).all()
    return [
        {
            "kod": p.kod,
            "tresc": p.tresc
        }
        for p in paragrafy
    ]

@app.get("/grupy_wydatkow")
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

@app.get("/czesci_budzetowe")
async def get_czesci_budzetowe(db: Session = Depends(get_db)):
    czesci = db.query(CzescBudzetowa).all()
    return [
        {
            "kod": c.kod,
            "nazwa": c.nazwa
        }
        for c in czesci
    ]

@app.get("/zrodla_finansowania")
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

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
