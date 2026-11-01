// 이벤트 목록(/events) 페이지 코드: 진행 중 → 예정 → 종료 순 카드. 종료된 것도 기록으로 남긴다.
import wixData from 'wix-data';
import { COLLECTION, listItems, period, eventUrl } from 'public/events.js';

const LABEL = { live: '진행 중', soon: '예정', ended: '종료' };

$w.onReady(async () => {
  const { items } = await wixData.query(COLLECTION).limit(100).find();
  const rows = listItems(items);

  $w('#eventRepeater').onItemReady(($item, ev) => {
    // 이미지 없으면 Wix 기본 이미지 대신 칸을 접는다
    if (ev.image) { $item('#evImage').src = ev.image; $item('#evImage').expand(); }
    else $item('#evImage').collapse();
    $item('#evTitle').text = ev.title || '';
    $item('#evPeriod').text = period(ev);
    $item('#evStatus').text = LABEL[ev._status];
    $item('#evButton').link = eventUrl(ev);
    $item('#evImage').link = eventUrl(ev);
  });
  $w('#eventRepeater').data = rows;

  // 리피터는 에디터에서 '로드 시 숨김'으로 두고, 데이터가 채워진 뒤 페이드로 보인다
  if (rows.length) {
    $w('#eventRepeater').show('fade', { duration: 200 });
  } else {
    $w('#eventRepeater').collapse();
    $w('#evEmpty').expand();
  }
});
