from dmi_core.providers.cafef_provider import CafeFProvider
from dmi_core.parsers.cafef_parser import CafeFParser
from dmi_core.mappers.cafef_mapper import CafeFMapper

provider = CafeFProvider()

raw_bsheet = provider.get_balance_sheet("FPT", period="NAM", page_size=4)
df_bsheet = CafeFParser.parse_finance_report(raw_bsheet)
print(df_bsheet.columns)
print(df_bsheet.head())
normalized_bsheet = CafeFMapper.normalize_finance_df(df_bsheet)
wide_bsheet = CafeFMapper.to_wide_format(normalized_bsheet)

print("===== NORMALIZED BSHEET =====")
print(normalized_bsheet.head(20))

print()
print("===== WIDE BSHEET =====")
print(wide_bsheet.head())

raw_insta = provider.get_income_statement("FPT", period="NAM", page_size=4)
df_insta = CafeFParser.parse_finance_report(raw_insta)

normalized_insta = CafeFMapper.normalize_finance_df(df_insta)
wide_insta = CafeFMapper.to_wide_format(normalized_insta)

print()
print("===== NORMALIZED INSTA =====")
print(normalized_insta.head(20))

print()
print("===== WIDE INSTA =====")
print(wide_insta.head())

print()
print("CafeFMapper OK")