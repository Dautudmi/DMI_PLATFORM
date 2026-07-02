from dmi_core.providers.cafef_provider import CafeFProvider
from dmi_core.parsers.cafef_parser import CafeFParser

provider = CafeFProvider()

raw = provider.get_balance_sheet("FPT", period="NAM", page_size=4)

df = CafeFParser.parse_finance_report(raw)

print(df.head(20))
print()
print("Rows:", len(df))
print("Columns:", list(df.columns))

print()
print("CafeFParser OK")