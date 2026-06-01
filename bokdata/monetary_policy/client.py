"""
bokdata.MonetaryPolicy — 한국은행 통화정책 문서 수집 클라이언트.

사용 예:
    from bokdata import MonetaryPolicy
    mp = MonetaryPolicy()
    df = mp.get_list(start=1999, end=2026)
    mp.download(year=2024, doc_type="all")
    mp.download(year=2024, format="pdf")
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Literal, Optional

import pandas as pd

from bokdata.monetary_policy.constants import START_YEAR, MTG_SE
from bokdata.monetary_policy import fetcher as _fetcher

DocType = Literal["statement", "conference", "minutes", "all"]
FileFormat = Literal["hwp", "pdf", "all"]


class MonetaryPolicy:
    """한국은행 통화정책 문서 수집기."""

    def __init__(self, use_selenium: bool = False, headless: bool = True):
        """
        Args:
            use_selenium: True 이면 requests 대신 Selenium 으로 HTML 파싱.
            headless:     Selenium 헤드리스 모드 여부.
        """
        self._use_selenium = use_selenium
        self._headless = headless

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_list(
        self,
        start: int = START_YEAR,
        end: int | None = None,
        doc_type: DocType = "all",
    ) -> pd.DataFrame:
        """
        연도 범위·문서유형별 목록을 DataFrame 으로 반환.

        Columns: year, date, title, doc_type, filename, download_url
        """
        import datetime

        if end is None:
            end = datetime.date.today().year

        doc_types = list(MTG_SE.keys()) if doc_type == "all" else [doc_type]
        records: list[dict] = []

        for year in range(start, end + 1):
            for dt in doc_types:
                rows = self._fetch_list(year, dt)
                for row in rows:
                    for f in row.get("files", []):
                        records.append(
                            {
                                "year": year,
                                "date": row["date"],
                                "doc_type": row["doc_type"],
                                "filename": f["filename"],
                                "atch_file_id": f["atch_file_id"],
                                "file_sn": f["file_sn"],
                                "download_url": f["download_url"],
                            }
                        )

        df = pd.DataFrame(records)
        if df.empty:
            return df
        df["ext"] = df["filename"].apply(lambda x: Path(x).suffix.lower().lstrip("."))
        return df.reset_index(drop=True)

    def download(
        self,
        year: int | None = None,
        start: int | None = None,
        end: int | None = None,
        doc_type: DocType = "all",
        format: FileFormat = "all",
        dest_dir: str = ".",
        verbose: bool = True,
    ) -> list[str]:
        """
        파일을 로컬에 다운로드하고 저장된 경로 목록을 반환.

        Args:
            year:     단일 연도 (start/end 와 상호배타).
            start:    시작 연도.
            end:      종료 연도.
            doc_type: "statement" | "conference" | "minutes" | "all"
            format:   "hwp" | "pdf" | "all"
            dest_dir: 저장 디렉터리.
            verbose:  진행 상황 출력.
        """
        import datetime

        if year is not None:
            start, end = year, year
        if start is None:
            start = START_YEAR
        if end is None:
            end = datetime.date.today().year

        df = self.get_list(start=start, end=end, doc_type=doc_type)
        if df.empty:
            print("다운로드할 파일이 없습니다.")
            return []

        if format != "all":
            df = df[df["ext"] == format.lower()]

        dest = Path(dest_dir)
        dest.mkdir(parents=True, exist_ok=True)
        saved: list[str] = []

        for _, row in df.iterrows():
            safe_name = _safe_filename(row["filename"])
            file_path = dest / safe_name
            if file_path.exists():
                if verbose:
                    print(f"[SKIP] {safe_name}")
                saved.append(str(file_path))
                continue
            try:
                _fetcher.download_file(row["download_url"], str(file_path))
                if verbose:
                    print(f"[OK]   {safe_name}")
                saved.append(str(file_path))
            except Exception as e:
                if verbose:
                    print(f"[ERR]  {safe_name}: {e}")

        return saved

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _fetch_list(self, year: int, doc_type: str) -> list[dict]:
        if self._use_selenium:
            from bokdata.monetary_policy.selenium_fetcher import fetch_year_list_selenium
            return fetch_year_list_selenium(year, doc_type, headless=self._headless)
        return _fetcher.fetch_year_list(year, doc_type)


def _safe_filename(name: str) -> str:
    """파일시스템에 안전한 파일명으로 변환."""
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    return name.strip()
