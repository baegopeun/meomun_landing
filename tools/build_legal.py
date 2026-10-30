"""content/*.txt → 약관·처리방침·계정 삭제 안내 HTML 생성.

사용법:  py tools/build_legal.py
결과물:  terms/index.html, privacy/index.html, delete-account/index.html
줄 형식은 content/privacy.txt 맨 위 설명 참고.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAGES = [
    # (원문 파일, 출력 폴더, 푸터에서 굵게 할 링크, 목차 표시 여부)
    ("terms.txt", "terms", "/terms/", True),
    ("privacy.txt", "privacy", "/privacy/", True),
    ("delete-account.txt", "delete-account", "/delete-account/", False),
]

FOOT_LINKS = [
    ("/privacy/", "개인정보 처리방침"),
    ("/terms/", "이용약관"),
    ("/delete-account/", "계정 삭제 안내"),
    ("mailto:baegopeun703@gmail.com", "문의"),
]

LINK_RE = re.compile(
    r"\[(?P<label>[^\]]+)\]\((?P<href>[^)\s]+)\)"                                  # [글자](주소)
    r"|(?P<url>https?://[A-Za-z0-9._~:/?#@!$&'*+,;=%-]+[A-Za-z0-9/])"               # https://...
    r"|(?P<mail>[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)"               # 이메일
    r"|(?P<host>\b(?:www\.)?[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:go|or)\.kr\b)"          # 기관 누리집
)


def inline(text: str) -> str:
    out, pos = [], 0
    for m in LINK_RE.finditer(text):
        out.append(bold(html.escape(text[pos:m.start()], quote=False)))
        if m.group("label"):
            out.append(f'<a href="{html.escape(m.group("href"))}">{html.escape(m.group("label"))}</a>')
        elif m.group("url"):
            u = m.group("url")
            out.append(f'<a href="{html.escape(u)}" target="_blank" rel="noopener">{html.escape(u)}</a>')
        elif m.group("mail"):
            e = m.group("mail")
            out.append(f'<a href="mailto:{e}">{e}</a>')
        else:
            h = m.group("host")
            out.append(f'<a href="https://{h}" target="_blank" rel="noopener">{h}</a>')
        pos = m.end()
    out.append(bold(html.escape(text[pos:], quote=False)))
    return "".join(out)


def bold(s: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)


def parse(path: Path):
    meta, blocks = {}, []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.startswith("#"):
            continue
        kind, _, rest = raw.partition("|")
        if kind in ("TITLE", "META"):
            meta[kind] = rest
        elif kind in ("HANG", "HO", "HO2"):
            no, _, body = rest.partition("|")
            blocks.append((kind, no, body))
        else:
            blocks.append((kind, "", rest))
    return meta, blocks


def render_body(blocks):
    parts, toc, open_article = [], [], False
    n = 0

    def close():
        nonlocal open_article
        if open_article:
            parts.append("        </section>")
            open_article = False

    for kind, no, text in blocks:
        if kind == "CH":
            close()
            n += 1
            parts.append(f'        <h2 class="chapter" id="c{n}">{html.escape(text)}</h2>')
            toc.append(("group", f"c{n}", text))
        elif kind == "H":
            close()
            n += 1
            parts.append(f'        <section class="article" id="a{n}">')
            parts.append(f"          <h2>{html.escape(text)}</h2>")
            toc.append(("item", f"a{n}", text))
            open_article = True
        elif kind == "P":
            parts.append(f"          <p>{inline(text)}</p>")
        else:
            cls = {"HANG": "item hang", "HO": "item", "HO2": "item sub"}[kind]
            parts.append(f'          <p class="{cls}"><span class="no">{html.escape(no)}</span><span class="tx">{inline(text)}</span></p>')
    close()
    # 첫 문단(들어가며)이 조보다 앞에 오면 article 밖에 둔다
    return "\n".join(parts), toc


TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{title} — {meta}">
  <meta name="theme-color" content="#f9f7f5">
  <link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
  <link rel="icon" href="/assets/img/favicon-32.png" sizes="32x32" type="image/png">
  <link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
  <link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
  <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
<!-- 이 파일은 tools/build_legal.py 가 content/{src} 로부터 만든 것입니다. 직접 고치지 말고 원문을 고친 뒤 다시 실행하세요. -->
<div class="page">
  <div class="grain" aria-hidden="true"></div>
  <header class="top">
    <a class="logo" href="/" aria-label="머문 홈"><img src="/assets/img/logo.svg" alt="meomun" width="860" height="130"></a>
    <a class="back" href="/">← 홈으로</a>
  </header>
  <main>
    <div class="doc-head">
      <h1>{title}</h1>
      <p>{meta}</p>
    </div>
    <div class="doc">
{toc}      <div class="doc-body">
{body}
      </div>
    </div>
  </main>
  <footer class="foot">
    <nav aria-label="안내">
{foot}
    </nav>
    <div class="foot-meta">
      <small>© 2026 꼬르륵</small>
      <small>YouTube는 Google LLC의 상표입니다.</small>
    </div>
  </footer>
</div>
{script}</body>
</html>
"""

# 목차: 지금 읽는 조를 강조
SCROLLSPY = """<script>
(() => {
  const links = [...document.querySelectorAll('.toc a')];
  const targets = links.map(a => document.querySelector(a.getAttribute('href')));
  const box = document.querySelector('.toc');
  const set = i => {
    links.forEach((a, j) => a.classList.toggle('on', j === i));
    const a = links[i];
    if (box && a && box.scrollHeight > box.clientHeight) {          // 목차가 화면보다 길면 현재 항목이 보이게 목차만 스크롤
      const top = a.getBoundingClientRect().top - box.getBoundingClientRect().top + box.scrollTop;   // 목차 상자 안에서의 위치
      if (top < box.scrollTop + 40 || top > box.scrollTop + box.clientHeight - 60) box.scrollTop = top - box.clientHeight / 2;
    }
  };
  const onScroll = () => {
    let cur = 0;
    targets.forEach((t, i) => { if (t && t.getBoundingClientRect().top < 120) cur = i; });
    if (innerHeight + scrollY >= document.body.scrollHeight - 4) cur = targets.length - 1;
    set(cur);
  };
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();
</script>
"""


def build():
    for src, out_dir, current, with_toc in PAGES:
        meta, blocks = parse(ROOT / "content" / src)
        body, toc = render_body(blocks)
        toc_html = ""
        if with_toc and toc:
            rows = ['      <nav class="toc" aria-label="목차">', '        <span class="toc-label">목차</span>']
            first = True
            for kind, anchor, text in toc:
                if kind == "group":
                    rows.append(f'        <a class="toc-group" href="#{anchor}">{html.escape(text)}</a>')
                else:
                    rows.append(f'        <a href="#{anchor}"{" class=\"on\"" if first else ""}>{html.escape(text)}</a>')
                    first = False
            rows.append("      </nav>")
            toc_html = "\n".join(rows) + "\n"
        foot = "\n".join(
            f'      <a href="{href}"{" aria-current=\"page\"" if href == current else ""}>{label}</a>'
            for href, label in FOOT_LINKS
        )
        page = TEMPLATE.format(
            title=html.escape(meta["TITLE"]), meta=html.escape(meta.get("META", "")), src=src,
            toc=toc_html, body=body, foot=foot, script=SCROLLSPY if toc_html else "",
        )
        target = ROOT / out_dir / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page, encoding="utf-8")
        print(f"{target.relative_to(ROOT)}  ({len(blocks)}줄, 목차 {len(toc)}개)")


if __name__ == "__main__":
    build()
