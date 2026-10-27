from fastapi import APIRouter
from api.v1.endpoints import accounts, transfers

api_router = APIRouter()
api_router.include_router(accounts.router)
api_router.include_router(transfers.router)
