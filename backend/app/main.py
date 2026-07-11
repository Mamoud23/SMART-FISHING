from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import bateaux, alertes_sos, telemetrie, captures, pecheurs, auth

app = FastAPI(
    title="Smart Fishing API",
    description="Suivi des pêches artisanales et sécurité des pêcheurs",
    version="0.1.0",
)

# Permet au frontend (React, sur un autre port) d'appeler cette API depuis le
# navigateur. En développement, on autorise tout ; à restreindre en production
# à l'URL réelle du dashboard une fois déployé.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(bateaux.router)
app.include_router(alertes_sos.router)
app.include_router(telemetrie.router)
app.include_router(captures.router)
app.include_router(pecheurs.router)


@app.get("/health", tags=["Santé"])
async def health():
    """Endpoint de vérification rapide (utilisé par Docker healthcheck / monitoring)."""
    return {"status": "ok"}