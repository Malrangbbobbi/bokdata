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


def _direct_text(tag) -> str:
    """태그의 직접(direct) 텍스트만 반환 — 중첩 자식 요소 제외."""
    return " ".join(t.strip() for t in tag.find_all(string=True, recursive=False)).strip()


def _extract_date_from_row(tr) -> str:
    """
    행에서 날짜 추출 전략 (순서대로 시도):
    1. th[scope="row"] 의 직접 텍스트에서 월/일 패턴
    2. 모든 셀(th·td)의 직접 텍스트에서 월/일 패턴
    3. 실패 시 빈 문자열
    """
    candidates = []

    th = tr.find("th", {"scope": "row"})
    if th:
        candidates.append(_direct_text(th))

    for cell in tr.find_all(["th", "td"]):
        candidates.append(_direct_text(cell))

    for text in candidates:
        m = re.search(r"(\d{1,2})월\s*(\d{1,2})일", text)
        if m:
            return f"{int(m.group(1)):02d}-{int(m.group(2)):02d}"

    return ""


def _parse_list_html(html: str, doc_type: str) -> list[dict]:
    """
    mtgSe 별 페이지를 파싱한다.
    doc_type 은 요청한 mtgSe 값(statement/conference/minutes)을 그대로 신뢰.
    날짜는 th[scope="row"] 직접 텍스트 → 전체 셀 텍스트 순으로 탐색.
    """
    soup = BeautifulSoup(html, "html.parser")
    rows = []

    for tr in soup.select("table tbody tr"):
        date = _extract_date_from_row(tr)
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
