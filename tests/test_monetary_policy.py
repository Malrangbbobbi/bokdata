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


def test_parse_date():
    from bokdata.monetary_policy.fetcher import _parse_date
    assert _parse_date("01월 14일(금)") == "01-14"
    assert _parse_date("12월  3일(화)") == "12-03"
    assert _parse_date("2월 5일") == "02-05"
    # 파싱 불가 시 원문 반환
    assert _parse_date("unknown") == "unknown"


def test_parse_list_html_doctype():
    """thead 컬럼 헤더 기준으로 doc_type이 올바르게 분류되는지 검증."""
    from bokdata.monetary_policy.fetcher import _parse_list_html

    html = """
    <table>
      <thead>
        <tr>
          <th>날짜</th>
          <th>결정문</th>
          <th>기자간담회</th>
          <th>의사록</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th scope="row">01월 14일(금)</th>
          <td>
            <div class="fileGoupBox"><ul><li>
              <a href="?atchFileId=AAA&fileSn=0" title="결정문.pdf">결정문.pdf</a>
            </li></ul></div>
          </td>
          <td>
            <div class="fileGoupBox"><ul><li>
              <a href="?atchFileId=BBB&fileSn=0" title="기자간담회.pdf">기자간담회.pdf</a>
            </li></ul></div>
          </td>
          <td>
            <div class="fileGoupBox"><ul><li>
              <a href="?atchFileId=CCC&fileSn=0" title="의사록.pdf">의사록.pdf</a>
            </li></ul></div>
          </td>
        </tr>
      </tbody>
    </table>
    """

    rows = _parse_list_html(html, doc_type="all")
    doc_types = {r["doc_type"] for r in rows}
    assert doc_types == {"statement", "conference", "minutes"}

    dates = {r["date"] for r in rows}
    assert dates == {"01-14"}


def test_parse_list_html_doctype_filter():
    """doc_type 필터 시 해당 유형 행만 반환되는지 검증."""
    from bokdata.monetary_policy.fetcher import _parse_list_html

    html = """
    <table>
      <thead>
        <tr><th>날짜</th><th>결정문</th><th>기자간담회</th><th>의사록</th></tr>
      </thead>
      <tbody>
        <tr>
          <th scope="row">03월 14일(목)</th>
          <td><div class="fileGoupBox"><ul><li>
            <a href="?atchFileId=AAA&fileSn=0" title="결정문.pdf">결정문.pdf</a>
          </li></ul></div></td>
          <td></td>
          <td><div class="fileGoupBox"><ul><li>
            <a href="?atchFileId=CCC&fileSn=0" title="의사록.pdf">의사록.pdf</a>
          </li></ul></div></td>
        </tr>
      </tbody>
    </table>
    """

    rows = _parse_list_html(html, doc_type="minutes")
    assert all(r["doc_type"] == "minutes" for r in rows)
    assert len(rows) == 1
