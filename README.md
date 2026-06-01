# bokdata

**[한국어](#한국어) | [English](#english)**

---

<a name="한국어"></a>
## 한국어

한국은행 문서를 손쉽게 다운로드할 수 있는 오픈소스 Python 패키지입니다.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![CI](https://github.com/Malarngbbobbi/bokdata/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Malarngbbobbi/bokdata/actions)

### 설치

```bash
pip install bokdata
```

Selenium 지원이 필요하면:

```bash
pip install "bokdata[selenium]"
```

### 빠른 시작

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

### doc_type 옵션

| 값 | 설명 |
|---|---|
| `"statement"` | 통화정책결정문 |
| `"conference"` | 기자간담회 |
| `"minutes"` | 의사록 |
| `"all"` | 전체 (기본값) |

### format 옵션

| 값 | 설명 |
|---|---|
| `"hwp"` | HWP 파일만 |
| `"pdf"` | PDF 파일만 |
| `"all"` | 전체 (기본값) |

### Selenium 모드

JavaScript 렌더링이 필요한 경우:

```python
mp = MonetaryPolicy(use_selenium=True, headless=True)
```

ChromeDriver 가 PATH 에 있어야 합니다.

### 의사록 파일명 패턴

| 연도 | 패턴 |
|---|---|
| 1999 | `99년N차.hwp` |
| 2000–2002 | `의사록(2000년도제N차).hwp` |
| 2003–2005 | `금융통화위원회 의사록(2003년도 제N차).hwp` |
| 2006–2020 | `제N차+금통위+의사록.hwp/pdf` |
| 2021– | `금융통화위원회 의사록(2021년도 제N차)(날짜).hwp/pdf` |

### 개발 참여 (Contributing)

오픈소스 프로젝트로, 누구나 기여할 수 있습니다.

```bash
git clone https://github.com/Malarngbbobbi/bokdata.git
cd bokdata
pip install -e ".[dev]"
pytest
```

이슈·PR은 언제든지 환영합니다.

### 라이선스

[MIT License](LICENSE) — 자유롭게 사용·수정·배포할 수 있습니다.

---

<a name="english"></a>
## English

**bokdata** is an open-source Python package for downloading documents published by the Bank of Korea (BOK).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![CI](https://github.com/Malarngbbobbi/bokdata/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Malarngbbobbi/bokdata/actions)

### Installation

```bash
pip install bokdata
```

With Selenium support:

```bash
pip install "bokdata[selenium]"
```

### Quick Start

```python
from bokdata import MonetaryPolicy

mp = MonetaryPolicy()

# Retrieve document list as a pandas DataFrame
df = mp.get_list(start=1999, end=2026)
df = mp.get_list(start=2024, end=2024, doc_type="minutes")

# Download files
mp.download(year=2024)                          # all documents, all formats
mp.download(year=2024, doc_type="minutes")      # minutes only
mp.download(year=2024, format="pdf")            # PDF only
mp.download(start=2020, end=2024, dest_dir="downloads/")
```

### doc_type Options

| Value | Description |
|---|---|
| `"statement"` | Monetary policy decision statement |
| `"conference"` | Press conference |
| `"minutes"` | Meeting minutes |
| `"all"` | All types (default) |

### format Options

| Value | Description |
|---|---|
| `"hwp"` | HWP files only |
| `"pdf"` | PDF files only |
| `"all"` | All formats (default) |

### Selenium Mode

Use when JavaScript rendering is required:

```python
mp = MonetaryPolicy(use_selenium=True, headless=True)
```

ChromeDriver must be available in your PATH.

### Contributing

bokdata is open source and contributions are welcome.

```bash
git clone https://github.com/Malarngbbobbi/bokdata.git
cd bokdata
pip install -e ".[dev]"
pytest
```

Feel free to open issues or submit pull requests.

### License

[MIT License](LICENSE) — free to use, modify, and distribute.
