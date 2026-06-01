BASE_URL = "https://www.bok.or.kr"

# mtgSe 코드
MTG_SE = {
    "statement": "A",   # 통화정책결정문
    "conference": "B",  # 기자간담회
    "minutes": "C",     # 의사록
}

MENU_NO = "200755"

LIST_URL = (
    BASE_URL
    + "/portal/singl/crncyPolicyDrcMtg/listYear.do"
    + "?mtgSe={mtg_se}&menuNo={menu_no}&pYear={year}"
)

DOWNLOAD_URL = (
    BASE_URL
    + "/portal/cmmn/file/fileDown.do"
    + "?menuNo={menu_no}&atchFileId={atch_file_id}&fileSn={file_sn}"
)

START_YEAR = 1999
