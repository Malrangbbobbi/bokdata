"""
기본 단위 테스트 — 네트워크 없이 구조만 검증.
실제 수집 테스트는 tests/test_integration.py 에서 진행.
"""
import importlib


def test_import():
    mod = importlib.import_module("bokdata")
    assert hasattr(mod, "MonetaryPolicy")


def test_instantiate():
    from bokdata import MonetaryPolicy
    mp = MonetaryPolicy()
    assert mp is not None


def test_doc_type_constants():
    from bokdata.monetary_policy.constants import MTG_SE
    assert set(MTG_SE.keys()) == {"statement", "conference", "minutes"}
