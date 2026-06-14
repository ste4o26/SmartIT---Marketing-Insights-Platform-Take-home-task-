import fastapi

from api.services.market_data import MarketDataService
from api.utils import get_user_subject
from common.dtos.signal import Signal
from common.dtos.ticker import Ticker

router = fastapi.APIRouter(
    prefix="/crypto",
    tags=["crypto-market-data"],
    dependencies=[fastapi.Depends(get_user_subject)],
)


@router.get("/prices/{symbol}", response_model=Ticker)
async def get_ticker(symbol: str) -> Ticker:
    service = MarketDataService()
    return await service.get_ticker(symbol)


@router.get("/signal/{symbol}", response_model=Signal)
async def get_signal(symbol: str) -> Signal:
    service = MarketDataService()
    return await service.get_signal(symbol)
