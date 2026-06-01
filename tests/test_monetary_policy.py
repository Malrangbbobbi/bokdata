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


def test_parse_date_from_th_direct_text():
    """th[scope="row"] 에 파일박스가 중첩돼도 직접 텍스트에서 날짜를 파싱한다."""
    from bokdata.monetary_policy.fetcher import _parse_list_html

    html = """
    <table><tbody>
      <tr>
        <th scope="row">01월 14일(금)
          <div class="fileGoupBox"><ul><li>
            <a href="?atchFileId=AAA&fileSn=0" title="결정문.pdf">결정문.pdf</a>
          </li></ul></div>
        </th>
      </tr>
    </tbody></table>
    """
    rows = _parse_list_html(html, doc_type="statement")
    assert rows[0]["date"] == "01-14"


def test_parse_list_html_doctype_uses_param():
    """doc_type 은 mtgSe URL 파라미터(전달값)를 그대로 사용한다."""
    from bokdata.monetary_policy.fetcher import _parse_list_html

    html = """
    <table><tbody>
      <tr>
        <th scope="row">03월 14일(목)</th>
        <td><div class="fileGoupBox"><ul><li>
          <a href="?atchFileId=AAA&fileSn=0" title="의사록.pdf">의사록.pdf</a>
        </li></ul></div></td>
      </tr>
    </tbody></table>
    """
    rows = _parse_list_html(html, doc_type="minutes")
    assert len(rows) == 1
    assert rows[0]["doc_type"] == "minutes"
    assert rows[0]["date"] == "03-14"


def test_date_fallback_to_any_cell():
    """th[scope="row"] 에 날짜 없으면 다른 셀에서 탐색한다."""
    from bokdata.monetary_policy.fetcher import _parse_list_html

    html = """
    <table><tbody>
      <tr>
        <th scope="row">
          <div class="fileGoupBox"><ul><li>
            <a href="?atchFileId=BBB&fileSn=0" title="기자간담회.pdf">기자간담회.pdf</a>
          </li></ul></div>
        </th>
        <td>05월 29일(목) 관련 회의록</td>
      </tr>
    </tbody></table>
    """
    rows = _parse_list_html(html, doc_type="conference")
    assert rows[0]["date"] == "05-29"
    assert rows[0]["doc_type"] == "conference"
