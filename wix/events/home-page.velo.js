// 홈 페이지 코드: 진행 중인 '팝업 노출' 이벤트가 있으면 1.5초 뒤 팝업을 연다. 오늘 하루 보지 않기를 누른 날은 안 연다.
import wixWindowFrontend from 'wix-window-frontend';
import wixData from 'wix-data';
import wixLocationFrontend from 'wix-location-frontend';
import { local } from 'wix-storage-frontend';
import { COLLECTION, POPUP, popupItems, today } from 'public/events.js';

$w.onReady(async () => {
  if (wixLocationFrontend.query.utm_source === 'video') return;  // 영상 유입은 팝업 없이 바로 본문
  if (local.getItem('ibPopupHidden') === today()) return;
  const { items } = await wixData.query(COLLECTION).eq('showPopup', true).limit(50).find();
  const live = popupItems(items);
  if (!live.length) return;
  setTimeout(() => wixWindowFrontend.openLightbox(POPUP, { items: live }), 1500);
});
