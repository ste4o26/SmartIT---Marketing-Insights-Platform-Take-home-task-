import logging

import fastapi

from common.dtos.signal import Signal
from common.dtos.ticker import Ticker
from market_data.exceptions import (
    MarketDataFormatMismatchError,
    MarketDataProviderError,
)
from market_data.services.crypto import CryptoMarketDataService

logger = logging.getLogger(__name__)
router = fastapi.APIRouter(prefix="/crypto", tags=["crypto-market-data"])


@router.get("/prices/{symbol}", response_model=Ticker)
async def get_ticker(symbol: str):
    service = CryptoMarketDataService()

    try:
        return await service.get_ticker(symbol)
    except ValueError as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid symbol {symbol}",
        ) from e
    except MarketDataProviderError as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="Market data provider failure",
        ) from e
    except MarketDataFormatMismatchError as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="Incompatible provider data format",
        ) from e


@router.get("/signals/{symbol}", response_model=Signal)
async def get_signal(symbol: str):
    service = CryptoMarketDataService()

    try:
        return await service.get_signal(symbol)
    except ValueError as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid symbol {symbol}",
        ) from e
    except MarketDataProviderError as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="Market data provider failure",
        ) from e
    except MarketDataFormatMismatchError as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="Incompatible provider data format",
        ) from e
