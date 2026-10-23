# Pin Local · Skin Blur

Premiere Pro에서 움직임을 따라가는 글자·이미지와 얼굴·피부 보정을 만드는 Windows용 플러그인입니다.

## 다운로드 · 설치

- **[Pin Local 경량 설치프로그램](https://github.com/contentriumkorea/local-studio-plugins/releases/download/pin-v0.2.5/PinLocalSetup.exe)** — 실행할 때 최신 정식 버전을 내려받습니다.
- [Pin Local 0.2.5 오프라인 설치](https://github.com/contentriumkorea/local-studio-plugins/releases/download/pin-v0.2.5/PinLocal-0.2.5-Setup.zip)
- **[SkinVeil (Skin Blur) 설치프로그램](https://github.com/contentriumkorea/local-studio-plugins/releases/download/skin-blur-v0.2.3/SkinBlurSetup.exe)**
- [SkinVeil 0.2.3 오프라인 설치](https://github.com/contentriumkorea/local-studio-plugins/releases/download/skin-blur-v0.2.3/SkinBlur-0.2.3-Setup.zip)

설치프로그램 실행 → 다운로드·파일 검증 → Adobe 작업 저장 및 앱 종료 → 설치·Windows 관리자 승인 → Premiere 재실행 → **창 → 확장 프로그램**에서 제품을 엽니다.

오프라인 ZIP은 압축을 풀고 안의 세 파일을 함께 둔 채 Setup.exe를 실행하세요. 설치 후 다운로드 ZIP은 보관할 필요가 없습니다.

## Pin Local 사용

1. 타임라인에서 원본 영상 컷만 선택하고 **선택 컷 불러오기**를 누릅니다.
2. **따라갈 이미지·그래픽**에서 같은 시간대의 글자·이미지를 선택합니다. 원본을 고정하려면 **피사체 고정**을 사용합니다.
3. 기준 프레임에 핀을 1개 또는 2개 지정하고 **추적 시작**을 누릅니다.
4. 추적·주변 영역 복구·가림 추정·미해결 프레임을 확인한 뒤 적용합니다. **복구·추정 구간 보기**로 확인할 구간으로 이동할 수 있습니다.
5. 결과는 각 컷의 Pin Local 효과와 키프레임으로 저장됩니다. 다른 컷을 작업해도 유지됩니다.

### 0.2.5 변경 사항

고개를 돌려 작은 핀의 무늬가 사라지면 주변 영역의 움직임으로 복구합니다. 이 결과는 정확한 표면 점의 재관측과 구분해 **주변 영역 복구**로 표시하며, 적용 전에 재생 확인이 필요합니다. 다른 물체로 갑자기 옮겨가거나 외형 연속성을 확인할 수 없는 프레임은 관측 결과로 사용하지 않습니다.

가림 뒤에는 계속 같은 피사체를 찾고, 다시 찾은 전후 사이의 빈 구간만 **가림 추정**으로 연결합니다. 끝내 찾지 못한 끝부분은 성공으로 채우지 않습니다. 필요한 구간은 핀을 다시 지정해 이어 추적할 수 있습니다.

업데이트가 기존의 짧은 키프레임을 자동으로 연장하지는 않습니다. **업데이트 후 해당 컷을 다시 추적하고 적용하세요.** 모든 영상의 복구를 보장하지 않으며, Premiere 실사용 확인은 사용자가 진행합니다.

## SkinVeil (Skin Blur) 사용

클립 선택 → **선택 클립에 SkinVeil 추가** → 효과 컨트롤에서 피부결·잡티·밝기·톤·얼굴형 등을 조절합니다. 기본 0은 원본입니다. 최대 4명에게 같은 값이 적용됩니다. 얼굴 미검출 프레임은 원본을 유지합니다.

0.2.3은 큰 얼굴 한 명에게만 보정되고 옆의 작은 얼굴이 누락되던 문제를 수정했습니다. 서로 크기가 다른 2·3·4명의 얼굴 검출과 각 얼굴의 피부 블러·밝기 보정을 로컬 엔진 및 배포 DLL→worker에서 확인했습니다. 최대 4명에게 같은 값이 적용되며 작은 얼굴·옆얼굴·가림에서는 검출이 제한될 수 있습니다.

현재 표시명은 SkinVeil입니다. 기존 Skin Blur·Glam Local 프로젝트의 효과와 설정, 설치 위치와 업데이트는 호환됩니다.

## 업데이트

패널의 **업데이트 확인** 또는 효과 컨트롤의 **Update → Check for Updates**에서 진행합니다. 설치할 파일을 검증한 뒤 교체하며, 기존 프로젝트의 키프레임과 설정을 유지합니다.

## 지원 범위

Windows x64 · Premiere Pro 26 · SDR 8비트. Pin은 속도 100%, 정방 픽셀, 일정한 프레임레이트의 원본 영상을 사용합니다. 중첩·멀티캠은 안쪽 원본에서 작업하세요. 속도 변경·기존 Motion 애니메이션은 지원하지 않습니다.

4K 전체 해상도의 실시간 재생은 보장하지 않습니다. 프리뷰가 느리면 재생 해상도를 1/4로 낮추거나 인/아웃 렌더링을 사용하세요. 다른 Premiere 버전·After Effects·macOS는 검증하지 않았습니다.

영상은 이 PC에서만 처리합니다. 포함된 구성요소의 라이선스와 저작권 고지는 패키지의 THIRD_PARTY_NOTICES.md에 유지합니다.


[![콘텐츠리움 홈페이지](https://img.shields.io/badge/콘텐츠리움-홈페이지-222222)](https://contentrium.com/)
