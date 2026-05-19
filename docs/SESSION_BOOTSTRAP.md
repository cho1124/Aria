# Session Bootstrap

> **새 Claude 세션(다른 머신/다른 컨텍스트) 진입 시 첫 번째로 읽기**.
> 이 문서는 로컬 메모리 시스템 없이도 풀 컨텍스트로 진입하기 위한 압축 요약입니다.
> 메모리는 머신별로 로컬 보관되므로(개인 정보 포함), 프로젝트 진행에 필요한 부분만 이 문서로 분리해 commit 됩니다.

## 읽는 순서

1. **이 문서** (Session Bootstrap) — 프로젝트 결정 + 도구 패턴 압축
2. **[HANDOFF.md](../HANDOFF.md)** — 마지막 세션 상태 + 다음 액션
3. **[AUDIO_VERIFICATION_QUEUE.md](../AUDIO_VERIFICATION_QUEUE.md)** — 청취 검증 대기 항목
4. (필요 시) [VERIFICATION.md](../VERIFICATION.md), [AI_INTEGRATION_PLAN.md](AI_INTEGRATION_PLAN.md), [AI_INTEGRATION_VERIFICATION.md](AI_INTEGRATION_VERIFICATION.md)

---

## 프로젝트 핵심 정체성

- **이름**: Aria — *AI Responsive Improvisation Atelier* (이탈리아어 솔로 멜로디 의미와 의도된 이중 의미)
- **목적**: AI 보조 DAW 학습/포트폴리오 (상용 의도 없음, JUCE GPL OK)
- **모드**: 바이브 코딩 — Claude (Opus 4.7) 가 코드 작성 주도, 사용자가 방향 결정 + 청취 검증
- **차별점**: AI가 오디오가 아닌 **편집 가능한 MIDI/DSL** 생성 = 사용자가 다듬을 수 있음. Suno/Udio류 텍스트→오디오와 반대

## 아키텍처 결정 (확정)

- **언어/프레임워크**: C++17 / JUCE 8.0.12 (`External/JUCE` submodule, tag `29396c2`)
- **빌드**: CMake 3.22+ (Projucer 미사용) / VS 2022 Community + C++ Desktop 워크로드 / MSVC 19.44
- **CMake.exe 절대 경로** (PATH 없을 때): `C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe`
- **AI 통합** (M12+): LLM Copilot + Python IPC/API (자연어 → Aria DSL → MIDI). llama.cpp 로컬 또는 OpenAI/Anthropic API. **C++ 단일 프로세스 집착 폐기** (Layer 3 적대적 검증 결과)
- **DAW 엔진** (3~4차 도입 검토): Tracktion Engine (JUCE 기반 오픈소스)

## 환각 방지 4계층 (Validation Stack)

본 프로젝트는 매 결정/코드 단위에서 다음을 가동합니다:

1. **L4 Build Gate** — 매 커밋, 로컬 컴파일 + CI 자동 빌드 + (집에서) 실행/청취
2. **L2 Code Review** — Gemini CLI (yolo, gemini-3-pro-preview) 로 정적 검토. **codex:codex-rescue 서브에이전트는 외부 폴더 접근 불가/임베드 무시 환각**으로 부적합 → Gemini 우선 사용
3. **L3 Adversarial Triad** — 큰 설계 갈림길에서 `/adversarial-verify`. Session 1에서 Claude 초안 (옵션 A: ONNX+JUCE 단일 프로세스) 전건 패배 → LLM Copilot으로 전환
4. **L1 Web Verify** — API 의심 시 WebSearch / WebFetch

## 세션 핸드오프 프로토콜

- **HANDOFF.md** 상단 YAML frontmatter = 상태의 source of truth
- **README.md AUTO:* 마커 영역** = HANDOFF frontmatter 변경 시 GitHub Actions가 자동 sync (`docs(README): auto-sync`)
- 세션 끝낼 때 frontmatter만 갱신하면 됨 (session 번호, last_commit, layer_*_status 등)

## 워크플로우 (오디오 검증 분리)

- **회사 PC**: 코드 + 컴파일 + 정적 검증 + git push 까지
- **집 PC**: 실행 + 청취 + 회귀 테스트
- `AUDIO_VERIFICATION_QUEUE.md`에 PENDING 항목 적치. 통과 시 `AUDIO_VERIFIED.md`로 archive (없으면 신규 생성)

## 도구 함정 (학습된 것 — 다시 시행착오 안 하기)

### GitHub Actions YAML `!` 부정 연산자
- `if: !contains(...)` 같은 `!`로 시작하는 표현은 **quoted/`${{ }}`로도 instant-fail (0초)**. `gh run view --log-failed`도 "log not found".
- 부정 로직은 **다른 조건으로 대체** (예: `github.actor != 'github-actions[bot]'`) 또는 **step-level if로 분리**

### PowerShell 5.1 한국어 round-trip
- `Get-Content + replace + Set-Content` 파이프는 `-Encoding utf8` 명시해도 **한국어 손상 위험** (mojibake)
- 한국어 파일 변형은 **Edit tool 또는 Python script로 처리**. PowerShell stdout도 cmd 인코딩이라 검증 부정확

### PowerShell native 명령 stderr
- `git`, `cmake` 등이 `NativeCommandError` 던지지만 **exit code 0만 신뢰**. 실제 동작은 보통 정상

### CMake.exe PATH 미등록
- VS 2022에 C++ 워크로드 설치해도 cmake가 시스템 PATH에 자동 추가되지 않음. 절대 경로 호출 필요 (위 명시).

## 빌드 & 실행 (집에서 처음 시작 시)

```powershell
git clone --recurse-submodules https://github.com/cho1124/Aria.git
cd Aria

# VS 2022 Community + Desktop development with C++ 워크로드 필수
$CMAKE = "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"

& $CMAKE -B build -G "Visual Studio 17 2022" -A x64
& $CMAKE --build build --config Debug

.\build\Aria_artefacts\Debug\Aria.exe
```

집에서 PATH에 cmake 추가되어 있으면 `cmake`로 그대로 사용 가능.

## 자동화 시스템 사용법

세션 끝낼 때:

1. `HANDOFF.md` frontmatter 갱신 (session 번호, last_commit, session_status 등)
2. `git commit + push`
3. GitHub Actions `Sync README` workflow가 자동으로 README의 `AUTO:STATUS` / `AUTO:VALIDATION` 영역 갱신 (또는 변경 없으면 no-op)
4. bot이 만든 commit은 무한 루프 방지로 skip됨 (actor 체크)

로컬에서 수동 확인:
```powershell
python .github/scripts/sync_readme.py --check  # 변경 필요 여부만
python .github/scripts/sync_readme.py          # 실제 갱신
```

## 외부 참조

- **MAV 리포 Aria 검증 사례**: https://github.com/cho1124/multi-agent-adversarial-verification/tree/master/docs/experiments/2026-05-19-Aria-DAW-AI-%ED%86%B5%ED%95%A9-%EC%95%84%ED%82%A4%ED%85%8D%EC%B2%98-%EA%B2%80%EC%A6%9D
- **JUCE 8 CMake API**: https://github.com/juce-framework/JUCE/blob/master/docs/CMake%20API.md
- **JUCE 공식 튜토리얼**: https://juce.com/learn/tutorials

---

이 문서는 프로젝트 결정 + 도구 패턴 압축본입니다. 영준님 개인 작업 스타일/백그라운드는 머신 로컬 메모리에 보관되며, 본 문서에는 포함하지 않습니다. 새 세션이 모든 패턴을 다시 시행착오로 학습하지 않도록 하는 목적입니다.
