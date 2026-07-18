class PEV24Mapper:
    def get_first(self, row: dict, keys: list[str]):
        for key in keys:
            if key in row:
                return row[key]
        return None

    def to_float(self, value):
        if value is None:
            return None

        text = str(value).strip()

        if not text:
            return None

        try:
            return float(text.replace(",", ""))
        except ValueError:
            return None

    def to_symbol(self, value) -> str:
        if value is None:
            return ""

        return str(value).strip().upper()

    def to_text(self, value) -> str | None:
        if value is None:
            return None

        text = str(value).strip()

        return text if text else None