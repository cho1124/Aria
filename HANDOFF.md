# Aria - Session Handoff

> 매 세션 끝에 갱신됨. 새 세션 시작 시 이 문서를 첫 번째로 읽고 작업 이어가기.

## 핸드오프 프로토콜 (Reference)

### Validation Stack (4계층)
1. **Build Gate** — 매 커밋, 컴파일 + (집) 실행 + 청취
2. **Codex Review** — 코드 단위, `/codex:rescue`로 C++/JUCE 특이사항
3. **Adversarial Triad** — 설계 갈림길, `/adversarial-verify`
4. **Web Verify** — API 의심 시 WebSearch/WebFetch

### Session Boundary Flow
```
세션 중 ─────────────────────────────────
  Claude 작업
  HANDOFF.md 실시간 갱신
세션 마감 신호 ──────────────────────────
  (컨텍스트 80% / /handoff / 자연 완료 / 에러 누적)
  1) Claude: HANDOFF.md 최종 정리
  2) Codex: 주장 vs 실제 파일 대조 → VERIFICATION.md
  3) Memory: project_aria.md 마지막 줄 commit hash 갱신
새 세션 ─────────────────────────────────
  MEMORY.md → project_aria.md → HANDOFF.md → VERIFICATION.md
```

### Audio Verification Split
- 회사: 컴파일 + 정적 검증 + git push까지
- 집: 실행 + 청취 + 회귀 테스트
- 큐: `AUDIO_VERIFICATION_QUEUE.md`

---

## Current Session

**Session**: 1 (환경 세팅)
**Date**: 2026-05-19
**Claude**: Opus 4.7 (1M context)
**Status**: 진행 중

### Goals
- [x] CMake + JUCE 8.0.12 환경 결정
- [x] Aria 폴더 생성 + git init
- [x] .gitignore 작성 (C++/CMake/VS/JUCE)
- [x] JUCE 8.0.12 submodule 추가 (shallow clone + tag fetch)
- [x] CMakeLists.txt 작성
- [x] src/ 디렉토리 + Hello Audio 최소 구현
- [x] 메모리 등록 (project_aria.md + MEMORY.md 인덱스)
- [x] **cmake configure 성공** (MSVC 19.44, 29.8s)
- [x] **Debug 빌드 컴파일 성공** (Aria.exe 24.54MB, JUCE 모듈 전체 빌드)
- [x] 첫 커밋 (`cfc353a`) + GitHub push
- [ ] **[집에서] 실행 + 청취 검증** → AUDIO_VERIFICATION_QUEUE 참고

### What Claude Claims to Have Done (Codex 검증 대상)

| 파일 | 주장 내용 | 검증 포인트 |
|---|---|---|
| `.gitignore` | C++/CMake/VS/JUCE 표준 패턴 | OK (검증 단순) |
| `CMakeLists.txt` | `juce_add_gui_app(Aria)` + 모듈 11개 링크 | `juce_generate_juce_header` 매크로명 정확? |
| `src/Main.cpp` | JUCE Application + DocumentWindow | `ProjectInfo::projectName` 매크로 존재? |
| `src/MainComponent.{h,cpp}` | AudioAppComponent + MidiKeyboardComponent + Synthesiser | `juce::Font(juce::FontOptions(...))` — JUCE 8 신규 API |
| `src/SineSynth.{h,cpp}` | SineSound + SineVoice + ADSR | `juce::ADSR` `juce::MidiMessage::getMidiNoteInHertz` 시그니처 |
| `External/JUCE` | submodule, tag 8.0.12, commit 29396c2 | 검증됨 (`git describe --tags` → 8.0.12) |

### Known Issues / 의심점 (모두 해소됨)

#### 환각 가능성 → 모두 빌드 통과로 검증됨
1. ✅ **JUCE 8 Font API**: `juce::Font(juce::FontOptions(20.0f, juce::Font::bold))` — 정상 컴파일.
2. ✅ **`juce_generate_juce_header(Aria)`**: CMake 매크로 존재 확인.
3. ✅ **`ProjectInfo::projectName`**: 매크로 정상 생성.

#### 환경 노이즈 (무시 가능)
- PowerShell 5.1에서 git/cmake가 NativeCommandError 던지지만 실제 동작은 정상 (CLAUDE.md 가이드라인 참고, exit code 0만 신뢰).
- cmake.exe가 PATH에 없음 → 절대 경로로 호출 중. `C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe`
- (선택) 향후 편의를 위해 PATH 추가 또는 VS Developer PowerShell 진입 고려.

### Next Steps (Session 2 시작 시)
1. **[집] 클론 + 빌드 + 실행**:
   ```powershell
   git clone --recurse-submodules https://github.com/cho1124/Aria.git
   cd Aria
   # VS 2022 + Desktop development with C++ 워크로드 필요
   cmake -B build -G "Visual Studio 17 2022" -A x64
   cmake --build build --config Debug
   .\build\Aria_artefacts\Debug\Aria.exe
   ```
2. `AUDIO_VERIFICATION_QUEUE.md`의 항목 1 (Hello Audio) 청취 검증
3. 청취 통과 시 → `AUDIO_VERIFIED.md`로 archive (없으면 신규 생성)
4. Session 2 본 작업:
   - 멀티 트랙 기반 (TrackController + 채널 수 N개)
   - 추가 신디 (Sawtooth, Square — 신디 코어 추상화)
   - 또는 시퀀서 prototype (마디 단위 노트 입력)
   - 결정은 영준님 선택

### For Codex (다음 인계 시)
- 위 "환각 가능성" 1~3번 우선 검증.
- 빌드 실패 시 에러 메시지 분석 + 정확한 JUCE 8.0.12 API 시그니처 확인 (`External/JUCE/modules/` 헤더 직접 grep).
- 청취 검증은 절대 시도하지 말 것 (Codex도 소리 못 들음).

### For Next Session
- 이번 세션 빌드 성공 시: 채널/트랙 추가, 멀티 보이스 폴리포니 강화
- 이번 세션 빌드 실패 시: 에러 정정부터 + 메모리에 "JUCE 8 환각 패턴" feedback 추가 고려

---

## Last commit
- `cfc353a` (2026-05-19) — feat: Aria 프로젝트 초기 스캐폴드 (JUCE 8.0.12 + CMake)
- GitHub: https://github.com/cho1124/Aria (private)
- Branch: `main` (tracking origin/main)

## 다음 세션 시작 시
**[집] 환경 준비**:
```powershell
# 처음 한 번만
git clone --recurse-submodules https://github.com/cho1124/Aria.git
cd Aria
# VS 2022 Community + "Desktop development with C++" 워크로드 필요
cmake -B build -G "Visual Studio 17 2022" -A x64
cmake --build build --config Debug
.\build\Aria_artefacts\Debug\Aria.exe
```

**[회사] 다음 세션 진입 체크리스트**:
1. C++ 워크로드 설치 완료 여부 확인 (영준님)
2. `cmake -B build -G "Visual Studio 17 2022" -A x64` 실행
3. configure 성공 시 → 빌드 시도
4. 빌드 에러 발생 시 → 위 "환각 가능성" 1~3번 우선 의심 → Codex 검증
