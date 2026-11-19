# fivecolorgames.github.io

FiveColorGames 홈페이지 <https://fivecolorgames.com> 의 소스다. GitHub Pages로 게시하며, 빌드 도구 없이 손으로 쓴 정적 HTML이다.

| 경로 | 내용 |
|---|---|
| `index.html`, `en/index.html` | 홈(한국어, 영어) |
| `games/` | 게임 목록 페이지(SNS 프로필 링크용). 목록은 `games/games.json`, 그리기는 `assets/js/games.js` |
| `<게임>/privacy.html` | 게임별 개인정보처리방침(한국어·영어 한 장) |
| `app-ads.txt` | AdMob 판매자 인증 파일. 사이트 최상위에 있어야 한다 |
| `assets/` | 스타일과 이미지 |
| `tools/` | 이미지 생성 스크립트와 원본(사이트에는 게시하지 않음) |
| `CNAME` | 사용자 도메인 `fivecolorgames.com` |

## 로컬 미리보기

```
python -m http.server 8780
```

<http://127.0.0.1:8780> 에서 확인한다. 페이지가 `/assets/...`처럼 사이트 최상위 기준 경로를 쓰므로 저장소 루트에서 서버를 띄운다.

## 이미지 다시 만들기

```
python tools/build_assets.py
```

로고 원본(`tools/source/logo.png`)이나 게임 아이콘이 바뀌었을 때만 실행한다(Pillow 필요).

## 게임 목록 페이지에 게임 더하기

1. `games/games.json`에 한 줄을 더한다. `id`는 방침 폴더 이름과 같고(`/<id>/privacy.html`), 아이콘은 `assets/img/games/<id>.webp`다.
2. 아이콘이 없으면 `tools/build_assets.py`의 `GAME_ICONS`에 원본을 더하고 실행한다.
3. `python tools/check_site.py`로 필수 칸·패키지 형식·아이콘·방침 파일을 확인한다.

페이지는 주소의 `?from=<플랫폼>`을 Google Play 주소의 `referrer`(`utm_source`)로 넘긴다. 없으면 `website`다.
