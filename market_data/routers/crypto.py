import logging

import fastapi

from common.constants import InternalService
from common.dtos.signal import Signal
from common.dtos.ticker import Ticker
from common.utils import get_service_subject
from market_data.exceptions import (
    MarketDataFormatMismatchError,
    MarketDataProviderError,
    MarketDataSymbolNotFoundError,
)
from market_data.services.crypto import CryptoMarketDataService

logger = logging.getLogger(__name__)
router = fastapi.APIRouter(
    prefix="/crypto",
    tags=["crypto-market-data"],
    dependencies=[
        fastapi.Depends(
            get_service_subject(
                audience=InternalService.MARKET_DATA,
                allowed_issuers=[InternalService.API],
            )
        )
    ],
)


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
    except MarketDataSymbolNotFoundError as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except (MarketDataProviderError, MarketDataFormatMismatchError) as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_502_BAD_GATEWAY, detail=str(e)
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
    except MarketDataSymbolNotFoundError as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except (MarketDataProviderError, MarketDataFormatMismatchError) as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_502_BAD_GATEWAY, detail=str(e)
        ) from e
