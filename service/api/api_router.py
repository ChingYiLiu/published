from fastapi import APIRouter
from .routers.data1 import router as data1_router

router = APIRouter()
router.include_router(data1_router)