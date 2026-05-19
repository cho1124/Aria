#include "MainComponent.h"

MainComponent::MainComponent()
    : keyboardComponent(keyboardState, juce::MidiKeyboardComponent::horizontalKeyboard)
{
    titleLabel.setText("Aria - Hello Audio", juce::dontSendNotification);
    titleLabel.setFont(juce::Font(juce::FontOptions(20.0f, juce::Font::bold)));
    titleLabel.setJustificationType(juce::Justification::centredLeft);
    addAndMakeVisible(titleLabel);

    addAndMakeVisible(keyboardComponent);

    for (int i = 0; i < 8; ++i)
        synth.addVoice(new SineVoice());

    synth.addSound(new SineSound());

    setSize(900, 320);
    setAudioChannels(0, 2);
}

MainComponent::~MainComponent()
{
    shutdownAudio();
}

void MainComponent::prepareToPlay(int /*samplesPerBlockExpected*/, double sampleRate)
{
    synth.setCurrentPlaybackSampleRate(sampleRate);
}

void MainComponent::getNextAudioBlock(const juce::AudioSourceChannelInfo& bufferToFill)
{
    bufferToFill.clearActiveBufferRegion();

    incomingMidi.clear();
    keyboardState.processNextMidiBuffer(incomingMidi,
                                        bufferToFill.startSample,
                                        bufferToFill.numSamples,
                                        true);

    synth.renderNextBlock(*bufferToFill.buffer,
                          incomingMidi,
                          bufferToFill.startSample,
                          bufferToFill.numSamples);
}

void MainComponent::releaseResources()
{
}

void MainComponent::paint(juce::Graphics& g)
{
    g.fillAll(getLookAndFeel().findColour(juce::ResizableWindow::backgroundColourId));
}

void MainComponent::resized()
{
    auto area = getLocalBounds().reduced(12);
    titleLabel.setBounds(area.removeFromTop(36));
    area.removeFromTop(8);
    keyboardComponent.setBounds(area);
}
