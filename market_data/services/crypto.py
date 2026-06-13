import logging

from market_data.clients.binance import BinanceMarketDataClient
from market_data.dtos.ticker import Ticker
from market_data.utils import validate_symbol

logger = logging.getLogger(__name__)


class CryptoMarketDataService:

    def __init__(self, client: BinanceMarketDataClient | None = None):
        self._client = client or BinanceMarketDataClient()

    async def get_ticker(self, symbol: str) -> Ticker:
        validate_symbol(symbol)
        market_data = await self._client.get_ticker(symbol)
        return market_data
