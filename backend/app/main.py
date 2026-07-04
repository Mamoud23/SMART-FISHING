from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="Smart Fishing API",
    description="Backend pour le suivi des pêches artisanales et la sécurité des pêcheurs",
    version="1.0.0"
)

# CORS - Important pour que React puisse appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Change en production par ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route de bienvenue
@app.get("/")
async def root():
    return {
        "message": "🚀 Smart Fishing Backend est opérationnel !",
        "team": "DEMBELE - Backend & Bases de Données",
        "status": "OK"
    }

# Route de santé
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "pending connection",
        "cache": "pending connection"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)