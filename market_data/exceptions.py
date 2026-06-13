class MarketDataError(Exception):
    """Base exception for market-data failures."""


class MarketDataProviderError(MarketDataError):
    """Raised when an upstream provider cannot return usable market data."""


class MarketDataFormatMismatchError(MarketDataError):
    """Raised when the upstream provider rejects or cannot find a symbol."""
