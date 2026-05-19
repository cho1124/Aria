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
- [ ] cmake configure 성공
- [ ] Debug 빌드 컴파일 성공
- [ ] 첫 커밋
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

### Known Issues / 의심점

#### 환각 가능성 (우선순위 ↑)
1. **JUCE 8 Font API**: `juce::Font(juce::FontOptions(20.0f, juce::Font::bold))` — JUCE 8에서 FontOptions로 바뀐 것은 맞지만 정확한 시그니처 미검증. 컴파일 에러 시 1순위 의심.
2. **`juce_generate_juce_header(Aria)`**: 명령 이름 정확성. JUCE 8 CMake API에서 이 함수가 존재하는지.
3. **`ProjectInfo::projectName`**: `juce_generate_juce_header`가 생성하는 매크로/구조체 이름.

#### 환경 노이즈 (무시 가능)
- PowerShell 5.1에서 `git submodule add`가 NativeCommandError 던졌지만 실제 동작은 정상 (CLAUDE.md 가이드라인 참고).
- JUCE 8.0.12 Projucer 기본 익스포터가 VS 2026이지만, CMake에서는 `-G "Visual Studio 17 2022"`로 명시하므로 무관.

### Next Steps (순서)
1. `cmake -B build -G "Visual Studio 17 2022" -A x64` 실행
2. configure 성공 시 → `cmake --build build --config Debug`
3. **configure or 빌드 실패 시**:
   - 에러 메시지 → Codex 환각 검증
   - Web Verify로 JUCE 8 정확한 API 재확인
   - 정정 후 재시도
4. 빌드 성공 시 → 첫 커밋 (`feat: initial JUCE 8 setup with sine synth Hello Audio`)
5. (영준님이 GitHub 리모트 결정 시) → push
6. `AUDIO_VERIFICATION_QUEUE.md`에 commit hash 기록

### For Codex (다음 인계 시)
- 위 "환각 가능성" 1~3번 우선 검증.
- 빌드 실패 시 에러 메시지 분석 + 정확한 JUCE 8.0.12 API 시그니처 확인 (`External/JUCE/modules/` 헤더 직접 grep).
- 청취 검증은 절대 시도하지 말 것 (Codex도 소리 못 들음).

### For Next Session
- 이번 세션 빌드 성공 시: 채널/트랙 추가, 멀티 보이스 폴리포니 강화
- 이번 세션 빌드 실패 시: 에러 정정부터 + 메모리에 "JUCE 8 환각 패턴" feedback 추가 고려

---

## Last commit
TBD (첫 커밋 후 갱신)
