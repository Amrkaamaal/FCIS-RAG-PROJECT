from fastapi import APIRouter

from routes.base import router as base_router
from routes.data import router as data_router
from routes.nlp import router as nlp_router

router = APIRouter()

router.include_router(base_router)

router.include_router(data_router)

router.include_router(nlp_router)

__all__ = ["router"]
