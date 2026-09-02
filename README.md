# 인터베리알파 입점병원 지도 데이터

`interberry.gcvp.co.kr/clinic-map` 이 읽는 `clinics.json` 을 만드는 스크립트.

## 실행

```bash
python build_clinics.py --dry-run                       # 현황만 집계
python build_clinics.py --provider vworld --key <KEY>   # 신규분 지오코딩 + 생성
git add -A && git commit -m "병원 목록 갱신" && git push  # 사이트 반영 (최대 10분)
```

`--provider` 는 `vworld`(기본) / `google` / `kakao`. 키는 `GEO_KEY` 환경변수로도 됩니다.

## 동작

| 단계 | 원천 |
|---|---|
| 구매 거래처 | `Report 2026 V3` / `Master` — `Index=Actual`, `M_Code=9174001` |
| 거래처명 | `Report 2026 V3` / `Ckey` |
| 주소 | `동물병원 주소 뽑기.xlsx` / `C2*` 시트 (SAP BP 마스터) |
| 좌표 | `geocache.json` — 없는 주소만 API 호출 |

기준은 **전체 구매 이력**(현재 1,031곳). 최근 N개월로 좁히려면 `load_buyers()` 가 돌려주는
최종구매일로 필터하면 됩니다.

## 사이트 연결

Wix Velo 코드가 아래 URL 을 fetch 합니다. **한 번 설정한 뒤로는 Wix 를 건드릴 일이 없습니다.**

```js
$w.onReady(() => {
  $w('#html1').postMessage({
    dataUrl: 'https://jscha931-ux.github.io/ib-clinic-map/clinics.json',
    center: [37.5, 127.0]
  });
});
```

## 주기적으로 해야 할 것

- **분기 1회: `C2` 주소 마스터 갱신.** SAP 에서 BP 마스터를 새로 받아
  `동물병원 주소 뽑기.xlsx` 의 `C2(...)` 시트를 교체. 시트명이 바뀌어도 `C2` 로 시작하면 자동 인식.
  이걸 안 하면 신규 개설 병원이 계속 `주소없음` 으로 빠집니다.
- 매 실행 후 `unmatched.csv` 확인 (주소없음 / 지오코딩실패). 공개 저장소에는 올라가지 않습니다.

## 미포함

당월 온그린몰 매출은 반영하지 않습니다. V3 갱신 주기(월 1회)면 지도에는 충분해서 뺐습니다.
필요해지면 `IBA KPI Tracker` 의 `ongreen_download.py` 를 붙이면 됩니다.
