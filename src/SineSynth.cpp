#include "SineSynth.h"

SineVoice::SineVoice()
{
    adsr.setParameters(adsrParams);
}

bool SineVoice::canPlaySound(juce::SynthesiserSound* sound)
{
    return dynamic_cast<SineSound*>(sound) != nullptr;
}

void SineVoice::setCurrentPlaybackSampleRate(double newRate)
{
    juce::SynthesiserVoice::setCurrentPlaybackSampleRate(newRate);

    if (newRate > 0.0)
        adsr.setSampleRate(newRate);
}

void SineVoice::startNote(int midiNoteNumber,
                          float velocity,
                          juce::SynthesiserSound* /*sound*/,
                          int /*currentPitchWheelPosition*/)
{
    currentAngle = 0.0;
    level = velocity * 0.25f;

    const auto cyclesPerSecond = juce::MidiMessage::getMidiNoteInHertz(midiNoteNumber);
    const auto cyclesPerSample = cyclesPerSecond / getSampleRate();
    angleDelta = cyclesPerSample * juce::MathConstants<double>::twoPi;

    adsr.noteOn();
}

void SineVoice::stopNote(float /*velocity*/, bool allowTailOff)
{
    if (allowTailOff)
    {
        adsr.noteOff();
    }
    else
    {
        clearCurrentNote();
        angleDelta = 0.0;
        adsr.reset();
    }
}

void SineVoice::renderNextBlock(juce::AudioBuffer<float>& outputBuffer,
                                int startSample,
                                int numSamples)
{
    if (angleDelta == 0.0)
        return;

    for (int sample = 0; sample < numSamples; ++sample)
    {
        const auto envelope = adsr.getNextSample();
        const auto currentSample = static_cast<float>(std::sin(currentAngle) * level * envelope);

        for (int channel = 0; channel < outputBuffer.getNumChannels(); ++channel)
            outputBuffer.addSample(channel, startSample + sample, currentSample);

        currentAngle += angleDelta;
        if (currentAngle >= juce::MathConstants<double>::twoPi)
            currentAngle -= juce::MathConstants<double>::twoPi;
    }

    if (! adsr.isActive())
    {
        clearCurrentNote();
        angleDelta = 0.0;
    }
}
