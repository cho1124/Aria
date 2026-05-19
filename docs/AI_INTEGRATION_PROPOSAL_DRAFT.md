# AI 통합 아키텍처 - Draft Proposal (Phase 2)

> Phase 3 적대적 검증의 입력 문서. 검증 후 `AI_INTEGRATION_PLAN.md`로 정식화.

**Date**: 2026-05-19
**Author**: Claude Opus 4.7 (with Phase 1 web research)
**Status**: DRAFT — pending adversarial verification

---

## 컨텍스트

- **프로젝트**: Aria — AI 보조 DAW (C++/JUCE 8 / CMake)
- **현재 상태**: Session 1 완료 (사인 신디 + 가상 키보드 Hello Audio)
- **AI 통합 목표 시점**: M9~M10 (Session 9~10) — 약 8~10주 후
- **제약**:
  - 학습/포트폴리오 목적 (상용 의도 없음, JUCE GPL OK)
  - 회사/집 분리 워크플로우 (회사=컴파일, 집=청취)
  - 개인 GPU 자원 한정 (Quest 개발용 PC 정도)
  - 오디오 스레드 lock-free/allocation-free 엄수

## 시장 컨텍스트 (Phase 1 리서치 결과)

| 카테고리 | 상태 (2026 Q2 기준) |
|---|---|
| MIDI 생성 | Magenta RealTime "Atom" active. Magenta Studio (Ableton 플러그인) 참고 가치. ONNX 변환 정보는 추가 검증 필요 |
| 오디오 생성 (self-hosted) | MusicGen 2024 이후 정체. Stable Audio 2.5 상용 위주. 16GB VRAM 진입 장벽 |
| 클라우드 API | Suno Premier $30/mo = Suno Studio DAW 포함 (→ **직접 경쟁작/영감**) |
| ONNX + JUCE | iPlug2OnnxRuntime 예제 검증됨. naming conflict 이슈 알려짐 |
| 직접 비교 대상 | MAGDA (오픈소스 DAW + llama.cpp 통합 AI). 2026년 활발 개발 |

---

## 아키텍처 3안

### 옵션 A: MIDI 중심 (가벼움, ONNX 통합)

```
[JUCE C++ DAW]
      ↓
[ONNX Runtime C++ (정적 라이브러리)]
      ↓
[Magenta-계열 / TinyMusician-style 모델 (CPU/GPU)]
      ↓
[MIDI 출력 → 사용자 편집 가능 → 신디 재생]
```

**기능 예시**:
- "다음 마디를 채워주세요" (Magenta Continue 패턴)
- "이 코드 진행에 드럼 패턴 만들어주세요" (Drumify)
- "두 멜로디 사이를 보간해주세요" (Interpolate)

**장점**:
- 단일 프로세스, 배포 단순
- CPU에서도 작동 가능 (모델 크기에 따라)
- 출력이 MIDI → **사용자가 편집 가능 = 협업 가치**
- ONNX + JUCE 검증된 패턴 (iPlug2 예제)
- JUCE GPL과 호환 (Magenta Apache 2.0)

**단점**:
- 멋진 한 곡 자동 생성 불가
- Magenta → ONNX 변환 자체 검증 필요 (불확실성)
- 음색은 우리 신디에 의존 (모델이 음색을 생성 안 함)

**진입 복잡도**: ⭐⭐ (중)
**운영 부담**: ⭐ (낮음)
**학습 가치**: ⭐⭐⭐⭐ (높음 - 실시간 inference + DSP 통합)

---

### 옵션 B: 오디오 생성 (Python 마이크로서비스)

```
[JUCE C++ DAW]
      ↕ gRPC/WebSocket (로컬 IPC)
[Python Service]
      ↓
[MusicGen / Stable Audio (GPU)]
      ↓
[WAV/FLAC → DAW로 전송 → 트랙에 배치]
```

**기능 예시**:
- "차분한 피아노 솔로 30초 만들어주세요"
- "이 멜로디 위에 스트링 반주 깔아주세요"
- "이 트랙에서 보컬만 추출해서 다른 트랙으로 분리해주세요" (stem split)

**장점**:
- 풍부한 표현 (음색 포함)
- Python AI 생태계 그대로 활용
- 모델 교체 쉬움 (다음 모델 나오면 service만 바꾸면 됨)

**단점**:
- 2-프로세스 운영 복잡도 (배포, 디버깅)
- 16GB+ VRAM 필요 (영준님 환경 검증 필요)
- 실시간 생성 불가 (3~10초 단위 비동기)
- 결과물 편집 어려움 (오디오니까)

**진입 복잡도**: ⭐⭐⭐⭐ (높음 - IPC + 모델 호스팅)
**운영 부담**: ⭐⭐⭐⭐ (높음 - 두 프로세스 + GPU)
**학습 가치**: ⭐⭐⭐ (중간 - IPC 패턴은 흥미롭지만 코어는 Python 작업)

---

### 옵션 C: 하이브리드 (A 먼저, B는 나중)

- Session 9~10: 옵션 A 구현 (MIDI 중심)
- Session 11~12+: 옵션 B 추가 (필요/원하면)
- 두 시스템은 독립 작동, 사용자가 선택

**장점**: 점진적 확장, 위험 분산
**단점**: 일정 ↑, 모듈 경계 설계 추가 필요

---

### 옵션 D (참고): 클라우드 API (Suno 3rd party)

**탈락 이유**:
- Suno 공식 API 없음 → 3rd party 의존 = 비공식
- 학습 가치 낮음 (HTTP 요청만)
- Suno Studio 자체와 직접 경쟁 = Aria 정체성 약화
- 상용 의도 없는 학습 프로젝트에 월 $30 부담 불필요

---

## 추천 (검증 대상)

**옵션 A 단독 시작, 옵션 C로 확장 여지 열어둠**.

근거:
1. **학습 가치 최대화**: ONNX C++ inference, 실시간 신경망 추론, JUCE 통합 = DAW + AI 둘 다 깊이 학습
2. **포트폴리오 차별성**: Suno류는 텍스트→오디오, Aria는 **편집 가능한 MIDI 생성** = 협업 가치 강조
3. **운영 단순성**: 단일 프로세스, GPU 의존 최소화 (영준님 환경 친화적)
4. **점진적 확장 가능**: A가 안정화되면 B를 모듈로 추가

## 검증 필요 항목 (Phase 3 적대적 검증 목표)

1. **A 옵션 선택의 정당성** — 정말 옵션 B나 C가 더 가치 큰 거 아닌가?
2. **Magenta → ONNX 변환 실현성** — 정보 부족 영역. 안 되면 옵션 A 자체 무너짐
3. **모델 후보 우선순위** — Magenta RealTime "Atom" vs TinyMusician 스타일 자체 학습 vs 기존 melody_rnn ONNX 변환
4. **MAGDA와의 차별점** — 이미 비슷한 게 있는데 Aria가 의미 있나? (정체성 질문)
5. **타이밍** — M9~M10이 적절한가? 더 일찍? 더 늦게?

---

## 메모

- Phase 1 출처는 메인 결산 응답에 포함됨 (Sources 섹션)
- 이 문서는 Phase 3 적대적 검증의 입력. 검증 후 `AI_INTEGRATION_PLAN.md`로 정식화
