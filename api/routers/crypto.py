import fastapi

from common.dtos.signal import Signal
from common.dtos.ticker import Ticker
from api.exceptions import UpstreamResourceNotFoundError, UpstreamServiceError
from api.services.market_data import MarketDataService
from api.utils import get_current_user_id

router = fastapi.APIRouter(prefix="/crypto", tags=["crypto-market-data"])


@router.get("/prices/{symbol}", response_model=Ticker)
async def get_ticker(symbol: str, subject: int = fastapi.Depends(get_current_user_id)):
    service = MarketDataService()

    try:
        return await service.get_ticker(symbol)
    except UpstreamResourceNotFoundError as error:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="Crypto symbol was not found",
        ) from error
    except UpstreamServiceError as error:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="Invalid data format",
        ) from error


@router.get("/signal/{symbol}", response_model=Signal)
async def get_signal(symbol: str, subject: int = fastapi.Depends(get_current_user_id)):
    service = MarketDataService()

    try:
        return await service.get_signal(symbol)
    except UpstreamResourceNotFoundError as error:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="Crypto symbol was not found",
        ) from error
    except UpstreamServiceError as error:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="Invalid data format",
        ) from error
