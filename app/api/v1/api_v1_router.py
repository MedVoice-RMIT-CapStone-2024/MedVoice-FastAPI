from fastapi import APIRouter, Depends, HTTPException

from .endpoints.post import llm
from .endpoints.get import gcloud_storage
from .endpoints import nurse

api_router = APIRouter()

api_router.include_router(llm.router, prefix="/test/llm", tags=["test-llm"])
api_router.include_router(gcloud_storage.router, tags=["gcloud-storage"])
api_router.include_router(nurse.router, prefix="/nurses", tags=["nurses"])