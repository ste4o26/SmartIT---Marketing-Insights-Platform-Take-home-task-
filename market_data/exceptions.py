import fastapi


class MarketDataError(Exception):
    """Base exception for market-data failures."""

    def __init__(
        self,
        *args: object,
        status_code: int = fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        self.status_code = status_code
        super().__init__(*args)


class MarketDataProviderError(MarketDataError):
    """Raised when an market data provider cannot return usable payload."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args, fastapi.status.HTTP_502_BAD_GATEWAY)


class MarketDataFormatMismatchError(MarketDataError):
    """Raised when the market data provider returns an unexpected payload."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args, fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY)


class MarketDataSymbolNotFoundError(MarketDataError):
    """Raised when the upstream provider rejects or cannot find a symbol."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args, fastapi.status.HTTP_404_NOT_FOUND)
