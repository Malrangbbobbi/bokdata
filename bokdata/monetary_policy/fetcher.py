"""
XHR/requests 기반 HTML 페이지 취득.
JS 렌더링이 필요한 경우 selenium_fetcher.py 로 폴백.
"""
import re
import urllib.parse
from typing import Optional

import requests
from bs4 import BeautifulSoup

from bokdata.monetary_policy.constants import (
    BASE_URL,
    DOWNLOAD_URL,
    LIST_URL,
    MENU_NO,
    MTG_SE,
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": BASE_URL,
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def _fetch_html(url: str) -> str:
    resp = SESSION.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text


def _parse_file_items(html: str) -> list[dict]:
    """
    .fileGoupBox li a 에서 파일 정보 파싱.
    display:none 레이어이므로 requests 로도 HTML 텍스트에 포함됨.
    """
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for a in soup.select(".fileGoupBox li a"):
        href = a.get("href", "")
        title = a.get("title", "") or a.get_text(strip=True)
        title = urllib.parse.unquote_plus(title)

        # atchFileId, fileSn 추출
        atch_match = re.search(r"atchFileId=([^&'\"]+)", href)
        sn_match = re.search(r"fileSn=([^&'\"]+)", href)
        if not (atch_match and sn_match):
            # onclick 속성 폴백
            onclick = a.get("onclick", "")
            atch_match = re.search(r"atchFileId['\"]?\s*[,:]?\s*['\"]?([A-Z0-9]+)", onclick)
            sn_match = re.search(r"fileSn['\"]?\s*[,:]?\s*['\"]?(\d+)", onclick)

        if atch_match and sn_match:
            items.append(
                {
                    "filename": title,
                    "atch_file_id": atch_match.group(1),
                    "file_sn": sn_match.group(1),
                    "download_url": DOWNLOAD_URL.format(
                        menu_no=MENU_NO,
                        atch_file_id=atch_match.group(1),
                        file_sn=sn_match.group(1),
                    ),
                }
            )
    return items


def fetch_year_list(year: int, doc_type: str) -> list[dict]:
    """
    연도·문서유형별 목록 페이지 파싱.
    반환: [{"date": ..., "title": ..., "doc_type": ..., "files": [...]}]
    """
    mtg_se = MTG_SE[doc_type]
    url = LIST_URL.format(mtg_se=mtg_se, menu_no=MENU_NO, year=year)
    html = _fetch_html(url)
    return _parse_list_html(html, doc_type)


def _parse_date(raw: str) -> str:
    """'01월 14일(금)' → '01-14', 파싱 실패 시 원문 반환."""
    m = re.search(r"(\d{1,2})월\s*(\d{1,2})일", raw)
    if m:
        return f"{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    return raw.strip()


# thead th 텍스트 → doc_type 매핑
_HEADER_TO_DOCTYPE: dict[str, str] = {
    "결정문": "statement",
    "기자간담회": "conference",
    "의사록": "minutes",
}


def _parse_list_html(html: str, doc_type: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    rows = []

    # thead th 순서로 td 인덱스 → doc_type 매핑 구성
    # th[0] = 날짜(scope=row 헤더), th[1]= 결정문, th[2]= 기자간담회, th[3]= 의사록
    # → td 인덱스는 헤더 인덱스 -1
    td_to_doctype: dict[int, str] = {}
    for table in soup.select("table"):
        for i, th in enumerate(table.select("thead th")):
            text = th.get_text(strip=True)
            for keyword, dt in _HEADER_TO_DOCTYPE.items():
                if keyword in text:
                    td_to_doctype[i - 1] = dt  # th 인덱스 -1 = td 인덱스
        if td_to_doctype:
            break  # 첫 번째 테이블만 사용

    for tr in soup.select("table tbody tr"):
        # 날짜: th[scope="row"] 우선, 없으면 첫 번째 td
        th_row = tr.find("th", {"scope": "row"})
        date_raw = th_row.get_text(strip=True) if th_row else ""
        date = _parse_date(date_raw) if date_raw else ""

        tds = tr.find_all("td")
        if not tds:
            continue

        if td_to_doctype:
            # 헤더에서 파악한 인덱스별로 각 doc_type 파일 수집
            for td_idx, dt in td_to_doctype.items():
                # doc_type 필터가 걸려 있으면 해당 유형만 수집
                if doc_type != "all" and dt != doc_type:
                    continue
                if td_idx >= len(tds):
                    continue
                files = _parse_file_items(str(tds[td_idx]))
                if files:
                    rows.append(
                        {
                            "date": date,
                            "doc_type": dt,
                            "files": files,
                        }
                    )
        else:
            # 헤더 파싱 실패 시 전체 td 에서 파일 수집 (기존 동작 유지)
            files = _parse_file_items(str(tr))
            if files:
                rows.append(
                    {
                        "date": date,
                        "doc_type": doc_type,
                        "files": files,
                    }
                )

    return rows


def download_file(download_url: str, dest_path: str) -> None:
    resp = SESSION.get(download_url, timeout=60, stream=True)
    resp.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
