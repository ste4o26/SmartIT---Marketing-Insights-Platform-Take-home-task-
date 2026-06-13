from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signin")
async def signin(): ...
