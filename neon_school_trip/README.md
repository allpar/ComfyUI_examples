# 수학여행 안전 안내 — 네온사인 모션그래픽

- `neon_safety.mp4` — 1920×1080, 30fps, 15초, H.264 + AAC
- 다크 벽돌 벽 + 핑크·청록·옐로 네온. 글자는 16분음표 박자에 맞춰 몇 번 깜빡인 뒤 정박에 켜지고, 벽에 색이 번집니다. 네온 밝기·벽 반사·카메라 줌이 킥마다 펄스합니다.

## 구성 (124 BPM, 1비트 = 0.484초)
| 시간 | 내용 |
|---|---|
| 0–3.6s | 타이틀 "SCHOOL TRIP / 수학여행 / 안전 안내" — 1.94s 드롭에 맞춰 점등 |
| 3.9–6.5s | 10월 1일(목) · 08:00 · 학교 집합 |
| 6.8–11.4s | 안전 약속 3가지: ① 혼자 다니지 않기 ② 버스에선 안전벨트 ③ 다치면 바로 알리기 |
| 11.6–15s | "안전한 수학여행을 위하여" |

## 음악
"Electronic L Discoed" — FreePD.com (Kevin MacLeod), **CC0 1.0 퍼블릭 도메인**: 상업적 이용 가능, 출처 표기 불필요.
GitHub 미러 https://github.com/0lhi/FreePD (`Zoned/Electronic L Discoed.mp3`)에서 받았으며, 원곡 2.588초 지점부터 15초를 사용합니다(4번째 비트에 드롭).

## 폰트
Jua, Monoton (Google Fonts, SIL OFL 1.1) — `fonts/`

## 다시 렌더링
```
pip install playwright
CHROME_PATH=/path/to/chrome python3 render.py video   # -> video_noaudio.mp4
ffmpeg -i video_noaudio.mp4 -ss 2.5878 -t 15 -i "Electronic L Discoed.mp3" -map 0:v -map 1:a -c:v copy \
  -af "afade=t=in:d=0.05,afade=t=out:st=13.9:d=1.1" -c:a aac -b:a 256k -shortest neon_safety.mp4
```
