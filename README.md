# Pin Local · Skin Blur

Windows x64용 Premiere Pro 26 플러그인입니다. 두 제품은 각각 설치하고 업데이트합니다.

| 제품 | 기능 | 설치 파일 |
|---|---|---|
| Pin Local 0.2.1 | 모션 추적 · 피사체 고정 · 컷별 효과와 키프레임 저장 | [Pin 설치](https://github.com/contentriumkorea/local-studio-plugins/releases/download/pin-v0.2.1/PinLocal-0.2.1-Setup.zip) |
| Skin Blur 0.2.1 | 얼굴 검출 · 피부 스무딩 · 잡티/밝기/톤 · 얼굴형 보정 | [Skin Blur 설치](https://github.com/contentriumkorea/local-studio-plugins/releases/download/skin-blur-v0.2.1/SkinBlur-0.2.1-Setup.zip) |

## 설치

1. 사용할 제품의 **Setup.zip**을 다운로드하고 압축을 풉니다.
2. 안에 있는 Setup.exe를 실행합니다. Windows.zip과 update.json은 같은 폴더에 둡니다.
3. Adobe 앱의 작업을 저장하고 종료한 다음 **설치**를 누르고 Windows 관리자 승인을 진행합니다.
4. Premiere를 다시 실행하고 **창 → 확장 프로그램 → Pin Local / Skin Blur**를 엽니다.

Python과 얼굴 모델이 포함되어 별도 다운로드나 API 키가 필요 없습니다. 설치 후 다운로드한 ZIP은 보관할 필요가 없습니다.

## 업데이트

패널의 **업데이트 확인** 또는 효과 컨트롤의 **Update → Check for Updates**를 누릅니다. 다운로드한 후 Adobe 앱을 종료하고 설치합니다. 업데이트 정보의 RSA 서명과 설치 파일의 SHA-256을 검증합니다.

Skin Blur는 기존 Glam Local의 이름을 변경한 제품입니다. 기존 프로젝트의 효과 식별자와 설정, 설치 위치를 유지합니다. 기존 0.2.0 업데이트 앱을 위한 호환 피드와 파일도 제공하며, 새 사용자용 설치 파일과 화면에는 Skin Blur 이름을 사용합니다.

## Pin Local 사용법

1. 기준 프레임에서 원본 영상과 대상 이미지/그래픽을 선택합니다. 영상 하나만 선택하면 피사체 고정 모드입니다.
2. **선택 클립 읽기 → 핀 지정 → 추적 시작 → 적용** 순서로 진행합니다.
3. 컷마다 별도의 **Pin Local** 효과와 키프레임이 프로젝트에 저장됩니다. 다른 컷을 작업하거나 프로젝트를 다시 열어도 적용 결과가 유지됩니다.
4. 패널의 **컷별 추적 작업**에서 이전 항목을 엽니다. 추적 캐시는 이 PC에 저장되며, 이미 적용된 키프레임의 렌더링에는 필요하지 않습니다.

속도 100%, CFR, 정방 픽셀, 원본 파일이 있는 일반 비디오를 사용하세요. 중첩/멀티캠은 안쪽 원본에서 작업합니다. 기존 Motion 애니메이션, 속도 변경, 재해석, VFR은 지원 범위 밖입니다. 추적은 원본 파일 기준이므로 다른 효과가 바꾼 화면은 반영하지 않습니다. 원본 레이어 밖은 투명해집니다.

## Skin Blur 사용법

클립 선택 후 **선택 클립에 Skin Blur 추가**를 누르고 효과 컨트롤에서 조절합니다. 기본값 0은 원본입니다.

| 컨트롤 | 기능 |
|---|---|
| Skin Smoothing / Blemish Reduction | 피부결 / 잡티 완화 |
| Skin Brightening / Skin Tone | 밝기 / 차갑게·따뜻하게 |
| Face Slim / V Line | 얼굴 폭 / 턱선 |
| Eye Size / Nose Narrow | 눈 크기 / 코 폭 |
| Mouth Size / Smile | 입 크기 / 미소 |
| Show Skin Mask / Show Face Points | 보정 범위 / 검출점 확인 |

최대 4명에게 같은 값을 적용하며 얼굴 선택 기능은 없습니다. 얼굴을 찾지 못한 프레임은 원본을 유지합니다. 빠른 움직임이나 가림에서 검출이 흔들릴 수 있습니다.

### 프리뷰가 느릴 때

- 프로그램 모니터의 **재생 해상도를 1/4**로 낮춥니다.
- 끊기는 구간에 인/아웃을 설정하고 **시퀀스 → 인/아웃 렌더링**으로 프리뷰를 만듭니다.
- 프리뷰 해상도를 낮춰도 최종 내보내기는 원본 해상도로 처리됩니다.

0.2.1은 공유 메모리 프레임 전달과 BGRA 검출 경로를 최적화했습니다. 로컬의 동일 3840×2160 프레임에서 초기 모델 로딩을 제외한 반복 처리 중앙값은 219ms → 117ms였습니다. 이는 네이티브 효과와 처리 엔진 왕복 측정이며, Premiere 타임라인의 실제 재생 fps 측정은 아닙니다. CPU 처리이므로 **4K 전체 해상도 실시간 재생은 보장하지 않습니다.** 첫 적용에는 모델 로딩 시간이 추가됩니다.

## 지원 범위와 검증

- Windows x64 · Premiere Pro 26 · CPU · SDR 8비트. GPU 가속과 HDR/16·32비트 처리는 포함하지 않습니다.
- Pin 0.2.1: Premiere 26.5.2에서 실제 추적·적용·프로젝트 재열기·다른 컷 유지·PNG 렌더 검증.
- Skin Blur 0.2.1: 네이티브 DLL과 실제 얼굴 검출 엔진 왕복, 해상도/설정 변경, 원본·배경·알파 보존 검증. 이름 변경과 성능 수정 후 Premiere의 설치·재생 검증은 별도입니다.
- 다른 Premiere 버전, After Effects, macOS는 검증하지 않았습니다.

영상은 이 PC에서만 처리합니다. 설치 위치는 Program Files/LocalStudio/PinLocal 및 기존 호환 경로 Program Files/LocalStudio/GlamLocal입니다. 사용자 데이터는 LocalAppData/LocalStudio 아래에 저장됩니다.

이 저장소는 설치 파일과 서명된 업데이트 배포용입니다. 제3자 구성요소의 라이선스는 패키지 안의 THIRD_PARTY_NOTICES.md와 각 런타임 라이선스를 확인하세요.
