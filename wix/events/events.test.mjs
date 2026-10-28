// node wix/events/events.test.mjs  — public-events.js 는 Velo(ESM) 문법이라 소스를 읽어 모듈로 불러온다
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';

const src = readFileSync(new URL('./public-events.js', import.meta.url), 'utf8');
const m = await import('data:text/javascript,' + encodeURIComponent(src));

const at = s => new Date(s);                     // 기준 시각
const NOW = at('2026-11-10T03:00:00Z');          // 한국 11/10 12시

// 날짜 형식 두 가지 + 한국 시간 자정 경계
assert.equal(m.ymd('2026-11-01'), '2026-11-01');
assert.equal(m.ymd(at('2026-11-09T15:30:00Z')), '2026-11-10');   // UTC 11/9 15:30 = 한국 11/10 00:30
assert.equal(m.ymd(null), '');

// 상태: 시작·종료일 당일 포함, 빈 날짜는 제한 없음
const ev = (s, e, x = {}) => ({ startDate: s, endDate: e, ...x });
assert.equal(m.status(ev('2026-11-10', '2026-11-30'), NOW), 'live');
assert.equal(m.status(ev('2026-11-01', '2026-11-10'), NOW), 'live');
assert.equal(m.status(ev('2026-11-11', '2026-11-30'), NOW), 'soon');
assert.equal(m.status(ev('2026-10-01', '2026-11-09'), NOW), 'ended');
assert.equal(m.status(ev(null, null), NOW), 'live');

assert.equal(m.period(ev('2026-11-01', '2026-11-30')), '2026.11.01 ~ 2026.11.30');
assert.equal(m.period(ev('2026-11-01', null)), '2026.11.01 ~');
assert.equal(m.eventUrl({ slug: 'webinar-1' }), '/event/webinar-1');

const items = [
  ev('2026-11-01', '2026-11-30', { title: 'A', showPopup: true }),
  ev('2026-11-05', '2026-11-30', { title: 'B', showPopup: true }),
  ev('2026-11-05', '2026-11-30', { title: 'C', showPopup: false }),
  ev('2026-11-20', '2026-11-30', { title: 'D', showPopup: true }),   // 예정
  ev('2026-10-01', '2026-10-31', { title: 'E', showPopup: true }),   // 종료
];
assert.deepEqual(m.popupItems(items, NOW).map(x => x.title), ['B', 'A']);
assert.deepEqual(m.listItems(items, NOW).map(x => x.title + x._status),
  ['Blive', 'Clive', 'Alive', 'Dsoon', 'Eended']);

console.log('events selftest ok');
