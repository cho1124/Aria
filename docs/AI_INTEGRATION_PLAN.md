# AI 통합 정식 플랜 (Aria)

> Phase 3 적대적 검증 (`AI_INTEGRATION_VERIFICATION.md`)의 Arbiter 권고를 영준님이 전면 수용함에 따라 작성된 정식 플랜.
> 이전 draft (`AI_INTEGRATION_PROPOSAL_DRAFT.md`)는 검증 후 폐기됨 (역사 보존용으로 docs/ 유지).

**Date**: 2026-05-19
**Status**: APPROVED (영준님 결정)
**Supersedes**: `AI_INTEGRATION_PROPOSAL_DRAFT.md` (Claude 초안)

---

## 최종 결정 사항

### 아키텍처

**LLM Copilot + 외부 IPC/API** 패러다임.

```
[JUCE C++ DAW] ←──IPC──→ [LLM Service]
    ↑                         ↓
    │                  ┌──────┴──────┐
    │                  │             │
    │             llama.cpp     OpenAI/Anthropic API
    │             (로컬, 무료)    (클라우드, 유료)
    │                  │             │
    │                  └──────┬──────┘
    │                         ↓
    │             자연어 → Aria DSL → MIDI/오토메이션
    │                         ↓
    └─────────── MIDI 클립 + 트랙 설정 적용
```

### 핵심 원칙

1. **C++ 단일 프로세스 집착 폐기** — AI 추론은 외부 프로세스/서비스에 격리
2. **2026 트렌드 부합** — LLM 자연어 인터페이스가 MIDI 멜로디 생성보다 차별적
3. **MIDI 모델 ONNX 변환 회피** — Magenta RNN/LSTM의 ONNX 변환 위험성(C-01) 우회

### 타이밍

- **Session 2~M11**: DAW 코어 구축 (시퀀서, 피아노 롤, 트랙 라우팅, 플러그인 호스팅)
- **M12+**: AI 통합 시작 (코어 안정화 후)
- ❌ ~~M9~M10~~ — Arbiter가 물리적 불가능으로 판정 (C-04)

### 백엔드 선택 (M12 진입 시점에 최종 결정)

| 백엔드 | 장점 | 단점 |
|---|---|---|
| **llama.cpp (로컬)** | 무료, 오프라인, 모델 통제 | 가벼운 모델은 DSL 따라 잡기 어려울 수 있음 |
| **OpenAI/Anthropic API** | 강력한 자연어 이해, DSL 생성 정확도 ↑ | 월 비용, 네트워크 의존 |
| **하이브리드** | 로컬 우선, 복잡할 때만 클라우드 | 구현 복잡 |

→ M11쯤 PoC로 결정. 지금은 "외부 IPC로 분리한다"만 확정.

---

## Aria DSL 설계 (미래 작업, M11~M12)

LLM이 출력할 DSL의 대략적 형태 (확정 아님, 영감용):

```
# 자연어 입력 예시
"잔잔한 피아노 솔로 8마디, C major, 90BPM, 4/4"

# LLM 출력 DSL 예시
SET TEMPO 90
SET TIME_SIGNATURE 4/4
SET KEY C_MAJOR
TRACK piano:
  CLIP bars=8:
    NOTE C4 beat=0 duration=2 velocity=80
    NOTE E4 beat=2 duration=2 velocity=75
    ...

# DSL 파서 (C++) → 내부 MIDI/오토메이션 데이터 구조
```

장점:
- LLM이 텍스트 → DSL이 자연스러움 (코드 생성 task)
- DSL → MIDI 변환은 결정적(deterministic) C++ 코드
- 사용자가 DSL을 직접 편집 가능 (협업 가치 유지)

---

## (선택) M3~M8 단계 PoC

**조건부 권고** (영준님 시간 여유 있을 때):

DAW 코어 작업 중 1주 정도 짬을 내어 **AI 부분만 분리 PoC**:

```python
# poc_llm_to_midi.py (Python 스크립트, Aria와 무관)
import openai  # or local llama.cpp
import mido

prompt = input("음악 설명을 입력하세요: ")
dsl = openai.chat.completions.create(...).choices[0].message.content
# DSL을 MIDI 파일로 변환
mid = parse_dsl_to_midi(dsl)
mid.save("output.mid")
```

목적:
- LLM이 실제로 좋은 DSL을 만드는지 확인
- 토큰 비용/지연 시간 측정
- DSL 문법 시안 검증

이 단계가 잘 되면 M12 진입 시점에 통합이 매끄러움.

---

## 폐기된 옵션 (참고용)

| 옵션 | 폐기 이유 (Verification 참조) |
|---|---|
| 옵션 A (ONNX + JUCE 단일 프로세스) | C-01 ONNX 변환 SPOF, C-02 단일 프로세스 ≠ 단순 |
| 옵션 B (MusicGen/Stable Audio Python) | C-03 LLM Copilot이 더 차별적, 음악 모델 자체는 후순위 |
| 옵션 C (하이브리드 A→B) | 옵션 A 자체가 위험하므로 하이브리드도 무의미 |

---

## 다음 액션 (Session 2 시작 시)

1. ❌ AI 통합 작업 시작하지 말 것 — M12+ 까지 동결
2. ✅ DAW 코어 (시퀀서/피아노 롤/트랙) 구축에 전념
3. (선택) 영준님 짬 날 때 Python PoC 진행 — Aria 리포 외부 또는 `experiments/` 폴더

---

## 관련 문서

- `AI_INTEGRATION_VERIFICATION.md` — 적대적 검증 라운드 1 전문
- `AI_INTEGRATION_PROPOSAL_DRAFT.md` — Claude 초안 (검증으로 폐기됨, 역사 보존)
- 메모리: [[project_aria]] [[project_adversarial_triad]] [[feedback_layer2_codex_vs_gemini]]
