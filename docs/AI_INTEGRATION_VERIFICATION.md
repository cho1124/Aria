# AI 통합 아키텍처 - Adversarial Verification

> 환각 방지 4계층 중 **Layer 3 (Adversarial Triad)** 가동 결과.
> Aria 프로젝트 첫 적대적 검증 — Claude 초안 추천이 패배하고 방향이 전환됨.

**Date**: 2026-05-19
**Round**: 1 (단일 라운드, 시간 제약으로 압축 진행)
**Subject**: Aria DAW의 AI 통합 아키텍처 결정 (M9~M10 시점 가정)
**Input doc**: `AI_INTEGRATION_PROPOSAL_DRAFT.md`

## 참여 모델

| 역할 | 모델 | 비고 |
|---|---|---|
| Executor | Claude Opus 4.7 (메인 세션) | 옵션 A 단독 시작 추천 |
| Challenger | Gemini 3 Pro (yolo, Bash 직접 호출) | 4개 모순 high/medium 제기 |
| Arbiter | Gemini 3 Pro (별도 호출, fresh context) | 4개 모두 VALID 판정 |

**한계**: Challenger와 Arbiter가 동일 모델(Gemini 3 Pro). 진정한 독립성은 약함. Codex 서브에이전트 sandbox 제약으로 회피 ([[feedback_layer2_codex_vs_gemini]]).

---

## Executor 제안 (Claude)

- **옵션 A 단독 시작** (MIDI 중심 / ONNX Runtime + JUCE 단일 프로세스 / Magenta-계열)
- 옵션 C (하이브리드)로 확장 여지
- 근거: 학습 가치 최대화, 포트폴리오 차별성(편집 가능 MIDI), 운영 단순성, 점진적 확장

## Challenger 반박 (Gemini)

| ID | Severity | Type | 핵심 공격 |
|---|---|---|---|
| **C-01** | High | ecosystem_outdated + assumption_flaw | Magenta RealTime 'Atom' active 상태 의심. RNN/LSTM의 ONNX 변환은 state 유지 + custom op 부재로 변환 에러 빈발. SPOF |
| **C-02** | High | logic_error | 단일 프로세스 ≠ 단순. lock-free 오디오 콜백 + ONNX 추론(필연 alloc/blocking) = 어차피 백그라운드 워커 + Lock-free Ring Buffer 직접 구현 필요. Python IPC보다 어려움 |
| **C-03** | Medium | frame_shift | MAGDA가 이미 자연어→DSL→MIDI 제어 LLM 에이전트 방식으로 한 발 앞서있음. 단순 'MIDI 생성'은 시대 뒤떨어진 접근 |
| **C-04** | High | assumption_flaw | M9~M10 물리적 불가능. 사인파→8세션 만에 DAW 뼈대(시퀀서/피아노 롤/라우팅) + ONNX 포팅 + 비동기 추론 = 불가능 |

**Challenger 권고**:
1. 옵션 B (Python 마이크로서비스)로 선회
2. **패러다임 전환**: 'AI 음악 생성' → **'LLM Copilot 에이전트'** (llama.cpp + 자연어 DSL → MIDI 클립 렌더링)
3. AI 통합 M12+ 로 연기. 옵션 A 강행 시 1주일 내 PoC 의무화

## Arbiter 판정 (Gemini, fresh context)

### 모순별 Verdict

| ID | Verdict | Reason |
|---|---|---|
| C-01 | **VALID** | 구형 RNN/LSTM의 C++ ONNX 변환은 state + custom op 문제로 실패 확률 매우 높음. 옵션 A의 SPOF |
| C-02 | **VALID** | C++ 백그라운드 스레드 + Lock-free 큐로 무거운 추론 통합은 Python IPC보다 난이도 훨씬 높음. '운영 부담 낮음' 명백한 논리 오류 |
| C-03 | **VALID** | 2026 기준 단순 신경망 MIDI 생성은 LLM 자연어 제어 워크플로우 대비 차별성/기술적 참신함 떨어짐 |
| C-04 | **VALID** | 개인 사이드 프로젝트에서 8~9세션 만에 DAW 코어 + 비동기 AI 추론 엔진 완성 = 물리적 불가능 |

### 라운드 상태

- **Challenger**: rational_consensus (논리적 우위로 합의 형성)
- **Executor frame_shift**: **true** — '학습 가치 최대화' 프레임을 사용하여 구형 기술 스택 채택과 ONNX 변환 위험성이라는 객관적 결함을 정당화

### 의존성 체인 분석

**Root Cause**: Executor가 스스로 부여한 **'AI 추론의 단일 C++ 프로세스 내장'** 제약. 이 제약 때문에:
- C++에서 돌아가는 ONNX를 선택해야 했음
- 최신 PyTorch 생태계 대신 구형 Magenta를 끌어와야 했음
- C++ 스레드 관리 복잡성을 과소평가하게 됨

**단일 피벗 포인트**: 이 제약 포기 → 외부 서비스/프로세스(Python IPC 또는 API)로 분리 → **C-01, C-02, C-03 동시 해소**

### 에스컬레이션 (영준님 판단 필요)

1. **AI 패러다임 선택**: 기존 'MIDI 멜로디 생성' vs 'LLM Copilot (자연어 → DSL/MIDI 렌더링)'
2. **아키텍처 수용 여부**: C++ 단일 프로세스 집착 포기 + Python IPC 또는 외부 LLM API(OpenAI/Anthropic) 수용 여부

### 최종 결정 (Arbiter)

- **옵션**: **새 옵션** (Challenger 권고 수용: LLM Copilot 패러다임 + Python IPC/API)
- **일정**: **M12+ 로 연기**
- **이유**:
  1. 옵션 A는 레거시 모델 ONNX 변환 리스크 + C++ 비동기 통합 복잡성으로 좌초 위험 높음
  2. LLM Copilot 방식은 구현 난이도 낮고 2026 트렌드 부합 + 포트폴리오 가치 ↑
  3. DAW 코어 없는 상태에서 AI 얹는 건 모래 위에 집 짓는 격 — 일정 연기 타당

### Actionable Next Steps

1. **DAW 코어 집중** (Session 2~8): 시퀀서, 피아노 롤 UI, 트랙 라우팅 등 뼈대 구축
2. **(선택) LLM Copilot PoC**: Python 스크립트로 '자연어 → LLM API → MIDI 파일' 흐름 1주일 내 가볍게 검증 (JUCE 무관)
3. **문서 업데이트**: `AI_INTEGRATION_PLAN.md`에 M12+ 시점 + LLM Copilot 아키텍처 명시

---

## Pending: 영준님 결정 후 `AI_INTEGRATION_PLAN.md` 작성

Arbiter 권고는 영준님 승인 필요 (에스컬레이션 항목). 위 결정 수용 여부 + 어떤 패러다임으로 갈지에 따라 정식 PLAN 문서 작성.

## Validation Stack에서의 의미

| Layer | 결과 |
|---|---|
| L1 Web Verify | ✅ Phase 1 리서치 (불완전 — Magenta active 상태 등에서 Challenger가 더 정확) |
| L3 Adversarial Triad | ✅ **시스템 가동 성공 — Claude 초안 패배 + 더 나은 방향 도출** |
| L2 Codex Review | ✕ (이번 검증엔 미사용) |
| L4 Build Gate | — (코드 변경 없음) |

이 검증의 핵심 가치는 **Claude(Executor)가 자기 frame에 갇혀 있던 걸 Challenger가 깨뜨린 점**. Layer 3가 단순 sanity check를 넘어 실질적인 방향 전환을 만들어냄.
