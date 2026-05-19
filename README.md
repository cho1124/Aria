# Aria

AI-assisted DAW (Digital Audio Workstation).

음악 용어 *Aria* = 솔로 보컬 멜로디. 솔리스트로서의 AI가 작곡을 보조한다는 의미를 담음.

## 스택

- **언어**: C++17
- **프레임워크**: JUCE 8.0.12 (서브모듈 `External/JUCE`)
- **빌드**: CMake 3.22+ / Visual Studio 2022 (Windows)
- **AI** (예정): ONNX Runtime (MIDI 생성) + Python 마이크로서비스 (오디오 생성)

## 빠른 시작

```powershell
git clone --recurse-submodules <repo-url> Aria
cd Aria
cmake -B build -G "Visual Studio 17 2022" -A x64
cmake --build build --config Debug
.\build\Aria_artefacts\Debug\Aria.exe
```

## 워크플로우 주의사항

- 회사에서는 **컴파일/정적 검증/git push**까지만.
- 오디오 청취 검증은 집에서 → `AUDIO_VERIFICATION_QUEUE.md` 참고.
- 환각 방지를 위해 [Codex 협업 + 적대적 검증](HANDOFF.md) 적용.

## 현재 상태

**Session 1 (2026-05-19)**: 환경 세팅 + Hello Audio (사인파 신디 + 가상 키보드).
다음 단계는 `HANDOFF.md` 참고.

## 라이선스

JUCE GPL을 따름 (상용 의도 없음, 학습/포트폴리오 목적).
