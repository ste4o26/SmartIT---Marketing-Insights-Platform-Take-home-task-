from fastapi import APIRouter

router = APIRouter(prefix="/crypto", tags=["crypto-market-data"])


@router.get("/prices")
async def get_prices(): ...
