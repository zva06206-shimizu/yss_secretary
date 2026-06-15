#!/usr/bin/env python3
"""Check public whitepaper/report source URLs and generate a monthly report.

Input:
- data/knowledge/public-data/source-index.md
- data/knowledge/public-data/public-whitepapers-and-reports.md

Output:
- data/knowledge/public-data/reports/YYYY-MM-public-source-check.md
- data/knowledge/public-data/source-check-latest.md

This script extracts URLs from Markdown files, checks HTTP status, records redirects,
and writes a Markdown report. It does not download full PDFs by default.
"""

from __future__ import annotations

import datetime as dt
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[3]
PUBLIC_DATA_DIR = ROOT / "data" / "knowledge" / "public-data"
REPORT_DIR = PUBLIC_DATA_DIR / "reports"
INPUT_FILES = [
    PUBLIC_DATA_DIR / "source-index.md",
    PUBLIC_DATA_DIR / "public-whitepapers-and-reports.md",
]
TIMEOUT_SECONDS = 20
USER_AGENT = "system-create-public-source-check/1.0 (+https://github.com/)"

URL_RE = re.compile(r"https?://[^\s)\]}>\"'`]+")


@dataclass
class CheckResult:
    url: str
    status: str
    http_status: str
    final_url: str
    note: str


def extract_urls(paths: Iterable[Path]) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for match in URL_RE.findall(text):
            url = match.rstrip(".,。")
            if url not in seen:
                seen.add(url)
                urls.append(url)
    return urls


def check_url(url: str) -> CheckResult:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status_code = getattr(response, "status", None) or response.getcode()
            final_url = response.geturl()
            if 200 <= int(status_code) < 400:
                status = "OK"
            else:
                status = "要確認"
            note = ""
            if final_url != url:
                note = f"redirected to {final_url}"
            return CheckResult(url, status, str(status_code), final_url, note)
    except HTTPError as exc:
        status = "NG" if exc.code in {404, 410} else "要確認"
        return CheckResult(url, status, str(exc.code), url, str(exc.reason))
    except URLError as exc:
        return CheckResult(url, "要確認", "-", url, str(exc.reason))
    except Exception as exc:  # noqa: BLE001
        return CheckResult(url, "要確認", "-", url, f"{type(exc).__name__}: {exc}")


def build_report(results: list[CheckResult]) -> str:
    today = dt.date.today()
    ok_count = sum(1 for item in results if item.status == "OK")
    ng_count = sum(1 for item in results if item.status == "NG")
    warn_count = sum(1 for item in results if item.status == "要確認")

    lines: list[str] = []
    lines.append(f"# Public Source Check Report - {today:%Y-%m}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Checked date: {today.isoformat()}")
    lines.append(f"- Total URLs: {len(results)}")
    lines.append(f"- OK: {ok_count}")
    lines.append(f"- NG: {ng_count}")
    lines.append(f"- 要確認: {warn_count}")
    lines.append("")
    lines.append("## Results")
    lines.append("")
    lines.append("| URL | 結果 | HTTP | 最終URL | 備考 |")
    lines.append("|---|---|---:|---|---|")
    for item in results:
        lines.append(
            f"| {item.url} | {item.status} | {item.http_status} | {item.final_url} | {item.note} |"
        )
    lines.append("")
    lines.append("## Required Follow-up")
    lines.append("")
    followups = [item for item in results if item.status != "OK"]
    if not followups:
        lines.append("- 現時点で要対応URLはありません。")
    else:
        for item in followups:
            lines.append(f"- {item.url}: {item.status} / {item.http_status} / {item.note}")
    lines.append("")
    lines.append("## Operation Notes")
    lines.append("")
    lines.append("- 404/410は差し替え候補を調査する。")
    lines.append("- リダイレクトは、恒久的な移動か確認して一覧を更新する。")
    lines.append("- 白書の最新版PDF URL、発行年、更新頻度は別途確認する。")
    lines.append("- 提案書に使った統計は、発行年と出典を必ず記録する。")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    urls = extract_urls(INPUT_FILES)
    if not urls:
        print("No URLs found.", file=sys.stderr)
        return 1

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    results = [check_url(url) for url in urls]
    report = build_report(results)

    month = dt.date.today().strftime("%Y-%m")
    monthly_report = REPORT_DIR / f"{month}-public-source-check.md"
    latest_report = PUBLIC_DATA_DIR / "source-check-latest.md"
    monthly_report.write_text(report, encoding="utf-8")
    latest_report.write_text(report, encoding="utf-8")

    print(f"Wrote {monthly_report}")
    print(f"Wrote {latest_report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
