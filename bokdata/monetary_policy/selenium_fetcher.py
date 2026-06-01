"""
Selenium 기반 폴백 fetcher.
requests 로 파일 링크를 파싱할 수 없을 때 사용.
"""
import time
import urllib.parse
import re
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from bokdata.monetary_policy.constants import LIST_URL, MENU_NO, MTG_SE, DOWNLOAD_URL


def _build_driver(headless: bool = True) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=options)


def fetch_year_list_selenium(year: int, doc_type: str, headless: bool = True) -> list[dict]:
    mtg_se = MTG_SE[doc_type]
    url = LIST_URL.format(mtg_se=mtg_se, menu_no=MENU_NO, year=year)

    driver = _build_driver(headless)
    rows = []
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
        )
        # display:none 레이어도 DOM 에 존재하므로 find_elements 로 취득
        trs = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        for tr in trs:
            tds = tr.find_elements(By.TAG_NAME, "td")
            if len(tds) < 2:
                continue
            date_text = tds[0].text.strip()
            title_text = tds[1].text.strip()
            files = _extract_files_selenium(tr)
            rows.append(
                {
                    "date": date_text,
                    "title": title_text,
                    "doc_type": doc_type,
                    "files": files,
                }
            )
    finally:
        driver.quit()
    return rows


def _extract_files_selenium(tr_element) -> list[dict]:
    files = []
    anchors = tr_element.find_elements(By.CSS_SELECTOR, ".fileGoupBox li a")
    for a in anchors:
        href = a.get_attribute("href") or ""
        title = a.get_attribute("title") or a.text.strip()
        title = urllib.parse.unquote_plus(title)

        atch_match = re.search(r"atchFileId=([^&'\"]+)", href)
        sn_match = re.search(r"fileSn=([^&'\"]+)", href)
        if not (atch_match and sn_match):
            onclick = a.get_attribute("onclick") or ""
            atch_match = re.search(r"atchFileId['\"]?\s*[,:]?\s*['\"]?([A-Z0-9]+)", onclick)
            sn_match = re.search(r"fileSn['\"]?\s*[,:]?\s*['\"]?(\d+)", onclick)

        if atch_match and sn_match:
            files.append(
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
    return files
