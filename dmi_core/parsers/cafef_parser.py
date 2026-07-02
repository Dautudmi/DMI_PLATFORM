import pandas as pd


class CafeFParser:
    @staticmethod
    def parse_finance_report(raw_json):
        value = raw_json.get("data", {}).get("value", {})

        symbol = value.get("symbol")
        report_title = value.get("title")
        report_type = value.get("typeName")
        type_time = value.get("typeTime")

        items = value.get("data", [])

        rows = []

        for item in items:
            unit = item.get("unit")
            order_number = item.get("orderNumber")
            code = item.get("code")
            name = item.get("name")
            values = item.get("data", [])

            for v in values:
                rows.append({
                    "symbol": symbol,
                    "report_title": report_title,
                    "report_type": report_type,
                    "type_time": type_time,
                    "unit": unit,
                    "order_number": order_number,
                    "code": code,
                    "name": name,
                    "text_time": v.get("textTime"),
                    "report_type_text": v.get("reportTypeText"),
                    "report_type_code": v.get("reportType"),
                    "year": v.get("year"),
                    "quarter": v.get("quarter"),
                    "value": v.get("value"),
                })

        return pd.DataFrame(rows)