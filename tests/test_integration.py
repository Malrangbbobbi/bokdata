"""
통합 테스트 — 실제 한국은행 웹사이트에 요청.
CI 에서는 스킵, 로컬에서만 실행:
    pytest tests/test_integration.py -v
"""
import pytest

pytest.importorskip("requests")
pytest.importorskip("bs4")

pytestmark = pytest.mark.network


@pytest.mark.network
def test_get_list_single_year():
    from bokdata import MonetaryPolicy

    mp = MonetaryPolicy()
    df = mp.get_list(start=2024, end=2024, doc_type="minutes")
    assert not df.empty, "2024년 의사록 목록이 비어 있음"
    assert "download_url" in df.columns


@pytest.mark.network
def test_get_list_returns_dataframe():
    from bokdata import MonetaryPolicy
    import pandas as pd

    mp = MonetaryPolicy()
    df = mp.get_list(start=2023, end=2023)
    assert isinstance(df, pd.DataFrame)
