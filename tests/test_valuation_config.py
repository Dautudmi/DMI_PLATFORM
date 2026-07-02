from dmi_core.valuation.valuation_config import ValuationConfig


def test_valuation_config():

    config = ValuationConfig()

    assert config.target_pe == 10.0
    assert config.target_pb == 1.5
    assert config.discount_rate == 0.12

    print(config)


if __name__ == "__main__":
    test_valuation_config()