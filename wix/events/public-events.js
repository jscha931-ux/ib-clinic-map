// 이벤트 CMS 공통 로직. Wix 에서는 public/events.js 로 만든다. 홈 팝업·이벤트 목록이 같이 쓴다.
export const COLLECTION = 'Events';   // CMS 컬렉션 ID
export const LIST_URL = '/events';    // 이벤트 목록 페이지 주소
export const POPUP = 'EventPopup';    // 팝업 이름(설정 > 이름)

// CMS 날짜는 Date 객체(날짜+시간 필드) 또는 'YYYY-MM-DD' 문자열(날짜 필드)로 온다 → 한국 날짜 'YYYY-MM-DD'
export function ymd(v) {
  if (!v) return '';
  if (typeof v === 'string') return v.slice(0, 10);
  return new Date(v.getTime() + 9 * 3600e3).toISOString().slice(0, 10);
}

export function today(now = new Date()) {
  return ymd(now);
}

// 'soon' 예정 / 'live' 진행 중 / 'ended' 종료. 시작·종료일은 그날 포함, 비어 있으면 제한 없음.
export function status(ev, now = new Date()) {
  const t = today(now), s = ymd(ev.startDate), e = ymd(ev.endDate);
  if (s && t < s) return 'soon';
  if (e && t > e) return 'ended';
  return 'live';
}

export function period(ev) {
  const f = v => ymd(v).replace(/-/g, '.');
  const s = f(ev.startDate), e = f(ev.endDate);
  return s && e ? `${s} ~ ${e}` : s ? `${s} ~` : e ? `~ ${e}` : '';
}

// 상세(동적) 페이지 주소 규칙을 /event/{slug} 로 설정해 둔다
export function eventUrl(ev) {
  return '/event/' + ev.slug;
}

// 팝업 대상: '팝업 노출' 체크 + 진행 중, 최근 시작 순
export function popupItems(items, now = new Date()) {
  return items.filter(ev => ev.showPopup && status(ev, now) === 'live')
    .sort((a, b) => ymd(b.startDate).localeCompare(ymd(a.startDate)));
}

// 목록: 진행 중 → 예정 → 종료, 각 묶음 안에서는 최근 시작 순
export function listItems(items, now = new Date()) {
  const order = { live: 0, soon: 1, ended: 2 };
  return items.map(ev => ({ ...ev, _status: status(ev, now) }))
    .sort((a, b) => order[a._status] - order[b._status]
      || ymd(b.startDate).localeCompare(ymd(a.startDate)));
}
