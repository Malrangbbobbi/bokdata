# bokdata

한국은행 데이터를 **pykrx** 처럼 쓸 수 있는 Python 패키지.

```bash
pip install bokdata
```

Selenium 지원이 필요하면:

```bash
pip install "bokdata[selenium]"
```

---

## 빠른 시작

```python
from bokdata import MonetaryPolicy

mp = MonetaryPolicy()

# 목록 조회 → pandas DataFrame
df = mp.get_list(start=1999, end=2026)
df = mp.get_list(start=2024, end=2024, doc_type="minutes")

# 파일 다운로드
mp.download(year=2024)                          # 전체 문서·전체 형식
mp.download(year=2024, doc_type="minutes")      # 의사록만
mp.download(year=2024, format="pdf")            # PDF만
mp.download(start=2020, end=2024, dest_dir="downloads/")
```

---

## doc_type 옵션

| 값 | 설명 |
|---|---|
| `"statement"` | 통화정책결정문 |
| `"conference"` | 기자간담회 |
| `"minutes"` | 의사록 |
| `"all"` | 전체 (기본값) |

## format 옵션

| 값 | 설명 |
|---|---|
| `"hwp"` | HWP 파일만 |
| `"pdf"` | PDF 파일만 |
| `"all"` | 전체 (기본값) |

---

## Selenium 모드

JavaScript 렌더링이 필요한 경우:

```python
mp = MonetaryPolicy(use_selenium=True, headless=True)
```

ChromeDriver 가 PATH 에 있어야 합니다.

---

## 개발

```bash
git clone https://github.com/Malarngbbobbi/bokdata.git
cd bokdata
pip install -e ".[dev]"
pytest
```

---

## 의사록 파일명 패턴

| 연도 | 패턴 |
|---|---|
| 1999 | `99년N차.hwp` |
| 2000–2002 | `의사록(2000년도제N차).hwp` |
| 2003–2005 | `금융통화위원회 의사록(2003년도 제N차).hwp` |
| 2006–2020 | `제N차+금통위+의사록.hwp/pdf` |
| 2021– | `금융통화위원회 의사록(2021년도 제N차)(날짜).hwp/pdf` |

---

## License

MIT
