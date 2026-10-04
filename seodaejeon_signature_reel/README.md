# 서대전 상떼빌 시그니처 — 15초 브랜드 쇼릴

`seodaejeon_signature_reel.mp4` — 1920×1080, 30fps, 15초, H.264 + AAC 320k, -13.4 LUFS
(60fps로 렌더링한 뒤 2프레임 블렌딩으로 모션블러를 넣어 30fps로 출력)

## 구성 — 음악의 실제 타격 시점에 맞춘 편집
| 시간 | 장면 |
|---|---|
| 0.07 / 0.56 / 1.05s | 저음 타격 3발에 맞춰 "도시의 / 높이를, / 다시 쓰다"를 한 단어씩 배치. 컷마다 배경 이미지 전환 |
| 2.66 / 3.16 / 3.65s | THE → NEW → *Signature*. 줌블러 라이저 후 화이트아웃 |
| 3.97s (드롭) | 히어로 컷 줌아웃 + 2.5D 시차. 거대한 SIGNATURE 글자가 **타워 뒤로** 지나감 |
| 5.92s | 타워 틸트업 + 층수 카운터 01→47 "최고 47층" |
| 7.86s | 3분할 패널이 펄스마다 슬라이드 인 → "총 508호 / 아파트 324세대 + 오피스텔 184실" |
| 9.81s | 휩 팬 → 트램 트래킹 샷 "도시철도 2호선 트램(예정) · 서대전역 인근" → 10.78s 위치 핀 "대전 중구 유천동" |
| 11.76s | 로고 락업 "10년 장기일반민간임대 주상복합 / 서대전 상떼빌 시그니처" |
| 13.70s | 음악 컷 + 최종 임팩트, 골드 샤인, 파티클, 고지 문구 |

## 제작 방식
- 첨부 이미지를 EDSR ×2 AI 업스케일(`up.py`). 타워 3개를 분리하고 배경을 인페인팅해(`layers.py`) 시차·텍스트 비하인드 효과에 사용
- `reel.html`: Canvas 2D 합성 + WebGL 후처리(색수차, 줌·방향 블러, 그레인, 비네트). `render.py`로 프레임 단위 결정적 렌더링
- `audio.py`: 음악 편집 + 효과음(라이저, 휙 소리, 임팩트, 잔향)을 모두 직접 합성

## 사용 소재와 라이선스
- 음악: "Release the Hybrids" — FreePD.com (Kevin MacLeod), **CC0 1.0**(상업적 이용 가능, 출처 표기 불필요). 원곡 68.70초부터 사용
- 폰트: Pretendard, Noto Serif KR, Playfair Display, Montserrat — 모두 SIL OFL 1.1
- 사실 정보 출처: 언론 보도(국제뉴스 "대전 유천동에 47층 주거단지…'서대전 상떼빌 시그니처' 5일 홍보관 오픈")와 분양 홍보 페이지 검색 결과

## 다시 만들기
```
./get_assets.sh && pip install playwright opencv-contrib-python-headless librosa soundfile scipy
python3 up.py && python3 layers.py src.png && python3 layers.py src_x2.png _x2
HI=1 python3 render.py video 60 v60.mp4
python3 audio.py "freepd/Epic/Release the Hybrids.mp3"   # -> mix_pre.wav (이후 -14 LUFS로 볼륨 조정)
ffmpeg -i v60.mp4 -i mix.wav -filter_complex "[0:v]tmix=frames=2,fps=30[v]" -map "[v]" -map 1:a ... reel.mp4
```
