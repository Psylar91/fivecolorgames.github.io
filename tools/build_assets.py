"""사이트 이미지 생성.

원본에서 사이트가 쓰는 이미지(로고, 파비콘, 공유 미리보기, 게임 아이콘)를 만든다.
결과 파일은 커밋하고, 원본이 바뀌었을 때만 다시 실행한다.

  python tools/build_assets.py

- 회사 로고 원본: tools/source/logo.png(1024×1024, 크림색 배경)
- 로고 마크 SVG: assets/img/logo-mark.svg(원본을 보고 손으로 옮긴 벡터). favicon.svg는 이 파일로 만든다.
- 게임 아이콘 원본은 각 게임 저장소에 있다(GAME_ICONS). 저장소가 없으면 그 아이콘은 건너뛴다.
"""
import os
import re

from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IMG = os.path.join(ROOT, "assets", "img")
LOGO = os.path.join(ROOT, "tools", "source", "logo.png")
MARK_SVG = os.path.join(IMG, "logo-mark.svg")

CREAM = (255, 248, 234)
SPECTRUM = ["#d93a36", "#ffba2a", "#338e53", "#1c89c6", "#2e4990"]

# 원본 로고 안의 영역(1024 좌표)
MARK_BOX = (200, 196, 820, 564)  # 프리즘 마크
FULL_BOX = (160, 190, 884, 830)  # 마크 + 글자

UNITY = "E:/Unity Project"
GAME_ICONS = {
    # 이름: (배경, 전경) 또는 (완성 아이콘,)
    "applegameplus": (f"{UNITY}/AppleGamePlus/Assets/@Resources/adaptive_icon_background.png",
                      f"{UNITY}/AppleGamePlus/Assets/@Resources/adaptive_icon_foreground.png"),
    "mallangpang": (f"{UNITY}/Match2/docs/store/icon_512.png",),
}


def square(im, size, pad_ratio, bg=CREAM):
    """가로로 긴 그림을 정사각형 배경 가운데에 놓는다."""
    canvas = Image.new("RGB", (size, size), bg)
    inner = int(size * (1 - 2 * pad_ratio))
    fit = im.copy()
    fit.thumbnail((inner, inner), Image.LANCZOS)
    canvas.paste(fit, ((size - fit.width) // 2, (size - fit.height) // 2))
    return canvas


def favicon_svg():
    src = open(MARK_SVG, encoding="utf-8").read()
    body = re.search(r"<svg[^>]*>(.*)</svg>", src, re.S).group(1).strip()
    # 마크(620×368)를 정사각형 크림색 바탕 가운데에 둔다.
    page = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="170 40 680 680">
  <rect x="170" y="40" width="680" height="680" rx="150" fill="#fff8ea"/>
  {body}
</svg>
"""
    with open(os.path.join(IMG, "favicon.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(page)


def main():
    os.makedirs(os.path.join(IMG, "games"), exist_ok=True)
    logo = Image.open(LOGO).convert("RGB")
    mark = logo.crop(MARK_BOX)

    # 회사 소개의 전체 로고
    full = logo.crop(FULL_BOX)
    full.thumbnail((640, 640), Image.LANCZOS)
    full.save(os.path.join(IMG, "logo.webp"), quality=90, method=6)

    # 파비콘
    favicon_svg()
    square(mark, 180, 0.12).save(os.path.join(IMG, "apple-touch-icon.png"), optimize=True)
    square(mark, 256, 0.06).save(os.path.join(ROOT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])

    # 링크 공유 미리보기(1200×630): 크림색 바탕에 로고, 아래에 다섯 색 띠
    og = Image.new("RGB", (1200, 630), CREAM)
    fit = logo.crop(FULL_BOX)
    fit.thumbnail((1000, 500), Image.LANCZOS)
    og.paste(fit, ((1200 - fit.width) // 2, (600 - fit.height) // 2))
    draw = ImageDraw.Draw(og)
    for i, color in enumerate(SPECTRUM):
        draw.rectangle([i * 240, 618, (i + 1) * 240, 630], fill=color)
    og.save(os.path.join(IMG, "og-image.jpg"), quality=88, optimize=True, progressive=True)

    # 게임 아이콘(화면 표시 약 88px, 고해상도 화면용 256px)
    for name, paths in GAME_ICONS.items():
        if not all(os.path.exists(p) for p in paths):
            print(f"skip {name}: source not found")
            continue
        layers = [Image.open(p).convert("RGBA") for p in paths]
        icon = layers[0]
        for layer in layers[1:]:
            icon = Image.alpha_composite(icon, layer.resize(icon.size))
        icon = icon.convert("RGB").resize((256, 256), Image.LANCZOS)
        icon.save(os.path.join(IMG, "games", f"{name}.webp"), quality=90, method=6)

    for dirpath, _, files in os.walk(IMG):
        for fn in sorted(files):
            p = os.path.join(dirpath, fn)
            print(f"{os.path.relpath(p, ROOT)}  {os.path.getsize(p):,} B")
    print(f"favicon.ico  {os.path.getsize(os.path.join(ROOT, 'favicon.ico')):,} B")


if __name__ == "__main__":
    main()
