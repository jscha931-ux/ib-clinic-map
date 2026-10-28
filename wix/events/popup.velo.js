// 팝업(EventPopup) 코드: 가장 최근 이벤트 1건을 보여 주고, 여러 건이면 '모두 보기'로 목록에 연결한다.
import wixWindowFrontend from 'wix-window-frontend';
import wixLocationFrontend from 'wix-location-frontend';
import { local } from 'wix-storage-frontend';
import { LIST_URL, eventUrl, period, today } from 'public/events.js';

$w.onReady(() => {
  const { items = [] } = wixWindowFrontend.lightbox.getContext() || {};
  const ev = items[0];
  if (!ev) return wixWindowFrontend.lightbox.close();

  const go = url => { wixWindowFrontend.lightbox.close(); wixLocationFrontend.to(url); };

  if (ev.image) $w('#popImage').src = ev.image;
  $w('#popTitle').text = ev.title || '';
  $w('#popPeriod').text = period(ev);
  $w('#popImage').onClick(() => go(eventUrl(ev)));
  $w('#popGo').onClick(() => go(eventUrl(ev)));

  if (items.length > 1) {
    $w('#popAll').label = `진행 중인 이벤트 ${items.length}개 모두 보기`;
    $w('#popAll').onClick(() => go(LIST_URL));
  } else {
    $w('#popAll').collapse();
  }

  $w('#popHideToday').onClick(() => {
    local.setItem('ibPopupHidden', today());
    wixWindowFrontend.lightbox.close();
  });
  $w('#popClose').onClick(() => wixWindowFrontend.lightbox.close());
});
