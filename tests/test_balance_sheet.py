from dmi_core.models.balance_sheet import BalanceSheet


def main():
    bs = BalanceSheet(
        symbol="AAA",
        year=2026,
        quarter=1,
        total_assets=1000,
    )

    print(bs)


if __name__ == "__main__":
    main()
    