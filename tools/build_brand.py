"""브랜드 로고 원본 → 사이트에서 쓰는 파일 생성.

사용법:  py tools/build_brand.py
원본:    assets/brand/logo-horizontal-source.svg  (디자이너가 준 가로 로고. 로고가 바뀌면 이 파일만 교체)
결과물:  assets/img/logo.svg            헤더용 가로 로고 (여백 제거, 잉크색)
         assets/img/favicon.svg         탭 아이콘 (심볼만, 어두운 둥근 사각형 위)
         assets/img/favicon-32.png      구형 브라우저용
         assets/img/apple-touch-icon.png 아이폰 홈 화면 추가용 (180px)

원본 구조 가정: <svg> 안에 [심볼 경로 3개] → [글자 경로 여러 개] → <defs> 순서.
"""
import asyncio
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "brand" / "logo-horizontal-source.svg"
OUT = ROOT / "assets" / "img"

INK = "#16161a"      # 로고 글자·심볼 색 (사이트 본문 잉크색)
CREAM = "#f9f7f5"    # 파비콘 속 심볼 색 (사이트 바탕색)

# 원본(908×178)에서 실제 그림이 차지하는 영역 — 브라우저로 측정한 값
SYM = (24, 24, 226.71, 154)       # 심볼 x0, y0, x1, y1
ALL = (24, 24, 883.63, 154)       # 심볼+글자 전체


def split(svg: str):
    inner = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1)
    defs = re.search(r"<defs>.*?</defs>", inner, re.S).group(0)
    body = inner.replace(defs, "").strip()
    # 글자 경로의 시작점(첫 글자 'n'의 오른쪽 기둥)을 기준으로 심볼과 글자를 가른다
    cut = body.index('<path d="M825.417')
    return body[:cut].strip(), body[cut:].strip(), defs


def uniq(s: str) -> str:
    """clipPath id가 페이지의 다른 SVG와 겹치지 않게 이름을 바꾼다."""
    return re.sub(r"clip(\d)_\d+_\d+", r"meomun-clip\1", s)


def build_svgs():
    svg = SRC.read_text(encoding="utf-8")
    sym, word, defs = split(svg)
    x0, y0, x1, y1 = ALL
    w, h = x1 - x0, y1 - y0

    logo = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" viewBox="{x0} {y0} {w:.2f} {h:.2f}" fill="none" role="img" aria-label="meomun">\n'
        f"{sym}\n{word}\n{defs}\n</svg>\n"
    ).replace('fill="black"', f'fill="{INK}"')
    (OUT / "logo.svg").write_text(uniq(logo), encoding="utf-8")

    sx0, sy0, sx1, sy1 = SYM
    sw, sh = sx1 - sx0, sy1 - sy0

    def icon(size: int, radius: float, pad: float) -> str:
        scale = (size - pad * 2) / sw
        tx = pad
        ty = (size - sh * scale) / 2
        body = sym.replace('fill="black"', f'fill="{CREAM}"')
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}" fill="none">\n'
            f'<rect width="{size}" height="{size}" rx="{radius}" fill="{INK}"/>\n'
            f'<g transform="translate({tx:.2f} {ty:.2f}) scale({scale:.5f}) translate({-sx0} {-sy0})">\n{body}\n</g>\n{defs}\n</svg>\n'
        )

    (OUT / "favicon.svg").write_text(uniq(icon(64, 14, 9)), encoding="utf-8")
    return uniq(icon(32, 7, 4.5)), uniq(icon(180, 0, 28))


async def render_png(svg: str, size: int, path: Path):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome")
        pg = await (await b.new_context(viewport={"width": size, "height": size}, device_scale_factor=1)).new_page()
        await pg.set_content(f'<body style="margin:0;background:transparent">{svg}</body>')
        await pg.screenshot(path=str(path), omit_background=True, clip={"x": 0, "y": 0, "width": size, "height": size})
        await b.close()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    small, touch = build_svgs()
    asyncio.run(render_png(small, 32, OUT / "favicon-32.png"))
    asyncio.run(render_png(touch, 180, OUT / "apple-touch-icon.png"))
    for n in ("logo.svg", "favicon.svg", "favicon-32.png", "apple-touch-icon.png"):
        print(n, (OUT / n).stat().st_size, "bytes")


if __name__ == "__main__":
    main()
