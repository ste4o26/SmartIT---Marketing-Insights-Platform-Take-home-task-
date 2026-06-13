from market_data.constants import SYMBOL_PATTERN


def validate_symbol(value: str) -> str:
    symbol = value.strip().upper()
    if not SYMBOL_PATTERN.fullmatch(symbol):
        raise ValueError("Symbol must contain 3-20 uppercase letters or numbers")
    return symbol
