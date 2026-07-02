import pandas as pd

from dmi_core.core.exporter import (
    save_excel,
    save_csv,
    save_text
)

df = pd.DataFrame({
    "Ticker": ["FPT", "HPG", "GVR"],
    "Price": [100, 30, 35]
})

save_excel(df, "tests/output.xlsx")

save_csv(df, "tests/output.csv")

save_text("Hello DMI Framework", "tests/output.txt")

print("Exporter OK")