# Audio Verification Queue

> 회사에서는 소리를 들을 수 없으므로, 오디오 출력이 필요한 검증은 모두 여기 쌓아두고
> 집에서 일괄 확인한다. 검증 완료 항목은 ✅ 표시 후 `AUDIO_VERIFIED.md`로 archive.

---

## Pending

### [PENDING] Hello Audio (Session 1 + Gemini Layer 2 fixes)

- **Commit**: `cfc353a` (scaffold) + fix commit (Layer 2 반영)
- **Date queued**: 2026-05-19
- **빌드 상태**: ✅ 회사 PC에서 컴파일 성공 (Aria.exe 24.54MB)
- **회사 빌드 환경**: VS 2022 Community + C++ Desktop 워크로드, MSVC 19.44, CMake 3.31.6, Windows 11
- **CI 검증**: ✅ GitHub Actions Windows 빌드 통과 (Layer 4)
- **Layer 2 적용**: Gemini 3 Pro 정적 검토 + 권장사항 3건 모두 반영 → `VERIFICATION.md` 참고
  - MidiBuffer 멤버 변수화 → audio thread 힙 할당 제거 → dropout 위험 ↓
  - setCurrentPlaybackSampleRate override → ADSR 한 번만 초기화
  - Phase wrap-around → double 정밀도 보호
- **청취 시 추가 확인 항목** (Gemini 수정 반영 검증):
  - 노트 dropout/끊김 없는가? (MidiBuffer 멤버 변수화 효과)
  - 첫 노트 입력 시 즉시 사운드 나오는가? (ADSR sample rate 초기화 시점 변경 후)
- **빌드 명령**:
  ```powershell
  cmake -B build -G "Visual Studio 17 2022" -A x64
  cmake --build build --config Debug
  .\build\Aria_artefacts\Debug\Aria.exe
  ```
- **확인 사항**:
  1. 앱 실행 시 가상 키보드가 보이는가? (창 크기 900x320)
  2. 키보드 클릭 시 사인파 톤이 들리는가?
  3. 여러 노트 동시 누름이 가능한가? (폴리포니 8보이스)
  4. 노트 릴리즈 시 ADSR 디케이가 부드러운가? (뚝 끊기지 않음)
  5. 클릭 노이즈 없는가? (앞/끝)
- **예상 결과**: 사인파 폴리신디 정상 동작, 클릭 노이즈 없음
- **이슈 발생 시 의심 지점**:
  - `level = velocity * 0.25f` — 너무 조용/시끄러우면 조정
  - ADSR attack `0.01f` — 너무 짧으면 클릭 발생 가능
  - `setAudioChannels(0, 2)` — 출력 채널 잘못되면 무음

---

## Verified

(없음)
