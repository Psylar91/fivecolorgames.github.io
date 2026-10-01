"""게시 전 정적 점검.

  python tools/check_site.py

- 모든 HTML의 내부 링크·이미지·스타일 경로가 실제 파일로 이어지는지, `#앵커`가 대상 페이지에 있는지
- 개인정보처리방침에 `{EFFECTIVE_DATE}` 같은 자리 표시가 남지 않았는지
- mailto 주소가 정식 주소인지
- app-ads.txt가 사이트 최상위에 있는지
문제가 있으면 종료 코드 1을 돌려준다.
"""
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlsplit

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EMAIL = "fivecolorgames.official@gmail.com"
SKIP_DIRS = {".git", ".claude", "_docs", "tools", "node_modules"}


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for key in ("href", "src"):
            if a.get(key):
                self.links.append((tag, a[key]))


def parse(path):
    c = Collector()
    c.feed(open(path, encoding="utf-8").read())
    return c


def target_file(page, url_path):
    if url_path.startswith("/"):
        p = os.path.join(ROOT, url_path.lstrip("/"))
    else:
        p = os.path.join(os.path.dirname(page), url_path)
    if url_path.endswith("/") or os.path.isdir(p):
        p = os.path.join(p, "index.html")
    return os.path.normpath(p)


def main():
    pages = []
    for dirpath, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        pages += [os.path.normpath(os.path.join(dirpath, f)) for f in files if f.endswith(".html")]
    parsed = {p: parse(p) for p in pages}
    errors = []

    for page, c in parsed.items():
        rel = os.path.relpath(page, ROOT)
        for tag, url in c.links:
            if url.startswith("mailto:"):
                if url != f"mailto:{EMAIL}":
                    errors.append(f"{rel}: wrong mailto {url}")
                continue
            parts = urlsplit(url)
            if parts.scheme or url.startswith("//"):
                continue
            if not parts.path:  # 같은 페이지 앵커
                if parts.fragment and parts.fragment not in c.ids:
                    errors.append(f"{rel}: missing anchor #{parts.fragment}")
                continue
            target = target_file(page, parts.path)
            if not os.path.exists(target):
                errors.append(f"{rel}: missing {url}")
            elif parts.fragment and target in parsed and parts.fragment not in parsed[target].ids:
                errors.append(f"{rel}: missing anchor {url}")

    for page in pages:
        text = open(page, encoding="utf-8").read()
        if "privacy" in page and re.search(r"\{[A-Z_]+\}", text):
            errors.append(f"{os.path.relpath(page, ROOT)}: placeholder left")

    ads = os.path.join(ROOT, "app-ads.txt")
    if not os.path.exists(ads) or "pub-" not in open(ads, encoding="utf-8").read():
        errors.append("app-ads.txt missing or empty")

    for e in errors:
        print("ERROR", e)
    print(f"{len(pages)} pages, {sum(len(c.links) for c in parsed.values())} links, {len(errors)} errors")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
