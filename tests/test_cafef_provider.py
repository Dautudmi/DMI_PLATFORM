from dmi_core.providers.cafef_provider import CafeFProvider

provider = CafeFProvider()

symbols = ["FPT", "HPG", "VCB"]

for symbol in symbols:
    print("=" * 60)
    print("SYMBOL:", symbol)

    bs = provider.get_balance_sheet(symbol, period="NAM", page_size=4)
    print("BSHEET:", bs.get("succeeded"))

    insta = provider.get_income_statement(symbol, period="NAM", page_size=4)
    print("INSTA:", insta.get("succeeded"))

print("=" * 60)
print("CafeFProvider OK")