from api.clients.market_data import MarketDataClient
from common.dtos.signal import Signal
from common.dtos.ticker import Ticker


class MarketDataService:

    def __init__(self, client: MarketDataClient | None = None):
        self._client = client or MarketDataClient()

    async def get_ticker(self, symbol: str) -> Ticker:
        return await self._client.get_ticker(symbol)

    async def get_signal(self, symbol: str) -> Signal:
        return await self._client.get_signal(symbol)
