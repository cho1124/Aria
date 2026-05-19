# Gemini Verification - Session 1

> Layer 2 (Gemini Review) of validation stack. Independent pass by Gemini 3 Pro.

**Reviewer**: Gemini 3 Pro (via Gemini CLI)
**Date**: 2026-05-19
**Target commits**: cfc353a (scaffold) / 4909cbe (chore) / 78f794f (ci)

## Summary
- **Verdict**: CONCERNS (조건부 통과 - 오디오 스레드 내 메모리 할당 이슈 수정 권장)
- **Build**: 통과 (Aria.exe 24.54MB, MSVC 19.44)
- **Audio thread safety**: 오디오 콜백(`getNextAudioBlock`) 스레드 내부에서 힙 할당(Heap Allocation)을 유발할 수 있는 구조적 문제를 발견했습니다. 실시간(Real-time) 제약 조건을 엄격히 준수하기 위해 개선이 필요합니다.
- **JUCE 8 API**: 성공적. 기존 JUCE 버전의 `juce::Font` 생성자가 Deprecated된 점을 정확히 인지하고 JUCE 8의 `juce::FontOptions`를 도입하는 등 최신 API를 완벽하게 사용하고 있습니다.
- **C++ correctness**: 우수함. `std::make_unique`를 통한 RAII 패턴 적용 및 `setContentOwned`, `addVoice` 등에 대한 소유권(Ownership) 이전이 정확하게 처리되어 메모리 누수 위험이 없습니다.

## Findings

### Critical (must fix before audio verification)
- 없음 (현재 스캐폴드 수준에서는 오디오가 출력될 것이나, DAW로서의 안정성을 위해 아래의 Concern 항목을 수정할 것을 강력히 권장합니다.)

### Concerns (consider before Session 2)
- **[src/MainComponent.cpp:34]** 오디오 스레드 내 힙 메모리 할당: `getNextAudioBlock` 함수 내부에 `juce::MidiBuffer incomingMidi;`가 지역 변수로 선언되어 있습니다. `keyboardState.processNextMidiBuffer`가 호출되어 MIDI 이벤트가 추가될 경우 내부적으로 동적 메모리 할당(Allocation)이 발생할 수 있습니다. 이는 실시간 오디오 스레드에서 오디오 드롭아웃(Dropout)을 유발할 수 있는 가장 대표적인 원인입니다.
- **[src/SineSynth.cpp:24]** 실시간 오디오 콜백 중 무거운 연산: `adsr.setSampleRate()`가 오디오 스레드 상에서 실행되는 `startNote()` 내부에 위치하고 있습니다. 노트가 발생할 때마다 ADSR 계수를 재계산하는 것은 비효율적이며 Lock-free 설계에 불리합니다. 샘플 레이트가 변경될 때만 호출되도록 해야 합니다.

### Observations (informational)
- **[src/SineSynth.cpp:49]** `std::sin` 함수 사용: 스캐폴드용으로는 동작하지만, 실제 DAW 개발에서는 CPU 사이클을 과도하게 소모합니다. 
- **[src/SineSynth.cpp:55]** Phase Wrap-around 누락: `currentAngle`이 수학적 주기인 $2\pi$를 초과할 때 $0$으로 순환시키는 위상 제한 로직이 없습니다. `double` 타입의 정밀도 한계에 도달하기까진 매우 긴 시간이 걸려 당장 문제는 없으나, 모범 사례(Best Practice) 측면에서 추가하는 것이 좋습니다.

## Recommendations for Session 2
1. **MidiBuffer 멤버 변수화**: `MainComponent.h`에 `juce::MidiBuffer incomingMidi;`를 클래스 멤버 변수로 이동시키고, `getNextAudioBlock` 내부에서는 `incomingMidi.clear()`를 통해 사전에 할당된 메모리를 재사용하는 구조로 변경하여 오디오 스레드 힙 할당을 제거하십시오.
2. **ADSR 샘플 레이트 초기화 최적화**: `SineVoice` 클래스에서 `juce::SynthesiserVoice::setCurrentPlaybackSampleRate(double newRate)` 가상 함수를 오버라이드하고, 해당 함수 내에서 `adsr.setSampleRate(newRate)`를 호출하도록 설계 원칙을 개선하십시오.
3. **Phase 순환 적용**: `currentAngle += angleDelta;` 연산 직후 `if (currentAngle >= juce::MathConstants<double>::twoPi) currentAngle -= juce::MathConstants<double>::twoPi;` 코드를 추가해 위상이 발산하는 것을 막으십시오.
4. **JUCE DSP 모듈로의 마이그레이션 준비**: 다음 세션에서 신디사이저가 확장될 때, 기본 `std::sin` 대신 `juce::dsp::Oscillator`나 룩업 테이블(Wavetable) 기반의 고속 오실레이터로 교체할 것을 고려하십시오.

## Methodology
- **정적 코드 및 라이프사이클 분석 (Static Analysis & Lifecycle Review)**: JUCE의 실시간 오디오 처리 엄격 규칙(Real-time audio strict rules)을 기준으로 `getNextAudioBlock`과 직간접적으로 연결된 함수들의 콜 스택을 추적하여 Lock-free, Allocation-free 원칙 준수 여부를 검토했습니다. 또한 JUCE 8 API 문서의 Breaking Changes를 참조하여 최신 컨벤션 적용 여부를 확인하고, 동적 할당 객체들의 RAII 생명주기를 분석하여 Memory Leak 가능성을 배제했습니다.