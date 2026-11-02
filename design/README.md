# 인터베리알파 홈 시안 (Clinical-clean)

열기: `cd design && python -m http.server 8765 --bind 127.0.0.1` → http://127.0.0.1:8765/?v=a1 (또는 `?v=a2`). 오른쪽 아래 스위치로도 전환됩니다.

## A-1 vs A-2 (내용·구성은 같고 녹색 면적만 다름)
| 영역 | A-1 그린 앵커형 (추천) | A-2 화이트 포인트형 |
|---|---|---|
| 히어로 | #00644E 전면 배경, 흰 제목, 흰 버튼 | 흰 배경, 녹색 제목·녹색 버튼 |
| 근거 수치 | 녹색 밴드 + 흰 숫자 | 흰 배경 + 녹색 숫자·녹색 상단선 |
| 나머지 | 흰색/#F4F7F6 교차, 녹색은 제목·숫자·CTA | 동일 |

## [Wix 에디터]에서 바꿀 것
- 사이트 디자인 > 글꼴: 제목 Paperlogy 7 Bold(소제목 6 SemiBold), 본문 Pretendard. 업로드 폰트로 등록 후 avenir/나눔/돋움/lulo 전부 교체
- 사이트 디자인 > 색상: 주색 #00644E, 진한색 #004D3C, 본문 #1A2B26, 보조 #4A5A55, 회색 면 #F4F7F6, 선 #D5DED9. 분홍 계열 삭제
- 헤더: 스크롤 효과 "고정(항상 표시)", 흰 배경, 메뉴 글자 17px·#1A2B26
- 섹션 배경: A-1은 히어로·근거 수치 섹션만 #00644E, 나머지 흰색/#F4F7F6
- 히어로 제품 이미지: 기존 패키지 이미지(인터베리알파산.png) 사용, 지연 로드 끄기
- 4분할 배너·Check Point 인용부호 블록은 근거 수치 섹션으로 대체

## 임베드 코드로 넣을 것
- 근거 수치 카운트업(IntersectionObserver), 승인·출시 타임라인 — `index.html`의 해당 섹션을 HTML 상자로 분리 가능
- 나머지(텍스트·버튼·카드)는 에디터 기본 요소로 구현 권장

## 레퍼런스
- Lazyweb Agentic Search: https://www.lazyweb.com/agentic-search/860219be-8dec-4f81-bc7f-f4a2ddd7c530
- Ritual (https://ritual.com): 확인 필요 (접속 차단 429)
- Elysium Health (https://www.elysiumhealth.com): 확인 필요 (접속 차단 429)
- FidoCure (https://www.fidocure.com): "수의사가 등록해야 하며 직접 처방하지 않는다"는 고지와 Nature 등 게재 논문 링크로 근거를 보여주는 방식
- Chewy Pharmacy (https://www.chewy.com/app/content/pharmacy): 확인 필요 (접속 차단 429)
- Modern Animal (https://www.modernanimal.com): 히어로의 "Find a nearby clinic" + 도시별 병원 목록(주소·예약·상세) 구성 → 입점 동물병원 찾기 참고
- Lemonade Pet (https://www.lemonade.com/pet): 진료비 청구를 3단계(병원 결제→앱 청구→입금)로 짧게 설명하는 방식 → 사용 방법 섹션 참고
