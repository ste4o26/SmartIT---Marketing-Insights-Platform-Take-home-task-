import re

SERVICE_URI_PREFIX = "market-data"
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{3,20}$")
