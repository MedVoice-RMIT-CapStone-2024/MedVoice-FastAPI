from fastapi import APIRouter, Depends, HTTPException

from .endpoints.post import llm
from .endpoints.get import gcloud_storage

api_router = APIRouter()

api_router.include_router(llm.router, prefix="/test/llm", tags=["test-llm"])
api_router.include_router(gcloud_storage.router, tags=["gcloud-storage"])