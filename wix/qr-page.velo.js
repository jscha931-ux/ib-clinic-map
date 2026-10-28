// /qr 페이지 코드: 영상 QR 진입용 빈 페이지. 홈으로 보내며 출처 표시(UTM)를 붙인다.
// 카메라에는 짧은 주소(interberry.gcvp.co.kr/qr)가 보이고, 이 페이지 조회수 = 영상 QR 스캔 수.
import wixLocationFrontend from 'wix-location-frontend';

$w.onReady(() => {
  wixLocationFrontend.to('/?utm_source=video&utm_medium=qr');
});
