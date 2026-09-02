# -*- coding: utf-8 -*-
"""인터베리알파 구매 거래처 -> 지오코딩 -> clinics.json

원천:
  1) Report 2026 V3 / Master  (Index=Actual, M_Code=9174001) -> 구매 C_code
  2) Report 2026 V3 / Ckey                                   -> 거래처명
  3) 동물병원 주소 뽑기.xlsx / C2* 시트 (SAP BP 마스터)       -> 주소
지오코딩은 geocache.json 에 영구 캐시. 신규 주소만 카카오 로컬 API 호출.
"""
import argparse, glob, json, os, re, shutil, sys, tempfile, time, urllib.parse, urllib.request

import openpyxl

DESKTOP = r"C:\Users\Owner\OneDrive - GREENCROSS VETERINARY PRODUCTS CO.,LTD\바탕 화면"
V3_GLOB = os.path.join(DESKTOP, r"MKT\CA 영업부", "2) Report 2026 V3*.xlsx")
BRAND = os.path.join(DESKTOP, r"MKT\CA 제품\인터베리알파\브랜드 페이지")
ADDR_XLSX = os.path.join(BRAND, "동물병원 주소 뽑기.xlsx")
LEGACY_JSON = os.path.join(BRAND, "clinics.json")

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "geocache.json")
OUT = os.path.join(HERE, "docs", "clinics.json")
UNMATCHED = os.path.join(HERE, "unmatched.csv")

IBA_MCODE = 9174001
KR_BOUNDS = (33.0, 39.7, 124.5, 132.1)  # lat_min, lat_max, lng_min, lng_max


def norm_addr(s):
    """캐시 키. 잉여 공백만 눌러 같은 주소가 두 번 지오코딩되지 않게."""
    if not s:
        return ""
    return re.sub(r"\s+", " ", str(s)).strip()


def open_locked(path):
    """OneDrive/Excel 로 잠긴 파일은 임시 복사본으로 연다."""
    try:
        return openpyxl.load_workbook(path, read_only=True, data_only=True), None
    except PermissionError:
        tmp = os.path.join(tempfile.gettempdir(), "ibcm_" + os.path.basename(path))
        shutil.copy2(path, tmp)
        return openpyxl.load_workbook(tmp, read_only=True, data_only=True), tmp


def header_index(ws):
    hdr = next(ws.iter_rows(max_row=1, values_only=True))
    return {h: i for i, h in enumerate(hdr) if h}


def load_buyers():
    """V3 Master 에서 IBA 를 산 적 있는 C_code -> (거래처명, 최종구매일)"""
    src = sorted(glob.glob(V3_GLOB))[-1]
    print("[V3] " + os.path.basename(src))
    wb, tmp = open_locked(src)
    try:
        ws = wb["Master"]
        i = header_index(ws)
        buyers = {}
        for r in ws.iter_rows(min_row=2, values_only=True):
            if r[i["Index"]] != "Actual" or r[i["M_Code"]] != IBA_MCODE:
                continue
            code = r[i["C_Code"]]
            if not code:
                continue
            d = r[i["Date"]]
            prev = buyers.get(code)
            if code not in buyers or (d and prev and d > prev) or (d and prev is None):
                buyers[code] = d

        ws = wb["Ckey"]
        i = header_index(ws)
        names = {}
        for r in ws.iter_rows(min_row=2, values_only=True):
            c = r[i.get("C_code", 0)]
            if c and c not in names:
                names[c] = r[i["Customer"]]
    finally:
        wb.close()
        if tmp and os.path.exists(tmp):
            os.remove(tmp)
    return {str(c): (names.get(c) or "", d) for c, d in buyers.items()}


def load_addresses():
    """SAP BP 마스터: C_code -> (주소, 전화)"""
    wb, tmp = open_locked(ADDR_XLSX)
    try:
        sheet = next(s for s in wb.sheetnames if s.startswith("C2"))
        print("[주소마스터] " + os.path.basename(ADDR_XLSX) + " / " + sheet)
        ws = wb[sheet]
        out = {}
        for r in ws.iter_rows(min_row=2, max_col=8, values_only=True):
            if not r[0]:
                continue
            addr = r[5] or r[6]  # F(청구처 주소) 우선, 없으면 G(납품처 주소)
            out[str(r[0]).strip()] = (norm_addr(addr), r[7] or "")
    finally:
        wb.close()
        if tmp and os.path.exists(tmp):
            os.remove(tmp)
    return out


def load_cache():
    cache = {}
    if os.path.exists(CACHE):
        cache = json.load(open(CACHE, encoding="utf-8"))
    # 최초 1회: 예전 clinics.json 좌표를 캐시로 흡수 (재지오코딩 방지)
    if not cache and os.path.exists(LEGACY_JSON):
        for c in json.load(open(LEGACY_JSON, encoding="utf-8")):
            a, lat, lng = norm_addr(c.get("address")), c.get("lat"), c.get("lng")
            if a and lat and lng:
                cache[a] = {"lat": float(lat), "lng": float(lng), "src": "legacy"}
        print("[캐시] 기존 clinics.json 에서 %d건 시드" % len(cache))
    return cache


def simplify_addr(addr):
    """상세주소(괄호, 층/호, 건물명)를 떼어 낸 축약 주소. 원문이 안 잡힐 때 재시도용."""
    s = re.sub(r"\([^)]*\)", " ", addr)          # (금호동,거북빌딩1층)
    s = re.split(r"[,.]", s)[0]                  # 쉼표/마침표 뒤 상세 제거
    s = re.sub(r"\s+\d+\s*(층|호)\b.*$", "", s)  # 남은 '1층', '104호'
    return norm_addr(s)


def _get_json(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)


def _q_kakao(addr, key):
    d = _get_json("https://dapi.kakao.com/v2/local/search/address.json?"
                  + urllib.parse.urlencode({"query": addr}),
                  {"Authorization": "KakaoAK " + key})
    docs = d.get("documents") or []
    return (float(docs[0]["y"]), float(docs[0]["x"])) if docs else None


def _q_google(addr, key):
    d = _get_json("https://maps.googleapis.com/maps/api/geocode/json?"
                  + urllib.parse.urlencode({"address": addr, "key": key,
                                            "region": "kr", "language": "ko"}))
    if d.get("status") == "REQUEST_DENIED":
        raise RuntimeError("Google: " + str(d.get("error_message")))
    res = d.get("results") or []
    if not res:
        return None
    loc = res[0]["geometry"]["location"]
    return (float(loc["lat"]), float(loc["lng"]))


def _q_vworld(addr, key):
    # VWorld 는 도로명(ROAD)/지번(PARCEL) 을 따로 물어야 한다.
    for kind in ("ROAD", "PARCEL"):
        d = _get_json("https://api.vworld.kr/req/address?"
                      + urllib.parse.urlencode({
                          "service": "address", "request": "getcoord", "version": "2.0",
                          "crs": "epsg:4326", "address": addr, "refine": "true",
                          "simple": "false", "format": "json", "type": kind, "key": key}))
        r = d.get("response") or {}
        if r.get("status") == "OK":
            p = r["result"]["point"]
            return (float(p["y"]), float(p["x"]))
        if r.get("status") == "ERROR":
            raise RuntimeError("VWorld: " + str(r.get("error")))
    return None


PROVIDERS = {"kakao": _q_kakao, "google": _q_google, "vworld": _q_vworld}


def geocode(addr, key, provider):
    """원문 -> 실패 시 축약 주소로 재시도. 한국 밖 좌표는 오지오코딩으로 간주해 버린다."""
    lo_lat, hi_lat, lo_lng, hi_lng = KR_BOUNDS
    fn = PROVIDERS[provider]
    for q, tag in ((addr, provider), (simplify_addr(addr), provider + "-short")):
        if not q or (tag.endswith("-short") and q == addr):
            continue
        hit = fn(q, key)
        if hit and lo_lat <= hit[0] <= hi_lat and lo_lng <= hit[1] <= hi_lng:
            return {"lat": hit[0], "lng": hit[1], "src": tag}
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", choices=sorted(PROVIDERS), default=os.environ.get("GEO_PROVIDER", "vworld"))
    ap.add_argument("--key", default=os.environ.get("GEO_KEY"), help="지오코딩 API 키")
    ap.add_argument("--dry-run", action="store_true", help="지오코딩 호출 없이 현황만 집계")
    a = ap.parse_args()

    buyers = load_buyers()
    addrs = load_addresses()
    cache = load_cache()

    clinics, no_addr, need = [], [], []
    for code, (name, last) in sorted(buyers.items()):
        addr, phone = addrs.get(code, ("", ""))
        if not addr:
            no_addr.append((code, name))
            continue
        if addr not in cache:
            need.append(addr)
        clinics.append({"code": code, "name": name, "address": addr, "phone": phone})

    print("\n구매 거래처 %d곳 | 주소 있음 %d | 주소 없음 %d | 지오코딩 필요 %d건"
          % (len(buyers), len(clinics), len(no_addr), len(set(need))))

    if need and not a.dry_run and not a.key:
        print("! API 키가 없어 신규 %d건은 건너뜁니다 (--key 또는 GEO_KEY)" % len(set(need)))
        need = []

    if need and not a.dry_run:
        todo = sorted(set(need))
        print("[지오코딩] %s / %d건" % (a.provider, len(todo)))
        for n, addr in enumerate(todo, 1):
            try:
                res = geocode(addr, a.key, a.provider)
            except Exception as e:
                res = None
                print("  ! %s -> %s" % (addr, e))
            if res:
                cache[addr] = res
            print("  [%d/%d] %s %s" % (n, len(todo), "OK  " if res else "FAIL", addr))
            time.sleep(0.05)
        json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    out, failed = [], []
    for c in clinics:
        hit = cache.get(c["address"])
        if not hit:
            failed.append(c)
            continue
        out.append({"id": str(len(out) + 1), "name": c["name"], "address": c["address"],
                    "phone": "", "lat": hit["lat"], "lng": hit["lng"]})

    prev = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else []
    if not a.dry_run:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        with open(UNMATCHED, "w", encoding="utf-8-sig") as f:
            f.write("사유,거래처코드,거래처명,주소\n")
            for code, name in no_addr:
                f.write("주소없음,%s,%s,\n" % (code, name))
            for c in failed:
                f.write("지오코딩실패,%s,%s,%s\n" % (c["code"], c["name"], c["address"]))

    print(">> clinics.json %d곳 (이전 %d곳, %+d)" % (len(out), len(prev), len(out) - len(prev)))
    print(">> 보완 필요 %d건 -> %s" % (len(no_addr) + len(failed), os.path.basename(UNMATCHED)))


def _selftest():
    assert norm_addr("  서울시   강남구  1 ") == "서울시 강남구 1"
    assert norm_addr(None) == ""
    assert simplify_addr("광주광역시 서구 금화로 54. 110(금호동,거북빌딩1층)") == "광주광역시 서구 금화로 54"
    assert simplify_addr("경기도 성남시 분당구 불곡로 4, 1층 104호(정자동, 리더스프라자)") == "경기도 성남시 분당구 불곡로 4"
    assert simplify_addr("서울특별시 광진구 광장동 517-5") == "서울특별시 광진구 광장동 517-5"
    lo_lat, hi_lat, lo_lng, hi_lng = KR_BOUNDS
    assert lo_lat <= 37.5 <= hi_lat and lo_lng <= 127.0 <= hi_lng  # 서울 = 통과
    assert not (lo_lat <= 40.7 <= hi_lat)  # 뉴욕 = 차단
    print("selftest ok")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _selftest()
    else:
        main()
