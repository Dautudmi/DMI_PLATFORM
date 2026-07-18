from infrastructure.pe_v24.strategy_repository import PEV24StrategyRepository


def test_pe_v24_strategy_repository_load_strategies(tmp_path):
    file_path = tmp_path / "strategy_master.csv"

    file_path.write_text(
        "symbol,strategy\n"
        "FPT,BUY_ATR_V2\n"
        "HPG,BUY_V1\n",
        encoding="utf-8-sig",
    )

    repo = PEV24StrategyRepository(csv_path=str(file_path))

    strategies = repo.load_strategies()

    assert len(strategies) == 2
    assert strategies[0].symbol == "FPT"
    assert strategies[0].strategy == "BUY_ATR_V2"


def test_pe_v24_strategy_repository_load_strategy_by_symbol(tmp_path):
    file_path = tmp_path / "strategy_master.csv"

    file_path.write_text(
        "symbol,strategy\n"
        "FPT,BUY_ATR_V2\n"
        "HPG,BUY_V1\n",
        encoding="utf-8-sig",
    )

    repo = PEV24StrategyRepository(csv_path=str(file_path))

    result = repo.load_strategy_by_symbol()

    assert result == {
        "FPT": "BUY_ATR_V2",
        "HPG": "BUY_V1",
    }