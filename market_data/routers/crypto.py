import logging

import fastapi

from common.constants import InternalService
from common.dtos.signal import Signal
from common.dtos.ticker import Ticker
from common.utils import get_service_subject
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
    return await service.get_ticker(symbol)


@router.get("/signals/{symbol}", response_model=Signal)
async def get_signal(symbol: str):
    service = CryptoMarketDataService()
    return await service.get_signal(symbol)
