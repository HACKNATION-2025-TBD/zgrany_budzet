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


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


# GET endpoint for all dzialy
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


# GET endpoint for all rozdzialy
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

# GET endpoint for all paragrafy
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

# GET endpoint for all grupy_wydatkow
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

# GET endpoint for all czesci_budzetowe
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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            message = {
                "cell": data.get("cell"),
                "user": data.get("user"),
                "value": data.get("value"),
                "timestamp": data.get("timestamp"),
                "type": data.get("type")
            }
            await manager.broadcast(message)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
