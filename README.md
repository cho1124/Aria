# Aria — AI-assisted DAW

[![Build](https://github.com/cho1124/Aria/actions/workflows/build.yml/badge.svg)](https://github.com/cho1124/Aria/actions/workflows/build.yml)
[![License](https://img.shields.io/badge/license-GPL--3.0-blue)](LICENSE)
[![JUCE](https://img.shields.io/badge/JUCE-8.0.12-orange)](https://juce.com)
[![CMake](https://img.shields.io/badge/CMake-3.22%2B-064F8C)](https://cmake.org)
[![C++](https://img.shields.io/badge/C%2B%2B-17-00599C)](https://en.cppreference.com/w/cpp/17)

> **Aria** *(이탈리아어, 오페라의 솔로 보컬 멜로디)* — AI가 작곡의 솔리스트로 작동하는 DAW.
> FL Studio / Ableton 류 DAW를 AI 작곡 보조 기능과 함께 처음부터 구현하는 학습 / 포트폴리오 프로젝트.

---

## 프로젝트 정체성

다른 AI 음악 도구(Suno, Udio)는 **텍스트 → 완성된 오디오**를 만든다. Aria는 다르다:

- **편집 가능한 출력**: AI는 오디오가 아니라 **MIDI 또는 DSL**을 만든다 → 사용자가 다듬을 수 있다
- **협업 가치**: AI = 솔리스트, 사용자 = 작곡가/지휘자
- **DAW에 내장된 흐름**: 클라우드 API 호출이 아니라 워크플로우의 일부

이 정체성은 [Layer 3 적대적 검증](docs/AI_INTEGRATION_VERIFICATION.md)을 통해 검증된 결과다.

## 현재 상태

<!-- AUTO:STATUS:START -->
*아래 표는 [HANDOFF.md](HANDOFF.md) frontmatter에서 자동 동기화됩니다 (push 시 GitHub Actions).*

| 항목 | 값 |
|------|------|
| 현재 세션 | Session 1 |
| 세션 포커스 | 환경 세팅 + Layer 2 검증 + Layer 3 검증 |
| 세션 상태 | ✅ completed |
| 마지막 세션 날짜 | 2026-05-19 |
| 마지막 commit | [`acc8ed8`](https://github.com/cho1124/Aria/commit/acc8ed8) |
| 빌드 (로컬) | ✅ passed |
| CI | ✅ passed |
| 청취 검증 | ⏳ pending |
| 다음 액션 | 집에서 실행 + 청취 검증 (AUDIO_VERIFICATION_QUEUE 참조) |
<!-- AUTO:STATUS:END -->

다음 세션 시작점은 [HANDOFF.md](HANDOFF.md)를 먼저 읽으면 된다.

## 기술 스택

| 영역 | 선택 | 근거 |
|------|------|------|
| 언어 | C++17 | JUCE 표준, 실시간 오디오 |
| 프레임워크 | JUCE 8.0.12 (submodule) | Direct2D, WebView, 가장 성숙한 오디오 프레임워크 |
| 빌드 | CMake 3.22+ | Projucer 대신 — 서드파티 통합 용이, CI 친화적 |
| 컴파일러 | MSVC 19.44 (VS 2022) | Windows 우선, macOS는 추후 |
| AI 백엔드 (계획) | llama.cpp 또는 OpenAI/Anthropic API | M11에 최종 결정. [PLAN.md](docs/AI_INTEGRATION_PLAN.md) 참조 |

## 빠른 시작

### 요구 사항

- Windows 10/11 + Visual Studio 2022 (**Desktop development with C++ 워크로드 필수**)
- Git (with LFS 없음 OK)

### 빌드

```powershell
git clone --recurse-submodules https://github.com/cho1124/Aria.git
cd Aria

# CMake 경로 (VS 번들 기준)
$CMAKE = "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"

# Configure + Build
& $CMAKE -B build -G "Visual Studio 17 2022" -A x64
& $CMAKE --build build --config Debug

# Run
.\build\Aria_artefacts\Debug\Aria.exe
```

CMake가 PATH에 있으면 그냥 `cmake`로 호출 가능. CI에서는 자동 PATH.

### CI 아티팩트로 받기

직접 빌드하지 않고 [Actions 페이지](https://github.com/cho1124/Aria/actions/workflows/build.yml)의 최신 성공 run에서 `Aria-Debug-Windows-x64` 아티팩트 다운로드 가능 (7일 보관).

## 환각 방지 4계층 (Validation Stack)

이 프로젝트는 [adversarial verification 시스템](https://github.com/cho1124/multi-agent-adversarial-verification)을 적극 활용한다.

```
┌─ L4: Build Gate ──────────────────────────┐  매 커밋 단위
│  로컬 컴파일 + CI 자동 빌드 + 청취 검증    │
├─ L3: Adversarial Triad ──────────────────┤  설계 갈림길
│  Executor / Challenger / Arbiter 3 모델   │
├─ L2: Independent Code Review (Gemini) ───┤  코드 단위
│  외부 LLM의 정적 검토 + VERIFICATION.md   │
├─ L1: Web Verify ─────────────────────────┤  API 의심 시
│  최신 문서로 환각 의심점 cross-check      │
└──────────────────────────────────────────┘
```

### Layer별 가동 실적 (Session 1)

| Layer | 실적 | 가치 |
|---|---|---|
| L1 | ✅ JUCE 8.0.12 + CMake API 사전 확인 | 표준 |
| L2 | ✅ Gemini 3 Pro로 3건 발견 (MidiBuffer 힙 할당 등) → 전건 수정 | **본전 입증** — 청취 시 진짜 dropout 유발할 결함 |
| L3 | ✅ AI 통합 아키텍처 검증 → Claude 추천 전건 패배 + 새 패러다임 채택 | **두 번째 본전** — 프로젝트 방향 전환 |
| L4 | ✅ 로컬 + CI 자동 빌드 | 표준 |

검증 사례 등록: [multi-agent-adversarial-verification/docs/experiments/2026-05-19-Aria-DAW-AI-통합-아키텍처-검증/](https://github.com/cho1124/multi-agent-adversarial-verification/tree/master/docs/experiments/2026-05-19-Aria-DAW-AI-%ED%86%B5%ED%95%A9-%EC%95%84%ED%82%A4%ED%85%8D%EC%B2%98-%EA%B2%80%EC%A6%9D)

## 로드맵

| 기간 | 목표 | 산출물 |
|---|---|---|
| ✅ Session 1 | 환경 세팅 + Hello Audio | 사인 폴리신디 + 가상 키보드 |
| Session 2~3 | 추가 신디 + 신디 코어 추상화 | Sawtooth/Square, IOscillatorVoice |
| Session 4~5 | 미디 시퀀서 기초 | MIDI 클립 데이터 구조 + 재생 |
| Session 6~7 | 피아노 롤 UI | 노트 입력/편집/줌/스크롤 |
| Session 8~9 | 트랙 / 믹서 / 라우팅 | 멀티 트랙 + 채널 스트립 |
| Session 10~11 | 플러그인 호스팅 | VST3 로드 + 파라미터 자동화 |
| **Session 12+** | **AI Copilot 통합** | 자연어 → Aria DSL → MIDI 렌더링. 외부 IPC로 LLM 분리 |

⚠️ AI 통합은 원래 M9~M10이었으나 [Layer 3 적대적 검증](docs/AI_INTEGRATION_VERIFICATION.md) C-04에서 일정 비현실성 판정 → **M12+ 로 연기**.

## 문서

| 파일 | 내용 |
|------|------|
| [HANDOFF.md](HANDOFF.md) | 세션 핸드오프 — 새 세션 시작 시 첫 번째로 읽기 |
| [AUDIO_VERIFICATION_QUEUE.md](AUDIO_VERIFICATION_QUEUE.md) | 청취 검증 대기 큐 (집에서만 가능) |
| [VERIFICATION.md](VERIFICATION.md) | Gemini Layer 2 정적 검토 결과 (Session 1) |
| [docs/AI_INTEGRATION_PLAN.md](docs/AI_INTEGRATION_PLAN.md) | AI 통합 정식 플랜 (LLM Copilot + M12+) |
| [docs/AI_INTEGRATION_VERIFICATION.md](docs/AI_INTEGRATION_VERIFICATION.md) | Layer 3 적대적 검증 전문 |
| [docs/AI_INTEGRATION_PROPOSAL_DRAFT.md](docs/AI_INTEGRATION_PROPOSAL_DRAFT.md) | (폐기됨, 역사 보존) Claude 초안 |

## 워크플로우 특이사항

- **회사 PC**: 컴파일 + 정적 검증 + git push 까지만 (오디오 출력 환경 아님)
- **집 PC**: 실행 + 청취 + 회귀 테스트
- **AI 협업**: 이 프로젝트는 **Claude (Opus 4.7) 가 주도, 사용자가 검증**하는 바이브 코딩 패턴. AI의 환각은 Validation Stack 4계층으로 막는다.

## 라이선스

- 프로젝트 자체: GPL-3.0 (JUCE 라이선스 의존)
- 상용 의도 없음 (학습 / 포트폴리오 목적)
- JUCE 상용 라이선스는 별도 — 이 리포는 GPL 경로만 지원

## 참고 자료

- [JUCE 공식](https://juce.com/learn/documentation/) - 프레임워크
- [JUCE CMake API](https://github.com/juce-framework/JUCE/blob/master/docs/CMake%20API.md)
- [Adversarial Verification System](https://github.com/cho1124/multi-agent-adversarial-verification) - Validation Stack의 Layer 3 시스템
- [Aria 검증 사례](https://github.com/cho1124/multi-agent-adversarial-verification/tree/master/docs/experiments/2026-05-19-Aria-DAW-AI-%ED%86%B5%ED%95%A9-%EC%95%84%ED%82%A4%ED%85%8D%EC%B2%98-%EA%B2%80%EC%A6%9D)
