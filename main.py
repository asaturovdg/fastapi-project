from fastapi import FastAPI
from fastapi.responses import Response

from app.api.v1.wallets import router as wallets_router
from app.api.v1.operations import router as operations_router

app = FastAPI()

app.include_router(wallets_router, prefix="/api/v1", tags=["wallet"])
app.include_router(operations_router, prefix="/api/v1", tags=["operations"])

@app.get("/health")
def health_check():
    return Response(content="OK", media_type="text/plain")