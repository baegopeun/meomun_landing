# meomun_landing
순간의 기억을 노래에 담아 기록하는 앱, 머문의 랜딩페이지 제작과 관련된 레퍼지토리입니다

## 구성

| 주소 | 파일 | 설명 |
|---|---|---|
| `/` | `index.html` | 랜딩 |
| `/terms/` | `terms/index.html` | 이용약관 |
| `/privacy/` | `privacy/index.html` | 개인정보 처리방침 (Play Console · 구글 로그인 처리방침 URL) |
| `/delete-account/` | `delete-account/index.html` | 계정 삭제 안내 (Play Console 계정 삭제 URL) |

- 빌드 없는 정적 사이트입니다. Vercel에 레포를 연결하면 `main`에 올릴 때마다 자동 배포됩니다.
- 디자인 원본: Figma `oTlJMBe8mjJnt4gr9tG2h2` — PC 밝은 버전(`13:122`), 폰 360(`35:222`). 768px 미만은 폰 시안 값을 씁니다.
- 글꼴: Pretendard Variable (jsDelivr CDN)

## 약관·처리방침 문구 고치기

HTML을 직접 고치지 말고 `content/*.txt` 를 고친 뒤 아래를 실행하세요.

```
py tools/build_legal.py
```

줄 형식은 `content/privacy.txt` 맨 위 설명에 있습니다. (`H|` 조 제목, `HANG|①|` 항, `HO|1.|` 호, `**굵게**`, `[글자](/주소/)`)

## 로컬에서 보기

```
py -m http.server 8765
```

브라우저에서 http://localhost:8765 를 엽니다.
