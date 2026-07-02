from dmi_core.models.engine_result import EngineResult

result = EngineResult(
    engine="Valuation",
    ticker="FPT",
    score=18,
    max_score=20,
    confidence=91,
    signals=["MOS > 30%", "Upside > 25%"],
    risks=["PB hơi cao"],
    metadata={"date": "2026-06-27"}
)

print(result)
print(result.normalized_score())
print(result.to_dict())

print("EngineResult OK")
