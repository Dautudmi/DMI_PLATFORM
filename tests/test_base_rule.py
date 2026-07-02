from dmi_core.rules import BaseRule


def test_base_rule_exists():
    assert BaseRule is not None
    print("BaseRule OK")


if __name__ == "__main__":
    test_base_rule_exists()
    