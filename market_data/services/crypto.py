import datetime
import decimal

from market_data.clients.binance import BinanceMarketDataClient
from market_data.constants import (
    FULL_CONFIDENCE_CHANGE_PERCENT,
    PERCENT_THRESHOLD,
    SignalPosition,
)
from market_data.dtos.signal import Signal
from market_data.dtos.ticker import Ticker
from market_data.utils import validate_symbol


class CryptoMarketDataService:

    def __init__(self, client: BinanceMarketDataClient | None = None):
        self._client = client or BinanceMarketDataClient()

    async def get_ticker(self, symbol: str) -> Ticker:
        validate_symbol(symbol)
        market_data = await self._client.get_ticker(symbol)
        return market_data

    async def get_signal(self, symbol: str) -> Signal:
        symbol = validate_symbol(symbol)
        ticker = await self._client.get_ticker(symbol)
        change_percent = ticker.price_change_percent
        signal = self._get_signal_type(change_percent)
        confidence = abs(change_percent) / FULL_CONFIDENCE_CHANGE_PERCENT
        confidence = float(min(confidence, decimal.Decimal(1)))
        return Signal.model_validate(
            {
                "symbol": ticker.symbol,
                "signal": signal,
                "confidence": confidence,
                "price": ticker.last_price,
                "price_change_percent_24h": ticker.price_change_percent,
                "source": "binance",
                "generated_at": datetime.datetime.now(datetime.UTC),
            }
        )

    def _get_signal_type(self, value: decimal.Decimal) -> SignalPosition:
        if abs(value) < PERCENT_THRESHOLD:
            return SignalPosition.NEUTRAL
        return SignalPosition.BULLISH if value > 0 else SignalPosition.BEARISH
