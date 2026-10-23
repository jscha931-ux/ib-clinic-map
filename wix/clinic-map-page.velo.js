// Wix 입점병원 지도 페이지 코드 (Velo). 페이지 코드 창 내용을 통째로 이것으로 바꾼다.
// '#html1' 은 지도 HTML 임베드의 ID. 편집기에서 ID 가 다르면 아래 한 곳만 바꾼다.
import wixWindowFrontend from 'wix-window-frontend';

const DATA = { dataUrl: 'https://jscha931-ux.github.io/ib-clinic-map/clinics.json', center: [37.5, 127.0] };

$w.onReady(() => {
  const map = $w('#html1');
  map.postMessage(DATA);  // 지도가 먼저 로드됐으면 이걸로, 아니면 아래 ibReady 응답으로 받는다

  map.onMessage(async (event) => {
    const msg = event.data || {};
    if (msg.type === 'ibReady') {
      map.postMessage(DATA);
    } else if (msg.type === 'ibLocate') {
      // 임베드(iframe)는 위치 권한이 없어 페이지에서 받아 넘긴다. 위치 꺼진 브라우저는 응답이 없을 수 있어 15초 제한.
      try {
        const pos = await Promise.race([
          wixWindowFrontend.getCurrentGeolocation(),
          new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 15000)),
        ]);
        map.postMessage({ type: 'ibMyLoc', lat: pos.coords.latitude, lng: pos.coords.longitude });
      } catch (e) {
        map.postMessage({ type: 'ibLocErr' });
      }
    }
  });
});
