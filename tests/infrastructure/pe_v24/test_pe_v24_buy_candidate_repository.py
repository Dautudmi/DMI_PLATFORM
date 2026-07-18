from infrastructure.pe_v24.buy_candidate_repository import (
    PEV24BuyCandidateRepository,
)


def test_pe_v24_buy_candidate_repository_load_candidates(tmp_path):
    file_path = tmp_path / "buy_candidates.csv"

    file_path.write_text(
        "symbol,strategy,score\n"
        "FPT,BUY_V1,85\n"
        "HPG,BUY_V2,90\n",
        encoding="utf-8-sig",
    )

    repo = PEV24BuyCandidateRepository(csv_path=str(file_path))

    candidates = repo.load_candidates()

    assert len(candidates) == 2
    assert candidates[0].symbol == "FPT"
    assert candidates[0].strategy == "BUY_V1"
    assert candidates[0].score == 85


def test_pe_v24_buy_candidate_repository_load_symbols(tmp_path):
    file_path = tmp_path / "buy_candidates.csv"

    file_path.write_text(
        "symbol,strategy,score\n"
        "FPT,BUY_V1,85\n"
        "FPT,BUY_V2,90\n"
        "HPG,BUY_V1,80\n",
        encoding="utf-8-sig",
    )

    repo = PEV24BuyCandidateRepository(csv_path=str(file_path))

    assert repo.load_symbols() == ["FPT", "HPG"]