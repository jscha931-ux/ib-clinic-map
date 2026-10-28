// 이벤트 목록(/events) 페이지 코드: 진행 중 → 예정 → 종료 순 카드. 종료된 것도 기록으로 남긴다.
import wixData from 'wix-data';
import { COLLECTION, listItems, period, eventUrl } from 'public/events.js';

const LABEL = { live: '진행 중', soon: '예정', ended: '종료' };

$w.onReady(async () => {
  const { items } = await wixData.query(COLLECTION).limit(100).find();
  const rows = listItems(items);

  $w('#eventRepeater').onItemReady(($item, ev) => {
    if (ev.image) $item('#evImage').src = ev.image;
    $item('#evTitle').text = ev.title || '';
    $item('#evPeriod').text = period(ev);
    $item('#evStatus').text = LABEL[ev._status];
    $item('#evButton').link = eventUrl(ev);
    $item('#evImage').link = eventUrl(ev);
  });
  $w('#eventRepeater').data = rows;

  if (!rows.length) {
    $w('#eventRepeater').collapse();
    $w('#evEmpty').expand();
  }
});
