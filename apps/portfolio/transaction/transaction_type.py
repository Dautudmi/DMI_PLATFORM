from enum import Enum


class TransactionType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"