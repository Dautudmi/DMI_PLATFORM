from dmi_core.valuation import BaseValuation


def test_base_valuation_exists():
    assert BaseValuation is not None
    print("BaseValuation OK")


if __name__ == "__main__":
    test_base_valuation_exists()