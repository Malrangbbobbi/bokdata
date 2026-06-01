"""
Selenium 기반 폴백 fetcher.
requests 로 파일 링크를 파싱할 수 없을 때 사용.
selenium 패키지가 설치돼 있지 않으면 ImportError 를 호출 시점에 발생시킨다.
"""
import urllib.parse
import re

from bokdata.monetary_policy.constants import LIST_URL, MENU_NO, MTG_SE, DOWNLOAD_URL


def _build_driver(headless: bool = True):
    # lazy import — selenium 없는 환경에서 모듈 import 시 터지지 않도록
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

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
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    mtg_se = MTG_SE[doc_type]
    url = LIST_URL.format(mtg_se=mtg_se, menu_no=MENU_NO, year=year)

    driver = _build_driver(headless)
    rows = []
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
        )
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
    from selenium.webdriver.common.by import By

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
