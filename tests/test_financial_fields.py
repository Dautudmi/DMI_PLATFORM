from dmi_core.dictionary.financial_fields import (
    DMI_FINANCIAL_FIELDS,
    CAFEF_NAME_TO_DMI_CODE,
)


def test_dictionary_loaded():
    assert len(DMI_FINANCIAL_FIELDS) > 0

    assert "total_assets" in DMI_FINANCIAL_FIELDS

    assert (
        CAFEF_NAME_TO_DMI_CODE["Tổng tài sản"]
        == "total_assets"
    )


if __name__ == "__main__":

    print("Total Fields:", len(DMI_FINANCIAL_FIELDS))

    print(CAFEF_NAME_TO_DMI_CODE)